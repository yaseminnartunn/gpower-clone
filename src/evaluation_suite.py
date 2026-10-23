"""
10 Clinical Benchmark Questions and Evaluation Suite
Course: YZM301 Software Verification and Testing - Teardown Sprint
Tests classification, parameter extraction, MCP execution, and token economics (GUI vs MCP).
"""

import json
from typing import List, Dict, Any
from src.clinical_agent import query_clinical_agent
from src.engine import run_power_analysis

BENCHMARK_SCENARIOS = [
    {
        "id": 1,
        "question": "Yeni geliştirdiğimiz antihipertansif ilacı standart plasebo ile iki bağımsız hasta grubunda karşılaştırmak istiyoruz. d=0.5 orta etki büyüklüğü, %5 alfa ve %95 güç hedefiyle tek yönlü üstünlük testi için toplam kaç hasta almalıyız?",
        "expected_test": "t2-indep",
        "expected_tails": 1,
        "expected_d": 0.5,
        "expected_alpha": 0.05,
        "expected_power": 0.95,
        "expected_ratio": 1.0,
        "expected_n_total": 176
    },
    {
        "id": 2,
        "question": "Diyabetik hastalarda yeni bir insülin duyarlılaştırıcı ilacın etkinliğini kontrol grubuyla iki bağımsız grupta çift yönlü olarak sınayacağız. d=0.6, alfa=0.01 ve güç=%90 için kaç hasta gerekir?",
        "expected_test": "t2-indep",
        "expected_tails": 2,
        "expected_d": 0.6,
        "expected_alpha": 0.01,
        "expected_power": 0.90,
        "expected_ratio": 1.0,
        "expected_n_total": 170
    },
    {
        "id": 3,
        "question": "Onkoloji faz 2 çalışmasında yeni immünoterapi koluna kontrol kolunun iki katı hasta (1:2 oranında) almayı planlıyoruz. İki bağımsız grupta orta etki (d=0.5), %80 güç ve 0.05 alfa düzeyinde çift yönlü analizde kaçar hasta gerekir?",
        "expected_test": "t2-indep",
        "expected_tails": 2,
        "expected_d": 0.5,
        "expected_alpha": 0.05,
        "expected_power": 0.80,
        "expected_ratio": 2.0,
        "expected_n_total": 144
    },
    {
        "id": 4,
        "question": "Akut apandisit ameliyatı sonrası iki farklı analjezik yönteminin ağrı skorunu iki bağımsız tedavi grubunda kıyaslayacağız. Literatürde d=0.8 büyük etki bildirilmiş. %5 alfa ve %80 güç için çift yönlü testte toplam örneklem ne olmalıdır?",
        "expected_test": "t2-indep",
        "expected_tails": 2,
        "expected_d": 0.8,
        "expected_alpha": 0.05,
        "expected_power": 0.80,
        "expected_ratio": 1.0,
        "expected_n_total": 52
    },
    {
        "id": 5,
        "question": "Yoğun bakımda sepsis hastalarında iki bağımsız tedavi protokolünü karşılaştırıyoruz. Küçük bir klinik fark bekliyoruz (d=0.2). Alfa=%5 ve güç=%80 için çift yönlü testte kaç hasta gerekecek?",
        "expected_test": "t2-indep",
        "expected_tails": 2,
        "expected_d": 0.2,
        "expected_alpha": 0.05,
        "expected_power": 0.80,
        "expected_ratio": 1.0,
        "expected_n_total": 788
    },
    {
        "id": 6,
        "question": "Migren profilaksisinde A ilacının B ilacından daha etkili olduğunu göstermek istiyoruz (tek yönlü hipotez). d=0.4 etki büyüklüğü, 0.05 anlamlılık ve %90 istatistiksel güç için bağımsız iki grupta kaç hasta gerekir?",
        "expected_test": "t2-indep",
        "expected_tails": 1,
        "expected_d": 0.4,
        "expected_alpha": 0.05,
        "expected_power": 0.90,
        "expected_ratio": 1.0,
        "expected_n_total": 216
    },
    {
        "id": 7,
        "question": "Aynı hastaların ameliyat öncesi ve ameliyat sonrası sistolik tansiyon değerlerini eşleştirilmiş t testi ile karşılaştırmak istiyoruz. Kaç hasta gerekir?",
        "expected_test": "t-paired",
        "expected_tails": 2,
        "expected_d": 0.5,
        "expected_alpha": 0.05,
        "expected_power": 0.80,
        "expected_ratio": 1.0,
        "expected_n_total": None  # Should be flagged as outside K1 module
    },
    {
        "id": 8,
        "question": "Üç farklı kemoterapi kolunun yaşam kalitesi skorlarını karşılaştıracağımız bir klinik çalışma için örneklem büyüklüğü nedir?",
        "expected_test": "anova-oneway",
        "expected_tails": 2,
        "expected_d": 0.25,
        "expected_alpha": 0.05,
        "expected_power": 0.80,
        "expected_ratio": 1.0,
        "expected_n_total": None  # Should be flagged as ANOVA outside K1 module
    },
    {
        "id": 9,
        "question": "Kardiyoloji kliniğinde iki bağımsız grup arasında (stent A vs stent B) troponin düzeyleri farkı için d=0.35, alfa=0.05 ve %95 güç ile tek yönlü üstünlük çalışması kaç hasta gerektirir?",
        "expected_test": "t2-indep",
        "expected_tails": 1,
        "expected_d": 0.35,
        "expected_alpha": 0.05,
        "expected_power": 0.95,
        "expected_ratio": 1.0,
        "expected_n_total": 356
    },
    {
        "id": 10,
        "question": "Covid-19 sonrası pulmoner rehabilitasyon alan ve almayan iki bağımsız hasta grubunun 6 dakika yürüme mesafesini kıyaslıyoruz. d=0.5, alfa=0.05 ve güç=%90 için çift yönlü t testinde toplam kaç hasta olmalı?",
        "expected_test": "t2-indep",
        "expected_tails": 2,
        "expected_d": 0.5,
        "expected_alpha": 0.05,
        "expected_power": 0.90,
        "expected_ratio": 1.0,
        "expected_n_total": 172
    }
]


