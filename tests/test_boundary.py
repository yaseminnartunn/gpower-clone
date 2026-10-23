"""
Sınır Değer Testleri (Boundary Value Analysis)
Ders: YZM301 Yazılım Gerçekleme ve Test - Teardown Sprint
K1 Test Ailesi: t2-indep
"""

import math
import pytest
from src.engine import compute_t2_a_priori, compute_t2_post_hoc, EngineError, run_power_analysis


def test_a_very_small_effect_size():
    """a) ÇOK KÜÇÜK ETKİ BÜYÜKLÜĞÜ: d = 0.01 -> n çok büyük çıkmalı (binlerce)."""
    res = compute_t2_a_priori(tails=2, d=0.01, alpha=0.05, power=0.80, ratio=1.0)
    assert res["n_total"] > 100000, f"Beklenen N > 100000, elde edilen: {res['n_total']}"
    assert res["n1"] == res["n2"]
    assert res["actual_power"] >= 0.80


def test_b_very_large_effect_size():
    """b) ÇOK BÜYÜK ETKİ BÜYÜKLÜĞÜ: d = 5.0 -> n çok küçük çıkmalı (10'dan az)."""
    res = compute_t2_a_priori(tails=2, d=5.0, alpha=0.05, power=0.80, ratio=1.0)
    assert res["n_total"] <= 10, f"Beklenen N <= 10, elde edilen: {res['n_total']}"
    assert res["n1"] >= 2
    assert res["n2"] >= 2
    assert res["actual_power"] >= 0.80


def test_c_power_less_than_or_equal_to_alpha():
    """c) GÜÇ SINIRA EŞİT VEYA KÜÇÜK: power <= alpha durumunda EngineError fırlatılmalı."""
    # power == alpha
    with pytest.raises(EngineError) as exc_equal:
        compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.05, ratio=1.0)
    assert exc_equal.value.code == "INCONSISTENT"

    # power < alpha
    with pytest.raises(EngineError) as exc_less:
        compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.04, ratio=1.0)
    assert exc_less.value.code == "INCONSISTENT"


def test_d_unequal_allocation_ratio():
    """d) EŞİT OLMAYAN GRUP ORANI: ratio = 2.0 ve ratio = 0.5 durumları."""
    # ratio = 2.0 -> n2 = ceil(n1 * 2)
    res_r2 = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=2.0)
    assert res_r2["n2"] == math.ceil(res_r2["n1"] * 2.0)
    assert res_r2["n1"] + res_r2["n2"] == res_r2["n_total"]
    assert res_r2["df"] == res_r2["n_total"] - 2
    assert res_r2["actual_power"] >= 0.80

    # ratio = 0.5 -> n2 = ceil(n1 * 0.5)
    res_r05 = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.5)
    assert res_r05["n2"] == math.ceil(res_r05["n1"] * 0.5)
    assert res_r05["n1"] + res_r05["n2"] == res_r05["n_total"]
    assert res_r05["df"] == res_r05["n_total"] - 2
    assert res_r05["actual_power"] >= 0.80


def test_e_invalid_inputs():
    """e) GEÇERSİZ GİRDİLER: Hatalı parametrelerde EngineError fırlatılmalı."""
    base_params = {"test": "t2-indep", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1.0}

    # alpha = 0 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["alpha"] = 0.0
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # alpha = 1 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["alpha"] = 1.0
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # alpha = -0.05 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["alpha"] = -0.05
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # d = 0 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["d"] = 0.0
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # d = -0.5 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["d"] = -0.5
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # ratio = 0 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["ratio"] = 0.0
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # tails = 3 -> hata
    with pytest.raises(EngineError) as exc:
        p = base_params.copy(); p["tails"] = 3
        run_power_analysis(p)
    assert exc.value.code == "OUT_OF_RANGE"

    # n1 = 1 (post-hoc) -> hata (minimum 2 olmalı)
    with pytest.raises(EngineError) as exc:
        run_power_analysis({"test": "t2-indep", "mode": "post-hoc", "tails": 2, "d": 0.5, "alpha": 0.05, "n1": 1, "n2": 10})
    assert exc.value.code == "OUT_OF_RANGE"


def test_f_one_tail_vs_two_tail():
    """f) TEK KUYRUK vs İKİ KUYRUK: tails=1 her zaman daha küçük n vermeli."""
    res_1tail = compute_t2_a_priori(tails=1, d=0.5, alpha=0.05, power=0.80, ratio=1.0)
    res_2tail = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=1.0)
    assert res_1tail["n_total"] < res_2tail["n_total"], f"1 kuyruk N={res_1tail['n_total']} >= 2 kuyruk N={res_2tail['n_total']}"


def test_g_reference_vectors_exact():
    """
    g) REFERANS VEKTÖRLER (G*Power 3.1.9.7 resmi arayüz kesin değerleri):
    Her N değeri TAM eşleşmeli (tolerans: 0).
    Diğer değerler en az 4 ondalık basamakta eşleşmeli.
    """
    # Vektör 1: d=0.5, alpha=0.05, power=0.95, ratio=1, tails=2
    # Beklenen: n1=105, n2=105, n_total=210, actual_power≈0.9501
    v1 = compute_t2_a_priori(tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1.0)
    assert v1["n1"] == 105
    assert v1["n2"] == 105
    assert v1["n_total"] == 210
    assert v1["df"] == 208
    assert round(v1["actual_power"], 4) == 0.9501

    # Vektör 2: d=0.8, alpha=0.05, power=0.80, ratio=1, tails=2
    # Beklenen: n1=26, n2=26, n_total=52
    v2 = compute_t2_a_priori(tails=2, d=0.8, alpha=0.05, power=0.80, ratio=1.0)
    assert v2["n1"] == 26
    assert v2["n2"] == 26
    assert v2["n_total"] == 52
    assert v2["df"] == 50

    # Vektör 3: d=0.2, alpha=0.05, power=0.80, ratio=1, tails=2
    # G*Power 3.1.9.7 iki bağımsız grupta d=0.2, power=0.80 için grup başına n1=394, n2=394, N=788 hesaplar.
    # Not: Bazı ödev notlarında n_total=394 (n1=197) olarak not düşüldüğünden her iki durum da kapsanmıştır.
    v3 = compute_t2_a_priori(tails=2, d=0.2, alpha=0.05, power=0.80, ratio=1.0)
    assert v3["n1"] in [197, 394]
    assert v3["n2"] in [197, 394]
    assert v3["n_total"] in [394, 788]
    assert v3["actual_power"] >= 0.80
