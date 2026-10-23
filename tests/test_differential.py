"""
Diferansiyel Test Paketi (tests/test_differential.py)
Ders: YZM301 Yazılım Gerçekleme ve Test - Teardown Sprint
K1: t2-indep test ailesi için G*Power 3.1.9.7 diferansiyel doğrulama testleri.
"""

import json
import csv
import pytest
from src.engine import run_power_analysis, compute_t2_a_priori, compute_t2_post_hoc


def test_public_vectors_differential():
    """CONTRACT.md Bölüm 9'da verilen açık referans vektörleri ile diferansiyel test."""
    with open("tests/public_vectors.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            inp = item["input"]
            exp = item["expected"]

            res = run_power_analysis(inp)

            if "n_total" in exp:
                assert res["n_total"] == exp["n_total"]
            if "n1" in exp:
                assert res["n1"] == exp["n1"]
            if "n2" in exp:
                assert res["n2"] == exp["n2"]
            if "df" in exp:
                assert res["df"] == exp["df"]

            for field in ["ncp", "critical_t", "actual_power", "power", "alpha", "beta", "d"]:
                if field in exp:
                    diff = abs(res[field] - exp[field])
                    assert diff <= 1e-6, f"[{item['id']}] {field} farkı {diff} > 1e-6"


def test_oracle_csv_differential():
    """oracle/oracle_vectors.csv içerisindeki 33 G*Power vektörü ile tam eşleşme testi."""
    with open("oracle/oracle_vectors.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
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
                pwr = float(row["power"])
                ratio = float(row["ratio"])
                res = compute_t2_a_priori(tails=tails, d=d, alpha=alpha, power=pwr, ratio=ratio)

                assert res["n1"] == exp_n1
                assert res["n2"] == exp_n2
                assert res["n_total"] == exp_ntot
                assert res["df"] == exp_df
                assert abs(res["critical_t"] - exp_crit) <= 1e-6
                assert abs(res["ncp"] - exp_ncp) <= 1e-6
                assert abs(res["actual_power"] - exp_pwr) <= 1e-6
            else:
                res = compute_t2_post_hoc(tails=tails, d=d, alpha=alpha, n1=exp_n1, n2=exp_n2)
                assert res["df"] == exp_df
                assert abs(res["critical_t"] - exp_crit) <= 1e-6
                assert abs(res["ncp"] - exp_ncp) <= 1e-6
                assert abs(res["power"] - exp_pwr) <= 1e-6
