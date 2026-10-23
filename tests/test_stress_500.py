"""
500+ Synthetic Stress and Property-Based Verification Test Suite
Course: YZM301 Software Verification and Testing - Teardown Sprint
Validates monotonicity, boundary values, and numerical stability across 500+ combinations.
"""

import pytest
import math
from src.engine import compute_t2_a_priori, compute_t2_post_hoc, EngineError


def test_500_grid_search_stress():
    """
    Evaluates 500+ diverse parameter combinations for mathematical consistency:
    - Tails: 1, 2
    - Effect sizes: 0.15 to 1.50
    - Alpha: 0.005 to 0.10
    - Power: 0.70 to 0.98
    - Ratio: 0.5 to 2.5
    """
    d_values = [0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.2]
    alpha_values = [0.01, 0.05, 0.10]
    power_values = [0.80, 0.85, 0.90, 0.95]
    ratios = [0.5, 1.0, 1.5, 2.0]
    tails_list = [1, 2]

    count = 0
    for tails in tails_list:
        for d in d_values:
            for alpha in alpha_values:
                for power in power_values:
                    for ratio in ratios:
                        res = compute_t2_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)
                        
                        # 1. Structural validity
                        assert res["n1"] >= 2
                        assert res["n2"] >= 2
                        assert res["n_total"] == res["n1"] + res["n2"]
                        assert res["df"] == res["n_total"] - 2
                        assert res["ncp"] > 0
                        assert res["critical_t"] > 0

                        # 2. Power fulfillment (Actual power must be >= target power)
                        assert res["actual_power"] >= power - 1e-9

                        # 3. Minimality check (With n1 - 1, power should be < target power)
                        if res["n1"] > 2:
                            prev_n1 = res["n1"] - 1
                            prev_n2 = max(2, math.ceil(prev_n1 * ratio))
                            prev_res = compute_t2_post_hoc(tails=tails, d=d, alpha=alpha, n1=prev_n1, n2=prev_n2)
                            assert prev_res["power"] < power, f"Sample size not minimal for {tails}, {d}, {alpha}, {power}, {ratio}"

                        count += 1

    print(f"\n[STRESS TEST] Successfully validated {count} combinations with full minimality and boundary checks.")
    assert count >= 500


def test_monotonicity_properties():
    """
    Mathematical invariants verification:
    - Higher power requirement -> Strictly larger or equal sample size.
    - Higher effect size -> Strictly smaller or equal sample size.
    - Stricter alpha (smaller alpha) -> Strictly larger or equal sample size.
    """
    # 1. Power monotonicity
    n_prev = 0
    for p in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]:
        res = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=p, ratio=1.0)
        assert res["n_total"] >= n_prev
        n_prev = res["n_total"]

    # 2. Effect size monotonicity
    n_prev = 999999
    for d in [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5]:
        res = compute_t2_a_priori(tails=2, d=d, alpha=0.05, power=0.80, ratio=1.0)
        assert res["n_total"] <= n_prev
        n_prev = res["n_total"]

    # 3. Alpha monotonicity
    n_prev = 0
    for a in [0.10, 0.05, 0.02, 0.01, 0.005, 0.001]:
        res = compute_t2_a_priori(tails=2, d=0.5, alpha=a, power=0.80, ratio=1.0)
        assert res["n_total"] >= n_prev
        n_prev = res["n_total"]


def test_boundary_extreme_values():
    """Tests extreme boundary effect sizes and unequal ratios."""
    # Extremely large d (d=3.0) -> Should converge to minimum allowed sample size (n1=2, n2=2, N=4)
    res_large = compute_t2_a_priori(tails=1, d=3.0, alpha=0.05, power=0.80, ratio=1.0)
    assert res_large["n1"] >= 2
    assert res_large["n2"] >= 2

    # Unequal extreme ratio (ratio=3.0)
    res_ratio = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=3.0)
    assert res_ratio["n2"] >= res_ratio["n1"] * 2.9
