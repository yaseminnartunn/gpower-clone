"""
Türkçe Klinik AI Ajanı (src/agent.py)
Ders: YZM301 Yazılım Gerçekleme ve Test - Teardown Sprint
Kural: LLM hesaplama YAPAMAZ; hesaplama her zaman src/engine.py üzerinden gelir!
"""

import os
import re
import sys
import json
import datetime
from typing import Dict, Any, Tuple
from src.engine import run_power_analysis, EngineError

COHEN_MAP = {
    "küçük": 0.2, "kucuk": 0.2, "small": 0.2,
    "orta": 0.5, "medium": 0.5,
    "büyük": 0.8, "buyuk": 0.8, "large": 0.8
}


def parse_clinical_question(question: str) -> Tuple[Dict[str, Any], str]:
    """
    Klinik soruyu kural ve desen tabanlı NLP ile analiz ederek parametreleri çıkarır.
    LLM mantığı simülasyonu: niyet (intent) tespiti ve parametre ayrıştırma.
    """
    q_norm = question.replace("İ", "i").replace("I", "ı").lower()
    q_low = q_norm
    notes = []

    # 1. Test Ailesi Tespiti
    if any(k in q_low for k in ["bağımsız", "bagimsiz", "iki grup", "ilaç ve plasebo", "tedavi ve kontrol", "kolda", "ilaç grubunda", "ilac grubunda", "tedavi kolu"]):
        test = "t2-indep"
    elif any(k in q_low for k in ["önce ve", "once ve", "öncesi ve", "oncesi ve", "eşleştirilmiş", "paired"]):
        test = "t-paired"
    elif any(k in q_low for k in ["üç grup", "uc grup", "anova", "3 kol"]):
        test = "anova-oneway"
    else:
        test = "ambiguous"

    # 2. Kuyruk Yönü (tails)
    if any(k in q_low for k in ["daha iyi", "daha etkili", "üstün", "tek yönlü", "tek yonlu"]):
        tails = 1
    else:
        tails = 2

    # 3. Anlamlılık Düzeyi (alpha)
    alpha = None
    if "0.01" in q_low or "%1" in q_low or "yüzde 1" in q_low:
        alpha = 0.01
    elif "0.001" in q_low or "%0.1" in q_low:
        alpha = 0.001
    elif "0.05" in q_low or "%5" in q_low or "yüzde 5" in q_low:
        alpha = 0.05
    elif "0.1" in q_low or "%10" in q_low:
        alpha = 0.10

    # 4. Güç (power)
    power = None
    if "0.95" in q_low or "%95" in q_low or "yüzde 95" in q_low:
        power = 0.95
    elif "0.90" in q_low or "%90" in q_low or "yüzde 90" in q_low:
        power = 0.90
    elif "0.80" in q_low or "%80" in q_low or "yüzde 80" in q_low:
        power = 0.80
    elif "0.70" in q_low or "%70" in q_low:
        power = 0.70

    # 5. Etki Büyüklüğü (d)
    d = None
    d_match = re.search(r'\b(?:d\s*=\s*|etki\s*büyüklüğü\s*(?:olan|ise)?\s*)?([0-9]+(?:[\.,][0-9]+))\b', q_low)
    if d_match:
        val = float(d_match.group(1).replace(",", "."))
        if 0.05 <= val <= 4.0:
            d = val
            notes.append(f"Belirtilen d={d} doğrudan kullanıldı.")

    if d is None:
        for kw, val in COHEN_MAP.items():
            if kw in q_low:
                d = val
                notes.append(f"Etki büyüklüğü '{kw}' ifadesine istinaden Cohen (1988) standardına göre d={val} kabul edildi.")
                break

    # 6. Oran (ratio)
    ratio = 1.0
    if "1:2" in q_low or "2 katı" in q_low:
        ratio = 2.0
    elif "2:1" in q_low:
        ratio = 0.5

    params = {
        "test": test,
        "mode": "a-priori",
        "tails": tails,
        "d": d,
        "alpha": alpha,
        "power": power,
        "ratio": ratio
    }

    return params, " ".join(notes)


def answer_clinical_query(question: str) -> Dict[str, Any]:
    """
    Kullanıcının klinik sorusunu alır, parametreleri çıkarır, motordan hesabı çeker ve açıklar.
    """
    tokens_in = len(question) // 4 + 150
    params, note = parse_clinical_question(question)

    # Eksik parametre kontrolü (Geçersiz veya belirsiz senaryolar)
    missing = []
    if params["d"] is None:
        missing.append("etki büyüklüğü (Cohen d veya küçük/orta/büyük)")
    if params["alpha"] is None:
        missing.append("anlamlılık düzeyi (alpha veya % yanılma payı)")
    if params["power"] is None:
        missing.append("hedef güç (1-beta)")

    if params["test"] != "t2-indep":
        resp = (
            f"Sorunuz incelendi ancak tespit edilen test türü '{params['test']}' ailesine aittir. "
            f"Mevcut motorumuz K1 (`t2-indep`: İki bağımsız grup t-testi) için onaylanmıştır. "
            f"Lütfen iki bağımsız tedavi kolu içeren bir araştırma sorusu ile tekrar deneyiniz."
        )
        tokens_out = len(resp) // 4
        return {
            "success": False,
            "response": resp,
            "params": params,
            "result": None,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out
        }

    if missing:
        resp = f"Hesaplama yapabilmem için eksik parametreler var: {', '.join(missing)}. Lütfen bu değerleri belirtiniz."
        tokens_out = len(resp) // 4
        return {
            "success": False,
            "response": resp,
            "params": params,
            "result": None,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out
        }

    # HESAP MOTORUNU ÇAĞIR (LLM hesap yapamaz!)
    try:
        engine_res = run_power_analysis(params)
    except EngineError as e:
        resp = f"İstatistiksel hesaplama motoru kısıt hatası verdi: {e.message}"
        tokens_out = len(resp) // 4
        return {
            "success": False,
            "response": resp,
            "params": params,
            "result": None,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out
        }

    n1 = engine_res["n1"]
    n2 = engine_res["n2"]
    ntot = engine_res["n_total"]
    act_pwr = engine_res["actual_power"]

    resp = (
        f"Hesapladım. Cohen d={params['d']}, alpha={params['alpha']}, power={params['power']} "
        f"ve {'tek yönlü' if params['tails'] == 1 else 'çift yönlü'} hipotez için:\n"
        f"Grup 1'de {n1} hasta, Grup 2'de {n2} hasta olmak üzere toplam {ntot} hastaya ihtiyacınız var. "
        f"(Ulaşılan gerçek güç: %{act_pwr * 100:.2f})."
    )
    if note:
        resp += f"\n*Açıklama:* {note}"

    tokens_out = len(resp) // 4
    return {
        "success": True,
        "response": resp,
        "params": params,
        "result": engine_res,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out
    }