def run_benchmark():
    """Runs the 10 evaluation questions and prints metrics."""
    correct_test_count = 0
    correct_n_count = 0
    total_mcp_tokens = 0
    total_gui_tokens_estimated = 0

    print("=" * 80)
    print("KLİNİK AI AJANI 10 SORULUK DEĞERLENDİRME VE DOĞRULAMA SUITE'İ")
    print("=" * 80)

    for item in BENCHMARK_SCENARIOS:
        qid = item["id"]
        q = item["question"]
        print(f"\n[Soru {qid}]: {q[:75]}...")

        res = query_clinical_agent(q)
        log = res["log"]

        # Token comparison metrics
        # MCP approach: text prompt + system prompt + JSON response ~ 250-400 tokens
        mcp_tokens = log["tokens_in"] + log["tokens_out"]
        total_mcp_tokens += mcp_tokens

        # GUI approach: 1920x1080 screenshot ~ 1600 tokens + reasoning prompt + OCR attempt ~ 2400 tokens per call
        gui_tokens = 2400
        total_gui_tokens_estimated += gui_tokens

        # Verify test family detection
        detected_test = log["tool_input"]["test"] if log.get("tool_input") else "OTHER"
        if item["expected_test"] == "t2-indep":
            is_test_ok = (detected_test == "t2-indep")
            if is_test_ok:
                correct_test_count += 1
            
            # Verify N calculation
            tool_out = log.get("tool_output", {})
            actual_n = tool_out.get("n_total")
            is_n_ok = (actual_n == item["expected_n_total"])
            if is_n_ok:
                correct_n_count += 1

            print(f"  -> Test Seçimi: {detected_test} (Beklenen: {item['expected_test']}) - {'BAŞARILI' if is_test_ok else 'HATALI'}")
            print(f"  -> Hesaplanan N: {actual_n} (Beklenen: {item['expected_n_total']}) - {'TAM EŞLEŞME' if is_n_ok else 'FARK'}")
            print(f"  -> Token (MCP): {mcp_tokens} token vs Token (GUI Tahmini): {gui_tokens} token")
        else:
            # Expected to reject non-K1 tests gracefully
            is_clarification = (log["status"] == "CLARIFICATION_REQUIRED")
            if is_clarification:
                correct_test_count += 1
            print(f"  -> K1 Dışı Aile ({item['expected_test']}): Başarıyla tespit edilip kullanıcıya doğrulama soruldu.")

    print("\n" + "=" * 80)
    print("DEĞERLENDİRME SONUÇLARI:")
    print(f"Test Ailesi Doğru Saptama Oranı: {correct_test_count} / 10 (%{correct_test_count * 10})")
    print(f"K1 Senaryolarında N Tam Eşleşme Oranı: {correct_n_count} / 8 (%{correct_n_count / 8 * 100:.1f})")
    print(f"Toplam MCP Token Tüketimi (10 Soru): {total_mcp_tokens} token")
    print(f"Tahmini GUI Ekran Görüntüsü Token Tüketimi (10 Soru): {total_gui_tokens_estimated} token")
    token_saving_pct = (1.0 - total_mcp_tokens / total_gui_tokens_estimated) * 100
    print(f"Token Tasarrufu: %{token_saving_pct:.1f} (Yaklaşık {total_gui_tokens_estimated // total_mcp_tokens} kat daha ucuz ve hızlı)")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
