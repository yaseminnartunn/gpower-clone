# Oturum 1 İlk Prompt'u — Tersine Mühendislik ve İnceleme

**Oturum Amacı:** G*Power 3.1.9.7 binary davranışını, makale formüllerini ve `CONTRACT.md` sözleşmesini inceleyerek davranış kurallarını kurtarmak, `SPEC.md` ve `LEDGER.md` dokümanlarını oluşturmak. (Bu oturumda kod yazılmaz; yalnızca spesifikasyon ve kanıt üretilir.)

---

## İlk Prompt (System Prompt / Görev Başlatıcı)

```markdown
G*Power 3.1.9.7 (Windows) yazılımının K1 test ailesini (t tests - Means: Difference between two independent means, t2-indep) tersine mühendislik yaklaşımıyla inceleyeceğiz.

Kapsam ve Kurallar:
1. Temiz oda kuralı gereğince bu oturumda kesinlikle son ürün kodu üretilmeyecektir. Yalnızca davranış analizi, matematiksel modeller ve kabul kriterleri çıkarılacaktır.
2. İncelenecek modlar: a-priori (örneklem büyüklüğü), post-hoc (gerçekleşen güç), compromise, criterion ve sensitivity.
3. Kılavuzda olmayan gizli davranışları ortaya çıkarın:
   - Örneklem büyüklüğü N nasıl aranıyor? İterasyon durma koşulu nedir?
   - Eşit olmayan grup dağılımında (ratio = N2/N1) n2 nasıl yuvarlanıyor (round mu, ceil mi)?
   - Çift yönlü t testinde alfa ret bölgesi ve güç integrali nasıl hesaplanıyor?
   - Giriş sınırları ve hata durumlarında sistem nasıl tepki veriyor?
4. Çıktı olarak:
   - Tüm iddiaların [DOK], [REA] ve [AJAN] etiketleriyle kayıt altına alındığı LEDGER.md kanıt defterini,
   - Gherkin formatında (Given/When/Then) kabul kriterlerini içeren SPEC.md belgesini oluşturun.

REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Başlayalım.
```
