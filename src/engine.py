"""
G*Power Statistical Engine for t2-indep (Two independent means t-test)
Course: YZM301 Software Verification and Testing - Teardown Sprint
Reference: Faul, Erdfelder, Lang & Buchner (2007, 2009); G*Power 3.1.9.7
"""

import math
from typing import Dict, Any, Tuple
import scipy.stats as stats
import scipy.optimize as optimize


class EngineError(Exception):
    def __init__(self, message: str, code: str = "INVALID_VALUE", field: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.field = field


def calc_ncp(d: float, n1: int, n2: int) -> float:
    """Calculate noncentrality parameter delta for two independent groups."""
    return float(d * math.sqrt((n1 * n2) / (n1 + n2)))


def calc_critical_t(tails: int, alpha: float, df: int) -> float:
    """Calculate critical t value under H0."""
    if tails == 1:
        return float(stats.t.ppf(1.0 - alpha, df))
    elif tails == 2:
        return float(stats.t.ppf(1.0 - alpha / 2.0, df))
    else:
        raise EngineError("tails must be 1 or 2", code="OUT_OF_RANGE", field="tails")


def calc_alpha_from_tcrit(tails: int, tcrit: float, df: int) -> float:
    """Calculate type I error alpha from critical t under H0."""
    if tails == 1:
        return float(stats.t.sf(tcrit, df))
    elif tails == 2:
        return float(2.0 * stats.t.sf(tcrit, df))
    else:
        raise EngineError("tails must be 1 or 2", code="OUT_OF_RANGE", field="tails")


def calc_power_from_tcrit(tails: int, tcrit: float, df: int, ncp: float) -> float:
    """Calculate power (1 - beta) under H1 using noncentral t distribution."""
    if tails == 1:
        return float(stats.nct.sf(tcrit, df, ncp))
    elif tails == 2:
        # Two-tailed t-test: power includes rejection in both upper and lower tails
        upper = stats.nct.sf(tcrit, df, ncp)
        lower = stats.nct.cdf(-tcrit, df, ncp)
        return float(upper + lower)
    else:
        raise EngineError("tails must be 1 or 2", code="OUT_OF_RANGE", field="tails")


def calc_beta_from_tcrit(tails: int, tcrit: float, df: int, ncp: float) -> float:
    """Calculate beta (type II error) under H1."""
    pwr = calc_power_from_tcrit(tails, tcrit, df, ncp)
    return float(1.0 - pwr)


def compute_t2_post_hoc(tails: int, d: float, alpha: float, n1: int, n2: int) -> Dict[str, Any]:
    """Post-hoc power analysis: Compute achieved power."""
    df = n1 + n2 - 2
    ncp = calc_ncp(d, n1, n2)
    critical_t = calc_critical_t(tails, alpha, df)
    power = calc_power_from_tcrit(tails, critical_t, df, ncp)
    return {
        "ncp": ncp,
        "critical_t": critical_t,
        "df": df,
        "power": power
    }


def compute_t2_a_priori(tails: int, d: float, alpha: float, power: float, ratio: float) -> Dict[str, Any]:
    """A-priori power analysis: Compute required sample sizes n1, n2 and total N."""
    if power <= alpha:
        raise EngineError("Power must be greater than alpha", code="INCONSISTENT", field="power")

    # Start search from n1 = 2
    # In G*Power, group allocation follows: n2 = ceil(n1 * ratio)
    # Binary search or incremental search with rapid doubling
    # First, bracket the upper bound
    n1_low = 2
    n1_high = 4
    while True:
        n2_high = max(2, math.ceil(n1_high * ratio))
        res = compute_t2_post_hoc(tails, d, alpha, n1_high, n2_high)
        if res["power"] >= power:
            break
        n1_high *= 2
        if n1_high > 10_000_000:
            raise EngineError("No solution found within reasonable sample size", code="NO_SOLUTION")

    # Binary search for the minimal n1
    while n1_low < n1_high:
        mid = (n1_low + n1_high) // 2
        n2_mid = max(2, math.ceil(mid * ratio))
        res = compute_t2_post_hoc(tails, d, alpha, mid, n2_mid)
        if res["power"] >= power:
            n1_high = mid
        else:
            n1_low = mid + 1

    final_n1 = n1_low
    final_n2 = max(2, math.ceil(final_n1 * ratio))
    final_res = compute_t2_post_hoc(tails, d, alpha, final_n1, final_n2)

    return {
        "ncp": final_res["ncp"],
        "critical_t": final_res["critical_t"],
        "df": final_res["df"],
        "n1": final_n1,
        "n2": final_n2,
        "n_total": final_n1 + final_n2,
        "actual_power": final_res["power"]
    }


def compute_t2_compromise(tails: int, d: float, beta_alpha_ratio: float, n1: int, n2: int) -> Dict[str, Any]:
    """Compromise power analysis: Compute implied alpha and power given beta/alpha ratio."""
    df = n1 + n2 - 2
    ncp = calc_ncp(d, n1, n2)

    # Function to find root of: beta(t) - q * alpha(t) = 0
    # As t increases, alpha decreases, beta increases
    def root_func(t_val: float) -> float:
        a = calc_alpha_from_tcrit(tails, t_val, df)
        b = calc_beta_from_tcrit(tails, t_val, df, ncp)
        return b - beta_alpha_ratio * a

    # Bracket search for t_crit
    # When t is very small (e.g. 0.001), beta is ~0, alpha is ~1 -> root_func < 0
    # When t is very large (e.g. 20), beta is ~1, alpha is ~0 -> root_func > 0
    t_min = 1e-4
    t_max = max(20.0, ncp + 10.0)

    try:
        critical_t = optimize.brentq(root_func, t_min, t_max, xtol=1e-12, rtol=1e-12)
    except Exception as e:
        raise EngineError(f"Compromise solver failed: {str(e)}", code="NO_SOLUTION")

    alpha_val = calc_alpha_from_tcrit(tails, critical_t, df)
    beta_val = calc_beta_from_tcrit(tails, critical_t, df, ncp)
    power_val = 1.0 - beta_val

    return {
        "ncp": ncp,
        "critical_t": critical_t,
        "df": df,
        "alpha": alpha_val,
        "beta": beta_val,
        "power": power_val
    }


def compute_t2_criterion(tails: int, d: float, power: float, n1: int, n2: int) -> Dict[str, Any]:
    """Criterion power analysis: Compute required alpha for given power."""
    df = n1 + n2 - 2
    ncp = calc_ncp(d, n1, n2)

    # Find t_crit such that power_from_tcrit(t_crit) = power
    # As t increases, power decreases
    def root_func(t_val: float) -> float:
        return calc_power_from_tcrit(tails, t_val, df, ncp) - power

    t_min = -10.0
    t_max = max(25.0, ncp + 15.0)

    try:
        critical_t = optimize.brentq(root_func, t_min, t_max, xtol=1e-12, rtol=1e-12)
    except Exception as e:
        raise EngineError(f"Criterion solver failed: {str(e)}", code="NO_SOLUTION")

    alpha_val = calc_alpha_from_tcrit(tails, critical_t, df)

    return {
        "ncp": ncp,
        "critical_t": critical_t,
        "df": df,
        "alpha": alpha_val
    }


def compute_t2_sensitivity(tails: int, alpha: float, power: float, n1: int, n2: int) -> Dict[str, Any]:
    """Sensitivity power analysis: Compute detectable effect size d for given power."""
    if power <= alpha:
        raise EngineError("Power must be greater than alpha", code="INCONSISTENT", field="power")

    df = n1 + n2 - 2
    critical_t = calc_critical_t(tails, alpha, df)
    sqrt_factor = math.sqrt((n1 * n2) / (n1 + n2))

    # Find d > 0 such that power_from_tcrit(critical_t, df, d * sqrt_factor) = power
    # As d increases, ncp increases, power increases
    def root_func(d_val: float) -> float:
        ncp_val = d_val * sqrt_factor
        return calc_power_from_tcrit(tails, critical_t, df, ncp_val) - power

    d_min = 1e-6
    d_max = 50.0

    try:
        solved_d = optimize.brentq(root_func, d_min, d_max, xtol=1e-12, rtol=1e-12)
    except Exception as e:
        raise EngineError(f"Sensitivity solver failed: {str(e)}", code="NO_SOLUTION")

    solved_ncp = calc_ncp(solved_d, n1, n2)

    return {
        "ncp": solved_ncp,
        "critical_t": critical_t,
        "df": df,
        "d": solved_d
    }


def run_power_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main dispatch function for power analysis.
    Validates parameters and calls appropriate calculation function.
    """
    test = params.get("test")
    mode = params.get("mode")

    if not test:
        raise EngineError("Missing test parameter", code="MISSING_PARAM", field="test")
    if test != "t2-indep":
        raise EngineError(f"Unsupported test family: '{test}'. This module implements 't2-indep'.", code="UNSUPPORTED", field="test")

    if not mode:
        raise EngineError("Missing mode parameter", code="MISSING_PARAM", field="mode")

    supported_modes = ["a-priori", "post-hoc", "compromise", "criterion", "sensitivity"]
    if mode not in supported_modes:
        raise EngineError(f"Unsupported analysis mode: '{mode}'", code="UNSUPPORTED", field="mode")

    # Common parameters validation
    tails = params.get("tails")
    if tails is None:
        raise EngineError("Parameter 'tails' is required for t-tests", code="MISSING_PARAM", field="tails")
    if tails not in [1, 2]:
        raise EngineError(f"Invalid tails value: {tails}. Must be 1 or 2.", code="OUT_OF_RANGE", field="tails")

    if mode == "a-priori":
        required = ["d", "alpha", "power", "ratio"]
        for p in required:
            if p not in params:
                raise EngineError(f"Missing parameter '{p}' for mode '{mode}'", code="MISSING_PARAM", field=p)
        d = params["d"]
        alpha = params["alpha"]
        power = params["power"]
        ratio = params["ratio"]

        if not (0 < alpha < 1):
            raise EngineError(f"alpha must be between 0 and 1, got {alpha}", code="OUT_OF_RANGE", field="alpha")
        if not (0 < power < 1):
            raise EngineError(f"power must be between 0 and 1, got {power}", code="OUT_OF_RANGE", field="power")
        if d <= 0:
            raise EngineError(f"d must be positive, got {d}", code="OUT_OF_RANGE", field="d")
        if ratio <= 0:
            raise EngineError(f"ratio must be positive, got {ratio}", code="OUT_OF_RANGE", field="ratio")

        return compute_t2_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)

    elif mode == "post-hoc":
        required = ["d", "alpha", "n1", "n2"]
        for p in required:
            if p not in params:
                raise EngineError(f"Missing parameter '{p}' for mode '{mode}'", code="MISSING_PARAM", field=p)
        d = params["d"]
        alpha = params["alpha"]
        n1 = params["n1"]
        n2 = params["n2"]

        if not (0 < alpha < 1):
            raise EngineError(f"alpha must be between 0 and 1, got {alpha}", code="OUT_OF_RANGE", field="alpha")
        if d <= 0:
            raise EngineError(f"d must be positive, got {d}", code="OUT_OF_RANGE", field="d")
        if n1 < 2:
            raise EngineError(f"n1 must be >= 2, got {n1}", code="OUT_OF_RANGE", field="n1")
        if n2 < 2:
            raise EngineError(f"n2 must be >= 2, got {n2}", code="OUT_OF_RANGE", field="n2")

        return compute_t2_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)

    elif mode == "compromise":
        required = ["d", "beta_alpha_ratio", "n1", "n2"]
        for p in required:
            if p not in params:
                raise EngineError(f"Missing parameter '{p}' for mode '{mode}'", code="MISSING_PARAM", field=p)
        d = params["d"]
        beta_alpha_ratio = params["beta_alpha_ratio"]
        n1 = params["n1"]
        n2 = params["n2"]

        if d <= 0:
            raise EngineError(f"d must be positive, got {d}", code="OUT_OF_RANGE", field="d")
        if beta_alpha_ratio <= 0:
            raise EngineError(f"beta_alpha_ratio must be positive, got {beta_alpha_ratio}", code="OUT_OF_RANGE", field="beta_alpha_ratio")
        if n1 < 2:
            raise EngineError(f"n1 must be >= 2, got {n1}", code="OUT_OF_RANGE", field="n1")
        if n2 < 2:
            raise EngineError(f"n2 must be >= 2, got {n2}", code="OUT_OF_RANGE", field="n2")

        return compute_t2_compromise(tails=tails, d=d, beta_alpha_ratio=beta_alpha_ratio, n1=n1, n2=n2)

    elif mode == "criterion":
        required = ["d", "power", "n1", "n2"]
        for p in required:
            if p not in params:
                raise EngineError(f"Missing parameter '{p}' for mode '{mode}'", code="MISSING_PARAM", field=p)
        d = params["d"]
        power = params["power"]
        n1 = params["n1"]
        n2 = params["n2"]

        if not (0 < power < 1):
            raise EngineError(f"power must be between 0 and 1, got {power}", code="OUT_OF_RANGE", field="power")
        if d <= 0:
            raise EngineError(f"d must be positive, got {d}", code="OUT_OF_RANGE", field="d")
        if n1 < 2:
            raise EngineError(f"n1 must be >= 2, got {n1}", code="OUT_OF_RANGE", field="n1")
        if n2 < 2:
            raise EngineError(f"n2 must be >= 2, got {n2}", code="OUT_OF_RANGE", field="n2")

        return compute_t2_criterion(tails=tails, d=d, power=power, n1=n1, n2=n2)

    elif mode == "sensitivity":
        required = ["alpha", "power", "n1", "n2"]
        for p in required:
            if p not in params:
                raise EngineError(f"Missing parameter '{p}' for mode '{mode}'", code="MISSING_PARAM", field=p)
        alpha = params["alpha"]
        power = params["power"]
        n1 = params["n1"]
        n2 = params["n2"]

        if not (0 < alpha < 1):
            raise EngineError(f"alpha must be between 0 and 1, got {alpha}", code="OUT_OF_RANGE", field="alpha")
        if not (0 < power < 1):
            raise EngineError(f"power must be between 0 and 1, got {power}", code="OUT_OF_RANGE", field="power")
        if n1 < 2:
            raise EngineError(f"n1 must be >= 2, got {n1}", code="OUT_OF_RANGE", field="n1")
        if n2 < 2:
            raise EngineError(f"n2 must be >= 2, got {n2}", code="OUT_OF_RANGE", field="n2")

        return compute_t2_sensitivity(tails=tails, alpha=alpha, power=power, n1=n1, n2=n2)
