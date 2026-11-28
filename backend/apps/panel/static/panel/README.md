# Panel statik dosyaları

- `panel.css`: panele özgü stiller. Yalnızca `tokens.css` değişkenlerini kullanır (PANEL.md §10, §11).
- `tokens.css`: `frontend/src/styles/tokens.css` dosyasının **birebir kopyası**. Elle değiştirilmez.
  Docker imajı yalnızca `backend/` klasöründen derlendiği için dosya burada tutulur. Kaynakla aynı
  olduğu `apps/panel/tests/test_statik.py` ile denetlenir; site renkleri değişince test kırılır.
- `fontlar.css`, `fontlar/`: sitedeki yazı tiplerinin (Source Serif 4, IBM Plex Sans, IBM Plex Mono)
  Latin ve Latin Genişletilmiş alt kümeleri. Lisans: SIL OFL 1.1 (`fontlar/LISANS-*.txt`).

Site renkleri veya yazı tipi sürümleri değişince repo kökünde:

```bash
cp frontend/src/styles/tokens.css backend/apps/panel/static/panel/tokens.css
```

Yazı tipi dosyaları `frontend/node_modules/@fontsource*/files/` altından kopyalanır
(`*-latin-*` ve `*-latin-ext-*`; Plex Sans 400/500/600, Plex Mono 400/500, Source Serif 4 opsz
normal/italic). `fontlar.css` içindeki `unicode-range` değerleri aynı paketlerin CSS dosyalarından
alınmıştır.
