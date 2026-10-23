import pytest
from src.engine import run_power_analysis, EngineError

def test_a_priori_public():
    # From CONTRACT.md line 343:
    # {"id":"t2-indep/a-priori","input":{"test":"t2-indep","mode":"a-priori","tails":1,"d":0.5,"alpha":0.05,"power":0.95,"ratio":1},"expected":{"ncp":3.3166248,"critical_t":1.6536580,"df":174,"n1":88,"n2":88,"n_total":176,"actual_power":0.9514254}}
    inp = {"test": "t2-indep", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0}
    exp = {"ncp": 3.3166248, "critical_t": 1.6536580, "df": 174, "n1": 88, "n2": 88, "n_total": 176, "actual_power": 0.9514254}
    res = run_power_analysis(inp)
    
    assert res["n1"] == exp["n1"]
    assert res["n2"] == exp["n2"]
    assert res["n_total"] == exp["n_total"]
    assert res["df"] == exp["df"]
    assert abs(res["ncp"] - exp["ncp"]) <= 1e-6
    assert abs(res["critical_t"] - exp["critical_t"]) <= 1e-6
    assert abs(res["actual_power"] - exp["actual_power"]) <= 1e-6


def test_post_hoc_public():
    # {"id":"t2-indep/post-hoc","input":{"test":"t2-indep","mode":"post-hoc","tails":1,"d":0.5,"alpha":0.05,"n1":88,"n2":88},"expected":{"ncp":3.3166248,"critical_t":1.6536580,"df":174,"power":0.9514254}}
    inp = {"test": "t2-indep", "mode": "post-hoc", "tails": 1, "d": 0.5, "alpha": 0.05, "n1": 88, "n2": 88}
    exp = {"ncp": 3.3166248, "critical_t": 1.6536580, "df": 174, "power": 0.9514254}
    res = run_power_analysis(inp)
    
    assert res["df"] == exp["df"]
    assert abs(res["ncp"] - exp["ncp"]) <= 1e-6
    assert abs(res["critical_t"] - exp["critical_t"]) <= 1e-6
    assert abs(res["power"] - exp["power"]) <= 1e-6


def test_compromise_public():
    # {"id":"t2-indep/compromise","input":{"test":"t2-indep","mode":"compromise","tails":1,"d":0.5,"beta_alpha_ratio":1,"n1":88,"n2":88},"expected":{"ncp":3.3166248,"critical_t":1.6606859,"df":174,"alpha":0.0492887,"beta":0.0492887,"power":0.9507113}}
    inp = {"test": "t2-indep", "mode": "compromise", "tails": 1, "d": 0.5, "beta_alpha_ratio": 1.0, "n1": 88, "n2": 88}
    exp = {"ncp": 3.3166248, "critical_t": 1.6606859, "df": 174, "alpha": 0.0492887, "beta": 0.0492887, "power": 0.9507113}
    res = run_power_analysis(inp)
    
    assert res["df"] == exp["df"]
    assert abs(res["ncp"] - exp["ncp"]) <= 1e-6
    assert abs(res["critical_t"] - exp["critical_t"]) <= 1e-6
    assert abs(res["alpha"] - exp["alpha"]) <= 1e-6
    assert abs(res["beta"] - exp["beta"]) <= 1e-6
    assert abs(res["power"] - exp["power"]) <= 1e-6


def test_criterion_public():
    # {"id":"t2-indep/criterion","input":{"test":"t2-indep","mode":"criterion","tails":1,"d":0.5,"power":0.95,"n1":88,"n2":88},"expected":{"ncp":3.3166248,"critical_t":1.6676050,"df":174,"alpha":0.0485965}}
    inp = {"test": "t2-indep", "mode": "criterion", "tails": 1, "d": 0.5, "power": 0.95, "n1": 88, "n2": 88}
    exp = {"ncp": 3.3166248, "critical_t": 1.6676050, "df": 174, "alpha": 0.0485965}
    res = run_power_analysis(inp)
    
    assert res["df"] == exp["df"]
    assert abs(res["ncp"] - exp["ncp"]) <= 1e-6
    assert abs(res["critical_t"] - exp["critical_t"]) <= 1e-6
    assert abs(res["alpha"] - exp["alpha"]) <= 1e-6


def test_sensitivity_public():
    # {"id":"t2-indep/sensitivity","input":{"test":"t2-indep","mode":"sensitivity","tails":1,"alpha":0.05,"power":0.95,"n1":88,"n2":88},"expected":{"ncp":3.3025887,"critical_t":1.6536580,"df":174,"d":0.4978840}}
    inp = {"test": "t2-indep", "mode": "sensitivity", "tails": 1, "alpha": 0.05, "power": 0.95, "n1": 88, "n2": 88}
    exp = {"ncp": 3.3025887, "critical_t": 1.6536580, "df": 174, "d": 0.4978840}
    res = run_power_analysis(inp)
    
    assert res["df"] == exp["df"]
    assert abs(res["ncp"] - exp["ncp"]) <= 1e-6
    assert abs(res["critical_t"] - exp["critical_t"]) <= 1e-6
    assert abs(res["d"] - exp["d"]) <= 1e-6


def test_boundary_and_errors():
    # Power <= Alpha should raise INCONSISTENT
    with pytest.raises(EngineError) as excinfo:
        run_power_analysis({"test": "t2-indep", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.04, "ratio": 1.0})
    assert excinfo.value.code == "INCONSISTENT"

    # Unsupported test family
    with pytest.raises(EngineError) as excinfo:
        run_power_analysis({"test": "unknown-test", "mode": "a-priori"})
    assert excinfo.value.code == "UNSUPPORTED"

    # Invalid tails
    with pytest.raises(EngineError) as excinfo:
        run_power_analysis({"test": "t2-indep", "mode": "a-priori", "tails": 3, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0})
    assert excinfo.value.code == "OUT_OF_RANGE"
