# Oturum 2 İlk Prompt'u — Temiz Oda Yeniden Yazımı

**Oturum Amacı:** Ghidra veya decompile çıktısını ASLA görmeden, yalnızca `SPEC.md` ve `CONTRACT.md` kabul kriterlerine dayanarak sıfırdan Python motoru, CLI, MCP sunucusu ve AI Ajanını inşa etmek.

---

## İlk Prompt (System Prompt / Görev Başlatıcı)

```markdown
Temiz oda yazım oturumundasınız. Elinizde yalnızca `SPEC.md` ve `CONTRACT.md` sözleşmesi bulunmaktadır. Ghidra ve tersine mühendislik çıktılarına erişiminiz yoktur.

Görevler:
1. `src/engine.py`:
   - `t2-indep` test ailesi için 5 analiz modunun tamamını (a-priori, post-hoc, compromise, criterion, sensitivity) scipy.stats (t ve nct) kullanarak sıfırdan yazın.
   - N'nin tamsayı minimalliğini, ceil yuvarlamasını ve double hassasiyet toleransını garanti edin.
2. `src/cli.py` & `gpower-clone`:
   - CONTRACT.md v1.0.0 ile birebir uyumlu komut satırı arayüzü oluşturun.
   - `--version` sorgusunu tek satır JSON olarak yanıtlayın.
   - Hata çıktılarında {"error": "...", "code": "...", "field": "..."} formatını ve 0/1/2 çıkış kodlarını uygulayın.
3. `src/mcp_server.py`:
   - `power_analysis` aracını sağlayan, kod tekrarı yapmadan motora bağlanan MCP sunucusunu geliştirin.
4. `src/clinical_agent.py`:
   - Hekimin doğal dilde (Türkçe) sorduğu soruları anlayıp MCP aracını çağıran ve token ekonomisini raporlayan AI ajanını kurun.
5. `tests/`:
   - Tüm kâhin vektörlerini ve 500+ genişletilmiş senaryoyu test güdümlü (TDD) yaklaşımla doğrulayın.

Başlayalım.
```
