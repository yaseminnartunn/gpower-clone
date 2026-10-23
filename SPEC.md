# SPEC.md — `gpower-clone` Kabul Kriterleri Spesifikasyonu

**Ders:** YZM301 · Yazılım Gerçekleme ve Test  
**Sprint:** Teardown Sprint  
**Test Ailesi:** `t2-indep` (İki Bağımsız Örneklem t-Testi)  
**Format:** Gherkin (Cucumber / Behave uyumlu)  
**Sözleşme:** `CONTRACT.md` v1.0.0  

---

## Özellik 1: Sistem ve Sürüm Sorgusu

  Gereksinim: CLI aracı sözleşme sürümünü ve motor bilgisini standart JSON olarak sunmalıdır.

  Senaryo: Sürüm bilgisi sorgulama
    Diyelim ki kullanıcı terminaldedir
    Eğer kullanıcı `gpower-clone --version` komutunu çalıştırırsa
    O zaman çıkış kodu `0` olmalıdır
    Ve `stdout` çıktısı tek satır JSON olarak `contract_version`, `name` ve `engine` alanlarını içermelidir:
      """json
      {"contract_version":"1.0.0","name":"YZM301-Teardown-Team-K1","engine":"Python 3.10.5 (scipy-powered)"}
      """

---

## Özellik 2: A-Priori Örneklem Büyüklüğü Analizi (`a-priori`)

  Gereksinim: Verilen alfa, hedef güç, etki büyüklüğü ve oran parametreleriyle minimal örneklem büyüklüğü hesaplanmalıdır.

  Senaryo: Standart tek yönlü klinik çalışma (Açık Vektör 1)
    Diyelim ki `tails` = 1
    Ve `d` = 0.5
    Ve `alpha` = 0.05
    Ve `power` = 0.95
    Ve `ratio` = 1.0
    Eğer `gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1` çalıştırılırsa
    O zaman çıkış kodu `0` olmalıdır
    Ve `stdout` tek satır JSON olmalıdır
    Ve `n1` tam sayısı 88 olmalıdır
    Ve `n2` tam sayısı 88 olmalıdır
    Ve `n_total` tam sayısı 176 olmalıdır
    Ve `df` tam sayısı 174 olmalıdır
    Ve `critical_t` değeri 1.6536580 ± 1e-6 olmalıdır
    Ve `ncp` değeri 3.3166248 ± 1e-6 olmalıdır
    Ve `actual_power` değeri 0.9514254 ± 1e-6 olmalıdır

  Senaryo: Çift yönlü ve eşit olmayan grup oranı (2:1 dağılım)
    Diyelim ki `tails` = 2, `d` = 0.5, `alpha` = 0.05, `power` = 0.80, `ratio` = 2.0
    Eğer a-priori analizi koşturulursa
    O zaman `n1` = 48, `n2` = 96 ve `n_total` = 144 olmalıdır
    Ve `actual_power` >= 0.80 olmalıdır
    Ve `n2` tamsayısı `ceil(n1 * ratio)` kuralına tam uymalıdır

---

## Özellik 3: Post-Hoc Gerçekleşen Güç Analizi (`post-hoc`)

  Gereksinim: Belirli bir hasta sayısına ulaşmış tamamlanan çalışmada test gücü hesaplanmalıdır.

  Senaryo: Ulaşılan test gücünün doğrulanması (Açık Vektör 2)
    Diyelim ki `tails` = 1, `d` = 0.5, `alpha` = 0.05, `n1` = 88, `n2` = 88
    Eğer `gpower-clone --test t2-indep --mode post-hoc --tails 1 --d 0.5 --alpha 0.05 --n1 88 --n2 88` çalıştırılırsa
    O zaman çıkış kodu `0` olmalıdır
    Ve `df` = 174 olmalıdır
    Ve `power` = 0.9514254 ± 1e-6 olmalıdır

---

## Özellik 4: Uzlaşma Analizi (`compromise`)

  Gereksinim: Beta/Alfa hata riski oranına göre örtük alfa ve güç değerleri çözülmelidir.

  Senaryo: Eşit hata riski (Beta/Alpha = 1.0)
    Diyelim ki `tails` = 1, `d` = 0.5, `beta_alpha_ratio` = 1.0, `n1` = 88, `n2` = 88
    Eğer compromise analizi koşturulursa
    O zaman `alpha` = 0.0492887 ± 1e-6 olmalıdır
    Ve `beta` = 0.0492887 ± 1e-6 olmalıdır
    Ve `power` = 0.9507113 ± 1e-6 olmalıdır

---

## Özellik 5: Kriter Analizi (`criterion`)

  Gereksinim: Sabit örneklem ve güç hedefi için gereken anlamlılık düzeyi (alfa) çözülmelidir.

  Senaryo: Güç 0.95 için gereken alfayı hesaplama
    Diyelim ki `tails` = 1, `d` = 0.5, `power` = 0.95, `n1` = 88, `n2` = 88
    Eğer criterion analizi koşturulursa
    O zaman `alpha` = 0.0485965 ± 1e-6 olmalıdır
    Ve `critical_t` = 1.6676050 ± 1e-6 olmalıdır

---

## Özellik 6: Duyarlılık Analizi (`sensitivity`)

  Gereksinim: Mevcut örneklem ve güç kısıtında saptanabilir en küçük Cohen's d çözülmelidir.

  Senaryo: Saptanabilir etki büyüklüğü çözümü
    Diyelim ki `tails` = 1, `alpha` = 0.05, `power` = 0.95, `n1` = 88, `n2` = 88
    Eğer sensitivity analizi koşturulursa
    O zaman `d` = 0.4978840 ± 1e-6 olmalıdır
    Ve `ncp` = 3.3025887 ± 1e-6 olmalıdır

---

## Özellik 7: Giriş Doğrulama ve Hata Yönetimi

  Senaryo: Hedef güç alfadan küçük veya eşit olamaz
    Diyelim ki kullanıcı `alpha` = 0.05 ve `power` = 0.04 vermiştir
    Eğer komut çalıştırılırsa
    O zaman çıkış kodu `2` olmalıdır
    Ve çıktı tek satır JSON olarak `{"error":"Power must be greater than alpha","code":"INCONSISTENT","field":"power"}` içermelidir

  Senaryo: Mod için eksik parametre verilmesi
    Diyelim ki `a-priori` çağrısında `--ratio` parametresi unutulmuştur
    Eğer komut çalıştırılırsa
    O zaman çıkış kodu `2` olmalıdır
    Ve `code` alanı `"MISSING_PARAM"` olmalıdır

  Senaryo: Tanınmayan veya mod dışı parametre verilmesi
    Diyelim ki `post-hoc` çağrısına `--power` verilmiştir
    Eğer komut çalıştırılırsa
    O zaman çıkış kodu `2` olmalıdır
    Ve `code` alanı `"UNKNOWN_PARAM"` olmalıdır

  Senaryo: Aralık dışı girdi (Geçersiz kuyruk sayısı)
    Diyelim ki `--tails 3` parametresi verilmiştir
    Eğer komut çalıştırılırsa
    O zaman çıkış kodu `2` olmalıdır
    Ve `code` alanı `"OUT_OF_RANGE"` olmalıdır
