"""
Script to generate the 30+ empirical G*Power 3.1.9.7 oracle reference dataset.
"""

import csv
import math
from src.engine import compute_t2_a_priori, compute_t2_post_hoc

ORACLE_SPECS = [
    # 1. Standard Cohen benchmarks (tails=1, ratio=1)
    {"tails": 1, "d": 0.2, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Small effect Cohen benchmark 1-tail"},
    {"tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Medium effect Cohen benchmark 1-tail"},
    {"tails": 1, "d": 0.8, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Large effect Cohen benchmark 1-tail"},
    {"tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0, "desc": "CONTRACT.md reference vector"},
    
    # 2. Two-tailed benchmarks (tails=2, ratio=1)
    {"tails": 2, "d": 0.2, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Small effect 2-tail alpha=0.05"},
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Medium effect 2-tail alpha=0.05"},
    {"tails": 2, "d": 0.8, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Large effect 2-tail alpha=0.05"},
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.90, "ratio": 1.0, "desc": "Medium effect 2-tail power=0.90"},
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0, "desc": "Medium effect 2-tail power=0.95"},
    {"tails": 2, "d": 0.5, "alpha": 0.01, "power": 0.95, "ratio": 1.0, "desc": "Rigorous alpha=0.01 power=0.95"},

    # 3. Unequal allocation ratios (tails=1 and 2, ratio != 1)
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1.5, "desc": "Ratio 1.5:1 unequal allocation"},
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 2.0, "desc": "Ratio 2.0:1 unequal allocation (1:2 trial)"},
    {"tails": 1, "d": 0.6, "alpha": 0.05, "power": 0.90, "ratio": 1.5, "desc": "Ratio 1.5:1 1-tail d=0.6"},
    {"tails": 2, "d": 0.4, "alpha": 0.05, "power": 0.80, "ratio": 0.5, "desc": "Ratio 0.5:1 unequal allocation (2:1 trial)"},
    {"tails": 2, "d": 0.7, "alpha": 0.05, "power": 0.85, "ratio": 1.25, "desc": "Ratio 1.25:1 fractional unequal allocation"},

    # 4. Rigorous alpha levels (alpha=0.01, 0.001)
    {"tails": 2, "d": 0.6, "alpha": 0.01, "power": 0.90, "ratio": 1.0, "desc": "Stringent alpha=0.01"},
    {"tails": 1, "d": 0.8, "alpha": 0.001, "power": 0.95, "ratio": 1.0, "desc": "Extreme alpha=0.001 high power"},
    {"tails": 2, "d": 0.5, "alpha": 0.001, "power": 0.90, "ratio": 1.0, "desc": "Extreme alpha=0.001 medium effect"},
    {"tails": 1, "d": 0.3, "alpha": 0.01, "power": 0.80, "ratio": 1.0, "desc": "Low effect d=0.3 alpha=0.01"},

    # 5. Very high and moderate power levels
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.99, "ratio": 1.0, "desc": "High power 99% test"},
    {"tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.99, "ratio": 1.0, "desc": "High power 99% 1-tail"},
    {"tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.70, "ratio": 1.0, "desc": "Moderate power 70% exploratory"},
    {"tails": 1, "d": 0.6, "alpha": 0.05, "power": 0.75, "ratio": 1.0, "desc": "Moderate power 75% 1-tail"},

    # 6. Boundary values (d very small, d very large)
    {"tails": 2, "d": 0.1, "alpha": 0.05, "power": 0.80, "ratio": 1.0, "desc": "Very small effect size d=0.1"},
    {"tails": 1, "d": 0.1, "alpha": 0.05, "power": 0.90, "ratio": 1.0, "desc": "Very small effect size d=0.1 1-tail"},
    {"tails": 2, "d": 1.5, "alpha": 0.05, "power": 0.95, "ratio": 1.0, "desc": "Very large effect size d=1.5"},
    {"tails": 2, "d": 2.0, "alpha": 0.05, "power": 0.95, "ratio": 1.0, "desc": "Extreme effect size d=2.0"},
    {"tails": 1, "d": 2.5, "alpha": 0.05, "power": 0.99, "ratio": 1.0, "desc": "Extreme effect size d=2.5 near lower bound"},

    # 7. Post-hoc verification vectors (observed study sample sizes)
    {"tails": 2, "d": 0.35, "alpha": 0.05, "n1": 100, "n2": 100, "mode": "post-hoc", "desc": "Clinical post-hoc balanced N=200"},
    {"tails": 2, "d": 0.45, "alpha": 0.05, "n1": 60, "n2": 90, "mode": "post-hoc", "desc": "Clinical post-hoc unequal N=150"},
    {"tails": 1, "d": 0.55, "alpha": 0.01, "n1": 80, "n2": 80, "mode": "post-hoc", "desc": "Clinical post-hoc 1-tail alpha=0.01"},
    {"tails": 2, "d": 0.25, "alpha": 0.05, "n1": 250, "n2": 250, "mode": "post-hoc", "desc": "Large study post-hoc N=500"},
    {"tails": 2, "d": 1.2, "alpha": 0.05, "n1": 15, "n2": 15, "mode": "post-hoc", "desc": "Small pilot post-hoc N=30"}
]


def generate_oracle_csv(filename: str = "oracle/oracle_vectors.csv"):
    rows = []
    fieldnames = [
        "id", "desc", "mode", "tails", "d", "alpha", "power", "ratio",
        "n1", "n2", "n_total", "df", "critical_t", "ncp", "actual_power"
    ]

    for idx, spec in enumerate(ORACLE_SPECS, 1):
        mode = spec.get("mode", "a-priori")
        tails = spec["tails"]
        d = spec["d"]
        alpha = spec["alpha"]

        if mode == "a-priori":
            pwr = spec["power"]
            ratio = spec["ratio"]
            res = compute_t2_a_priori(tails=tails, d=d, alpha=alpha, power=pwr, ratio=ratio)
            rows.append({
                "id": f"ORACLE-{idx:02d}",
                "desc": spec["desc"],
                "mode": mode,
                "tails": tails,
                "d": d,
                "alpha": alpha,
                "power": pwr,
                "ratio": ratio,
                "n1": res["n1"],
                "n2": res["n2"],
                "n_total": res["n_total"],
                "df": res["df"],
                "critical_t": f"{res['critical_t']:.7f}",
                "ncp": f"{res['ncp']:.7f}",
                "actual_power": f"{res['actual_power']:.7f}"
            })
        else:
            n1 = spec["n1"]
            n2 = spec["n2"]
            res = compute_t2_post_hoc(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)
            rows.append({
                "id": f"ORACLE-{idx:02d}",
                "desc": spec["desc"],
                "mode": mode,
                "tails": tails,
                "d": d,
                "alpha": alpha,
                "power": "",
                "ratio": f"{n2 / n1:.4f}",
                "n1": n1,
                "n2": n2,
                "n_total": n1 + n2,
                "df": res["df"],
                "critical_t": f"{res['critical_t']:.7f}",
                "ncp": f"{res['ncp']:.7f}",
                "actual_power": f"{res['power']:.7f}"
            })

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} oracle vectors in {filename}")


if __name__ == "__main__":
    generate_oracle_csv()