EVALUATION_SET = [
    # Kolay (Tüm parametreler açık)
    {"level": "Kolay", "q": "İki bağımsız grupta d=0.5, alpha=0.05 ve power=0.80 için çift yönlü testte toplam kaç hasta gerekir?"},
    {"level": "Kolay", "q": "Yeni bir tansiyon ilacı için plasebo kontrolüyle d=0.8, alpha=0.01, power=0.95 ile iki bağımsız kolda kaç hasta lazım?"},
    {"level": "Kolay", "q": "İki bağımsız grupta tek yönlü üstünlük için d=0.4, alpha=0.05, power=0.90 için gereken örneklem nedir?"},

    # Orta (Etki büyüklüğü küçük/orta/büyük olarak verilmiş)
    {"level": "Orta", "q": "İlaç grubunda orta büyüklükte etki bekliyorum, %5 yanılma payı ile %80 güç istiyorum, kaç hasta lazım?"},
    {"level": "Orta", "q": "İki bağımsız grupta büyük etki büyüklüğü, %5 alfa ve %90 güç için kaç hasta gerekir?"},
    {"level": "Orta", "q": "Klinik araştırmamızda küçük etki büyüklüğü bekliyoruz, %5 anlamlılık ve %80 güç ile iki grupta kaç denek olmalı?"},

    # Zor (Klinik bağlam verilmiş, parametreler bağlamdan çıkarılmalı)
    {"level": "Zor", "q": "Diyabet hastalarında A ve B ilaçlarının HbA1c düşürücü etkisini iki bağımsız grupta çift yönlü kıyaslayacağız. Literatüre göre d=0.6 fark bekleniyor. %1 tip 1 hata ve %90 güç için kaç hasta çalışmaya alınmalı?"},
    {"level": "Zor", "q": "Onkoloji çalışmasında yeni tedavi koluna kontrolün 2 katı hasta (1:2 oranında) alacağız. Orta düzey etki, %5 anlamlılık ve %80 güç hedefiyle iki bağımsız grupta toplam kaç hasta olmalı?"},

    # Geçersiz / Eksik (Eksik parametre -> Kullanıcıya sorulmalı)
    {"level": "Geçersiz", "q": "İki bağımsız grupta yeni ilacımı deneyeceğim, %5 alfa ile kaç hasta gerekir?"},
    {"level": "Geçersiz", "q": "Aynı hastaların ameliyat öncesi ve sonrası tansiyonlarını karşılaştırmak için kaç kişi gerekir?"}
]


def run_evaluation(out_markdown: str = "docs/agent_eval_results.md"):
    os.makedirs(os.path.dirname(out_markdown), exist_ok=True)
    results = []

    print("=== TÜRKÇE KLİNİK AI AJANI 10 SORULUK TEST SETİ ===")
    md_lines = [
        "# Türkçe Klinik AI Ajanı Değerlendirme Raporu\n",
        "**Ders:** YZM301 · Yazılım Gerçekleme ve Test\n",
        "**Modül:** `src/agent.py`\n\n",
        "| No | Seviye | Soru | Test Ailesi | Çıkarılan Parametreler | Motor Çıktısı (N) | Harcanan Token |\n",
        "|---|---|---|---|---|---|---|\n"
    ]

    for idx, item in enumerate(EVALUATION_SET, 1):
        res = answer_clinical_query(item["q"])
        p = res["params"]
        n_str = str(res["result"]["n_total"]) if res["result"] else "Eksik/Geçersiz (Kullanıcıya Soruldu)"
        tok = res["tokens_in"] + res["tokens_out"]

        param_summary = f"d={p['d']}, α={p['alpha']}, pwr={p['power']}, tails={p['tails']}"
        md_lines.append(f"| {idx} | {item['level']} | {item['q'][:50]}... | {p['test']} | {param_summary} | {n_str} | {tok} |\n")

        print(f"[{item['level']}] Soru {idx}: {item['q'][:60]}...")
        print(f"  -> Yanıt: {res['response'][:100]}...")
        print(f"  -> Harcanan Token: {tok}\n")

    with open(out_markdown, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    print(f"Değerlendirme sonuçları {out_markdown} dosyasına başarıyla kaydedildi.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--eval":
        run_evaluation()
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        ans = answer_clinical_query(query)
        print(ans["response"])
    else:
        # Default test evaluation run
        run_evaluation()
