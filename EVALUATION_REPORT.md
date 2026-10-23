# EVALUATION_REPORT.md — Klinik AI Ajanı ve Token Ekonomisi Değerlendirme Raporu

**Ders:** YZM301 · Yazılım Gerçekleme ve Test  
**Sprint:** Teardown Sprint  
**Test Ailesi:** K1 · `t2-indep`  

Bu rapor, klinik araştırma sorularını yanıtlayan AI Ajanının 10 soruluk benchmark performansını ve GUI (ekran görüntüsü) ile MCP (yapılandırılmış JSON) mimarileri arasındaki token/maliyet karşılaştırmasını sunar.

---

## 1. 10 Klinik Soru Benchmark Sonuçları

Tüm sorular kurgusal klinik araştırma senaryoları olup hiçbir gerçek hasta verisi içermemektedir. Testler `src/evaluation_suite.py` ile otomatik koşturulmuş ve `logs/agent_calls.jsonl` dosyasına kaydedilmiştir.

| No | Klinik Senaryo Konusu | Hedef Test | Çıkarılan Parametreler | Beklenen N | Hesaplanan N | Test Doğruluğu | N Eşleşmesi |
|:---:|---|:---:|---|:---:|:---:|:---:|:---:|
| **1** | Antihipertansif vs Plasebo (Tek Yönlü Üstünlük) | `t2-indep` | tails=1, d=0.5, α=0.05, 1-β=0.95, r=1.0 | 176 | 176 | %100 | **TAM** |
| **2** | Diyabetik İnsülin Duyarlılaştırıcı (Sıkı Alfa) | `t2-indep` | tails=2, d=0.6, α=0.01, 1-β=0.90, r=1.0 | 170 | 170 | %100 | **TAM** |
| **3** | Onkoloji İmmünoterapi (1:2 Dağılım Oranı) | `t2-indep` | tails=2, d=0.5, α=0.05, 1-β=0.80, r=2.0 | 144 | 144 | %100 | **TAM** |
| **4** | Post-op Analjezik Ağrı Skoru (Büyük Etki) | `t2-indep` | tails=2, d=0.8, α=0.05, 1-β=0.80, r=1.0 | 52 | 52 | %100 | **TAM** |
| **5** | Sepsis Protokolü (Küçük Klinik Fark) | `t2-indep` | tails=2, d=0.2, α=0.05, 1-β=0.80, r=1.0 | 788 | 788 | %100 | **TAM** |
| **6** | Migren Profilaksisi (Tek Yönlü Hipotez) | `t2-indep` | tails=1, d=0.4, α=0.05, 1-β=0.90, r=1.0 | 216 | 216 | %100 | **TAM** |
| **7** | Ameliyat Öncesi-Sonrası Tansiyon | `t-paired` | tails=2, d=0.5, α=0.05, 1-β=0.80 | — | *Açıklama İstendi* | %100 | **BAŞARILI** |
| **8** | 3 Kol Kemoterapi Yaşam Kalitesi | `anova-oneway` | tails=2, f=0.25, α=0.05, 1-β=0.80 | — | *Açıklama İstendi* | %100 | **BAŞARILI** |
| **9** | Kardiyoloji Stent Karşılaştırması | `t2-indep` | tails=1, d=0.35, α=0.05, 1-β=0.95, r=1.0 | 356 | 356 | %100 | **TAM** |
| **10** | Covid-19 Rehabilitasyon Yürüme Testi | `t2-indep` | tails=2, d=0.5, α=0.05, 1-β=0.90, r=1.0 | 172 | 172 | %100 | **TAM** |

### Performans Metrikleri:
- **Test Ailesi Doğru Saptama Oranı:** 10 / 10 (**%100.0**)
- **K1 Ailesi N Tam Eşleşme Oranı:** 8 / 8 (**%100.0**)
- **Kapsam Dışı Aileleri Ayırt Etme ve Doğrulama İsteme:** 2 / 2 (**%100.0**)

---

## 2. Token Ekonomisi ve Maliyet Karşılaştırması (GUI vs. MCP)

"Her arayüz bir maliyet transferidir: ya ajan her çağrıda öder, ya sistem bir kez."

| Metrik | GUI Yaklaşımı (Ekran Görüntüsü ile) | MCP Sunucusu Yaklaşımı (Yapılandırılmış Çağrı) | Kazanç / Tasarruf |
|---|:---:|:---:|:---:|
| **Girdi Temsili** | 1920×1080 ekran görüntüsü (~1,600 token) + OCR/VLM reasoning prompt (~800 token) | Doğal dil soru + MCP aracı çağrısı JSON (~320 token) | **~%83.3 Azalma** |
| **Ortalama İstek Başına Token** | **~2,400 token** | **~401 token** | **5.98 kat daha az token** |
| **10 Soru Toplam Token** | **24,000 token** | **4,016 token** | **19,984 token net tasarruf** |
| **Yanıt Süresi (Ortalama Gecikme)** | 4.5 – 7.0 saniye (Görsel işleme & UI tarama) | 0.2 – 0.5 saniye (Deterministik CLI/MCP çağrısı) | **~12 kat daha hızlı** |
| **Doğruluk ve Güvenilirlik** | Görsel piksel okuma hatalarına açık | Deterministik Scipy/C motoru hassasiyetinde | **Sıfır algısal hata** |
| **10,000 Çağrıda Tahmini Maliyet** | ~$36.00 | ~$6.02 | **~$30.00 tasarruf** |

### Çıkarım:
Ekran görüntüsü temelli ajanlar her hesaplama için yüksek görsel token ve gecikme bedeli öderken; arkasına ince bir MCP katmanı alan mimarilerde mühendis sistemi bir kez optimize eder, yapay zeka ise her kullanımda hız ve maliyet kazanır.
