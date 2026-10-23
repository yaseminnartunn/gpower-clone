# G*Power 3.1.9.7 Kâhin Ekran Görüntüleri ve Vektör Kataloğu

**Ders:** YZM301 · Yazılım Gerçekleme ve Test  
**Konu:** K1 · İki Bağımsız Ortalama t-Testi (`t2-indep`)  
**Kâhin Kaynağı:** G*Power 3.1.9.7 (Windows) GUI Arayüzü  

Bu belge, `oracle/oracle_vectors.csv` dosyasında yer alan 33 referans vektörünün G*Power 3.1.9.7 arayüzünden toplanma protokolünü, ekran düzenini ve doğrulanma sürecini açıklar.

---

## 1. G*Power Test Ailesi Yapılandırması

G*Power arayüzünde kullanılan ayarlar:
- **Test family:** `t tests`
- **Statistical test:** `Means: Difference between two independent means (two groups)`
- **Type of power analysis:**
  - `A priori: Compute required sample size - given α, power, and effect size` (Vektör 01-28)
  - `Post hoc: Compute achieved power - given α, sample size, and effect size` (Vektör 29-33)

---

## 2. Temsilî Ekran Görüntüsü Referans Haritası

### Vektör ORACLE-04 (Sözleşme Referans Vektörü)
* **Girdi Parametreleri:**
  - `Tail(s):` 1 (One-tailed)
  - `Effect size d:` 0.5
  - `α err prob:` 0.05
  - `Power (1-β err prob):` 0.95
  - `Allocation ratio N2/N1:` 1
* **G*Power Çıktı Değerleri:**
  - `Noncentrality parameter δ:` `3.3166248`
  - `Critical t:` `1.6536580`
  - `Df:` `174`
  - `Sample size group 1:` `88`
  - `Sample size group 2:` `88`
  - `Total sample size:` `176`
  - `Actual power:` `0.9514254`

### Vektör ORACLE-12 (Eşit Olmayan Oran - 1:2 Klinik Çalışma)
* **Girdi Parametreleri:**
  - `Tail(s):` 2
  - `Effect size d:` 0.5
  - `α err prob:` 0.05
  - `Power (1-β err prob):` 0.80
  - `Allocation ratio N2/N1:` 2.0
* **G*Power Çıktı Değerleri:**
  - `Sample size group 1 (n1):` `48`
  - `Sample size group 2 (n2):` `96`
  - `Total sample size (N):` `144`
  - `Critical t:` `1.976811`
  - `Actual power:` `0.800889`

---

## 3. Doğrulama Protokolü

Her vektör şu 3 aşamalı diferansiyel kontrolden geçirilmiştir:
1. **G*Power GUI Protokol Penceresi (Window -> Protocol of power analyses):** Hesaplama sonrası protokol kaydına düşen değerler 7 ondalık basamak hassasiyetiyle kopyalanmıştır.
2. **Kütüphane Karşılaştırması (`pwr.t.test` / `scipy`):** Kesirli N ile tamsayı $N$ arasındaki yukarı yuvarlama tavan etkisi (`ceil`) teyit edilmiştir.
3. **`tests/test_differential_oracle.py` Koşusu:** Yeniden yazılan motorun çıktıları ile CSV'deki değerler karşılaştırılmış, $N$ değerlerinde **%100 TAM EŞLEŞME** ve ondalık değerlerde **$\le 10^{-6}$** hata sağlanmıştır.
