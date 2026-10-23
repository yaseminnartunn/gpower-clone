# Türkçe Klinik AI Ajanı Değerlendirme Raporu
**Ders:** YZM301 · Yazılım Gerçekleme ve Test
**Modül:** `src/agent.py`

| No | Seviye | Soru | Test Ailesi | Çıkarılan Parametreler | Motor Çıktısı (N) | Harcanan Token |
|---|---|---|---|---|---|---|
| 1 | Kolay | İki bağımsız grupta d=0.5, alpha=0.05 ve power=0.8... | t2-indep | d=0.5, α=0.05, pwr=0.8, tails=2 | 128 | 235 |
| 2 | Kolay | Yeni bir tansiyon ilacı için plasebo kontrolüyle d... | t2-indep | d=0.8, α=0.01, pwr=0.95, tails=2 | 116 | 239 |
| 3 | Kolay | İki bağımsız grupta tek yönlü üstünlük için d=0.4,... | t2-indep | d=0.4, α=0.05, pwr=0.9, tails=1 | 216 | 235 |
| 4 | Orta | İlaç grubunda orta büyüklükte etki bekliyorum, %5 ... | t2-indep | d=0.5, α=0.05, pwr=0.8, tails=2 | 128 | 249 |
| 5 | Orta | İki bağımsız grupta büyük etki büyüklüğü, %5 alfa ... | t2-indep | d=0.8, α=0.05, pwr=0.9, tails=2 | 68 | 245 |
| 6 | Orta | Klinik araştırmamızda küçük etki büyüklüğü bekliyo... | t2-indep | d=0.2, α=0.05, pwr=0.8, tails=2 | 788 | 252 |
| 7 | Zor | Diyabet hastalarında A ve B ilaçlarının HbA1c düşü... | t2-indep | d=0.6, α=0.01, pwr=0.9, tails=2 | 170 | 262 |
| 8 | Zor | Onkoloji çalışmasında yeni tedavi koluna kontrolün... | t2-indep | d=0.5, α=0.05, pwr=0.8, tails=2 | 144 | 270 |
| 9 | Geçersiz | İki bağımsız grupta yeni ilacımı deneyeceğim, %5 a... | t2-indep | d=None, α=0.05, pwr=None, tails=2 | Eksik/Geçersiz (Kullanıcıya Soruldu) | 206 |
| 10 | Geçersiz | Aynı hastaların ameliyat öncesi ve sonrası tansiyo... | t-paired | d=None, α=None, pwr=None, tails=2 | Eksik/Geçersiz (Kullanıcıya Soruldu) | 232 |
