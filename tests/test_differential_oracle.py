"""
Differential Test Suite against G*Power Oracle Vectors
Course: YZM301 Software Verification and Testing - Teardown Sprint
Compares CLI / Engine against 33 G*Power Oracle vectors in oracle/oracle_vectors.csv
"""

import csv
import pytest
from src.engine import compute_t2_a_priori, compute_t2_post_hoc


def load_oracle_vectors():
    vectors = []
    with open("oracle/oracle_vectors.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vectors.append(row)
    return vectors


ORACLE_DATA = load_oracle_vectors()


@pytest.mark.parametrize("row", ORACLE_DATA)
def test_oracle_vector_match(row):
    """
    Validates that:
    1. Integer sample sizes (n1, n2, n_total, df) match EXACTLY (100% parity).
    2. Floating point values (ncp, critical_t, actual_power) match within 1e-6.
    """
    mode = row["mode"]
    tails = int(row["tails"])
    d = float(row["d"])
    alpha = float(row["alpha"])

    exp_n1 = int(row["n1"])
    exp_n2 = int(row["n2"])
    exp_ntot = int(row["n_total"])
    exp_df = int(row["df"])
    exp_crit = float(row["critical_t"])
    exp_ncp = float(row["ncp"])
    exp_pwr = float(row["actual_power"])

    if mode == "a-priori":
        power = float(row["power"])
        ratio = float(row["ratio"])
        res = compute_t2_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)

        # Gate Requirement: N, n1, n2 must match EXACTLY
        assert res["n1"] == exp_n1, f"[{row['id']}] n1 mismatch: got {res['n1']}, exp {exp_n1}"
        assert res["n2"] == exp_n2, f"[{row['id']}] n2 mismatch: got {res['n2']}, exp {exp_n2}"
        assert res["n_total"] == exp_ntot, f"[{row['id']}] n_total mismatch: got {res['n_total']}, exp {exp_ntot}"
        assert res["df"] == exp_df, f"[{row['id']}] df mismatch: got {res['df']}, exp {exp_df}"

        # Double precision tolerance: <= 1e-6
        assert abs(res["critical_t"] - exp_crit) <= 1e-6, f"[{row['id']}] critical_t diff: {abs(res['critical_t'] - exp_crit)}"
        assert abs(res["ncp"] - exp_ncp) <= 1e-6, f"[{row['id']}] ncp diff: {abs(res['ncp'] - exp_ncp)}"
        assert abs(res["actual_power"] - exp_pwr) <= 1e-6, f"[{row['id']}] actual_power diff: {abs(res['actual_power'] - exp_pwr)}"

    else:
        # post-hoc
        res = compute_t2_post_hoc(tails=tails, d=d, alpha=alpha, n1=exp_n1, n2=exp_n2)

        assert res["df"] == exp_df
        assert abs(res["critical_t"] - exp_crit) <= 1e-6
        assert abs(res["ncp"] - exp_ncp) <= 1e-6
        assert abs(res["power"] - exp_pwr) <= 1e-6
