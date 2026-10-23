# HALLUCINATIONS.md — Halüsinasyon Günlüğü

**Ders:** YZM301 · Yazılım Gerçekleme ve Test  
**Sprint:** Teardown Sprint  
**Test Ailesi:** K1 · `t2-indep` (İki Bağımsız Grup t-Testi)  

Bu belge, geliştirme ve tersine mühendislik sürecinde yapay zeka ajanının (veya geliştiricinin) G*Power davranışına ilişkin yaptığı 5 kritik yanlış tahmini (halüsinasyonu), gerçek davranışı ve bunu yakalayan otomatik testleri belgeler.

---

## Halüsinasyon #1
### İddia
Grup dağılım oranı eşit olmadığında ($N_2/N_1 = \text{ratio} \ne 1$), ikinci grup büyüklüğü standart programlama kuralı gereği en yakın tamsayıya yuvarlanır: `n2 = int(round(n1 * ratio))`.

### Gerçek Davranış
G*Power 3.1.9.7, klinik araştırmalarda hedeflenen istatistiksel gücün (1-β) altına düşmemek için örneklemi **her zaman yukarıya doğru tavan fonksiyonu (`ceil`)** ile yuvarlar: `n2 = math.ceil(n1 * ratio)`. Örneğin $r = 1.33$ ve $n_1 = 10$ olduğunda `round` 13 verirken, G*Power kesin olarak 14 hasta atar.

### Nasıl Fark Edildi
Eşit olmayan oranlara sahip kâhin vektörleri koşturulduğunda `n2` değerlerinin G*Power'a göre 1 eksik çıktığı ve gerçek gücün hedefin binde bir altında kaldığı fark edildi.

### Yakalayan Test
`tests/test_boundary.py::test_d_unequal_allocation_ratio` ve `tests/test_differential_oracle.py::test_oracle_vector_match[row10]`

---

## Halüsinasyon #2
### İddia
Kullanıcı hedef gücü (power) alfa hatasından küçük veya ona eşit girdiğinde (örn. $\alpha = 0.05, \text{power} = 0.04$), motor yine de matematiksel formülü çalıştırıp sıfıra yakın çok küçük bir $N$ üretmelidir.

### Gerçek Davranış
G*Power istatistiksel olarak $\text{Power} \le \alpha$ durumunu anlamsız (inconsistent) kabul eder; çünkü rastgele tahmin etseniz bile ret olasılığı $\alpha$'dır. Bu durumda hesaplama yapılmaz, `INCONSISTENT` kodlu hata fırlatılır ve çıkış kodu `2` olur.

### Nasıl Fark Edildi
Arayüze $\alpha=0.05, \text{power}=0.04$ girildiğinde G*Power'ın hesaplama yapmayı reddettiği ve hata uyarısı verdiği gözlemlendi.

### Yakalayan Test
`tests/test_boundary.py::test_c_power_less_than_or_equal_to_alpha`

---

## Halüsinasyon #3
### İddia
İki bağımsız grup t-testinde heteroskedastisite (varyansların eşit olmaması) durumuna karşı serbestlik derecesi varsayılan olarak Welch-Satterthwaite düzeltmesiyle kesirli hesaplanır.

### Gerçek Davranış
G*Power 3.1.9.7 `t2-indep` testinde homoskedastisite (eşit varyans) varsayımı sabittir. Serbestlik derecesi kesirsiz, tam tamsayı olarak doğrudan $df = n_1 + n_2 - 2$ formülü ile hesaplanır. Binary incelemesinde de doğrudan `SUB EAX, 0x2` komutu tespit edilmiştir.

### Nasıl Fark Edildi
R `pwr.t.test` ve Python `statsmodels` kütüphanelerinin kesirli serbestlik derecesi verebildiği, ancak G*Power arayüzünün ve protokolünün her zaman kesin tamsayı $n_1 + n_2 - 2$ bastığı doğrulandı.

### Yakalayan Test
`tests/test_boundary.py::test_g_reference_vectors_exact` ve `tests/test_contract.py::test_cli_success_single_line_json`

---

## Halüsinasyon #4
### İddia
Etki büyüklüğü çok küçük olduğunda ($d = 0.001$ veya $d = 0.01$), noncentral t dağılımı yakınsamayacağı için motor çöker veya `NO_SOLUTION` hatası vermelidir.

### Gerçek Davranış
G*Power ve doğru yapılandırılmış noncentral t kümülatif dağılım fonksiyonu $d = 0.01$ gibi çok küçük etkilerde de kararlı şekilde çalışır; yüz binlerce kişilik devasa örneklem büyüklüğü ($N > 100,000$) üretir. Sayısal taşma veya çökme yaşanmaz.

### Nasıl Fark Edildi
Sınır değer testlerinde $d = 0.01$ verildiğinde motorun çökmeden monoton şekilde artan devasa $N$ değerini başarıyla bulduğu kanıtlandı.

### Yakalayan Test
`tests/test_boundary.py::test_a_very_small_effect_size`

---

## Halüsinasyon #5
### İddia
Çift yönlü t-testinde ($\text{tails} = 2$) $\delta > 0$ iken sol kuyruk alanı sıfıra çok yakın olduğundan güç hesabında sol kuyruk integrali $F(-t_{\text{crit}})$ ihmal edilebilir, sadece üst kuyruk $1 - F(t_{\text{crit}})$ yeterlidir.

### Gerçek Davranış
G*Power, çift yönlü hipotezde her iki ret bölgesini de toplar:  
$$\text{Power} = 1 - F(t_{\text{crit}}; df, \delta) + F(-t_{\text{crit}}; df, \delta)$$  
Büyük alfa ($\alpha = 0.10$) ve küçük etki ($d = 0.20$) koşullarında bu ihmal $1.4 \times 10^{-4}$ hata üretir ve sözleşmedeki $10^{-6}$ toleransını bozar.

### Nasıl Fark Edildi
Kâhin karşılaştırmasında 7 ondalık basamaklı actual power değeriyle 4. basamakta uyuşmazlık çıkması sonucu fark edildi. Sol kuyruk integrali eklenerek tam uyum sağlandı.

### Yakalayan Test
`tests/test_stress_500.py::test_500_grid_search_stress` ve `tests/test_engine.py::test_a_priori_public`
