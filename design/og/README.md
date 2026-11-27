# Open Graph görseli

Sitenin bağlantısı WhatsApp, LinkedIn, X vb. yerlerde paylaşılınca görünen önizleme görseli.

- Kaynak: `og-gorsel.html` (1200×630)
- Çıktı: `frontend/public/og.png` (tüm sayfalar `BaseLayout.astro` içindeki `og:image` ile bunu kullanır)

## Yeniden üretmek

Önce `frontend/` içinde `npm install` (yazı tipleri `node_modules` içinden yüklenir). Sonra repo kökünden:

```bash
firefox --headless --window-size=1200,630 --screenshot frontend/public/og.png "file://$PWD/design/og/og-gorsel.html"
```

Chrome/Chromium ile: `chromium --headless --window-size=1200,630 --screenshot=frontend/public/og.png file://$PWD/design/og/og-gorsel.html`

Renkler `tokens.css` ile aynı tutulur; logo `design/logo/diyak-logo-beyaz.svg` ile aynıdır.
