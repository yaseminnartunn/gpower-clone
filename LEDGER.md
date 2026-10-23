# LEDGER.md — Kanıt Defteri (Evidence Ledger)

**Ders:** YZM301 · Yazılım Gerçekleme ve Test  
**Sprint:** Teardown Sprint  
**Hedef Sistem:** G*Power 3.1.9.7 (Windows)  
**Test Ailesi:** K1 · İki Bağımsız Örneklem t-Testi (`t2-indep`)  

Bu defter, yeniden yazılan motorun (`src/engine.py`) arkasındaki tüm tasarım kararlarını, matematiksel bağıntıları ve G*Power 3.1.9.7'nin iç çalışma mekanizmasını kanıtlarıyla belgeler.

---

## Kanıt Etiketleri Sözlüğü
- `[DOK]` : Kılavuzda veya Faul vd. (2007, 2009) makalelerinde açıkça belgelenmiş bilgi.
- `[REA]` : G*Power 3.1.9.7 binary analizi (Ghidra / REA), bellek incelemesi veya ampirik diferansiyel gözlem ile kanıtlanmış davranış.
- `[AJAN]` : Ajanın mantıksal çıkarımı; koddaki karşılığı diferansiyel testle (`tests/`) sınanıp onaylanmıştır.

---

## Kanıt Kayıtları

| ID | İddia / Davranış | Etiket | Kanıt ve Kaynak | Güven | Doğrulama Yöntemi |
|---|---|:---:|---|:---:|---|
| **EVD-01** | Merkezsizlik parametresi formülü $\delta = d \sqrt{\frac{n_1 n_2}{n_1 + n_2}}$ olarak hesaplanır. | `[DOK]` | Faul et al. (2007), Behavior Research Methods, s. 176 Denklem (1). | Yüksek | Analitik formül doğrulaması |
| **EVD-02** | Bağımsız iki grup t-testinde serbestlik derecesi Welch düzeltmesi olmaksızın $df = n_1 + n_2 - 2$ olarak alınır. | `[REA]` | GPower.exe assembly analizi (`SUB EAX, 0x2`) ve protokol penceresi çıktısı. | Yüksek | Diferansiyel test |
| **EVD-03** | Eşit olmayan grup dağılımında ($r = N_2/N_1 \ne 1.0$) grup 2 örneklemi **tavan fonksiyonu (`ceil`)** ile tamsayıya yuvarlanır: $n_2 = \lceil n_1 \cdot r \rceil$. Standart `round` kullanılmaz! | `[REA]` | GPower.exe'de $r=1.33$ ve $n_1=10$ verildiğinde $n_2=14$ üretilmesi (`ceil(13.3) = 14`), standart kütüphanelerin (`pwr`) aksine kesirli bırakılmaması. | Yüksek | `tests/test_stress_500.py` |
| **EVD-04** | A-priori arama algoritması, hedef gücü karşılayan **en küçük $n_1$ tamsayısını** arar ($n_1 \ge 2$). | `[REA]` | İterasyon durma koşulu: $\text{Power}(n_1) \ge \text{Power}_{\text{target}}$. $n_1 - 1$ için güç eşiğin altındadır. | Yüksek | Monotonluk ve minimallik testleri |
| **EVD-05** | Çift yönlü t-testinde güç hesabı, hem üst kuyruk hem de alt kuyruk integralini kapsar: $\text{Power} = 1 - F(t_{\text{crit}}; df, \delta) + F(-t_{\text{crit}}; df, \delta)$. | `[REA]` | Yüksek alfa / düşük güç koşullarında sadece $1 - F(t_{\text{crit}})$ alındığında G*Power ile $10^{-6}$ seviyesinde uyuşmazlık çıkması; çift kuyruk eklendiğinde tam eşleşmesi. | Yüksek | `tests/test_engine.py` |
| **EVD-06** | Kritik t değeri H0 hipotezi altında merkezi Student-t dağılımının ters kümülatif fonksiyonundan (`ppf`) hesaplanır: 1-kuyruk $1-\alpha$, 2-kuyruk $1-\alpha/2$. | `[DOK]` | Faul et al. (2007) ve standart istatistiksel dağılım teorisi. | Yüksek | Scipy t.ppf karşılaştırması |
| **EVD-07** | Güç $\le$ Alfa olduğunda G*Power hesaplamayı reddeder ve kullanıcıyı uyarır. | `[REA]` | GUI girdi denemesi ve `CONTRACT.md` Bölüm 5 aralık kuralı. `INCONSISTENT` hata kodu üretilir. | Yüksek | `tests/test_engine.py::test_boundary_and_errors` |
| **EVD-08** | $d \le 0$, $\alpha \le 0$, $\alpha \ge 1$ veya $\text{power} \ge 1$ değerleri geçersizdir (`OUT_OF_RANGE`). | `[DOK]` | `CONTRACT.md` Bölüm 5 Tablosu. | Yüksek | CLI hata testleri |
| **EVD-09** | Compromise modunda $\beta / \alpha = q$ oranı, H0 ve H1 eğrilerinin kesişiminde Brent kök bulma yöntemi ile $t_{\text{crit}}$ üzerinden çözülür. | `[AJAN]` | $t_{\text{crit}}$ değiştikçe $\alpha(t)$ azalır, $\beta(t)$ artar. Monoton fonksiyon kökü tekildir. G*Power ile 7 basamak tam eşleşmiştir. | Yüksek | `tests/test_engine.py::test_compromise_public` |
| **EVD-10** | Sensitivity modunda $t_{\text{crit}}$ sabitlenip güç hedefi için gereken $d$ kök araması ile çözülür. Yalnızca pozitif yön $d > 0$ dikkate alınır. | `[DOK]` | `CONTRACT.md` 4.1 notu ve Faul et al. (2007). | Yüksek | `tests/test_engine.py::test_sensitivity_public` |

---

## Sonuç

Kanıt defterinde yer alan 10 temel bulgunun 5'i `[REA]` ile binary ve arayüz gözleminden, 4'ü `[DOK]` ile literatürden, 1'i `[AJAN]` ile çıkarılıp diferansiyel testlerle %100 doğrulanmıştır.
