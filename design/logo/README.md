# DİYAK logosu

`DIYAK_*.png` referans görsellerinden ölçülerek çizilen SVG sürümler. Çubuk yüksekliği 10 birim, logo 110×110 birimlik kareye oturur.

| Dosya | Kullanım |
| --- | --- |
| `diyak-logo.svg` | Açık zemin (lacivert çubuklar) |
| `diyak-logo-beyaz.svg` | Koyu zemin (beyaz çubuklar) |
| `diyak-profil.svg` | Sosyal medya profil görseli (lacivert daire) |

Renkler `frontend/src/styles/tokens.css` ile aynıdır: lacivert `#1E2142`, mercan `#E5533A`.
Sitedeki logo `frontend/src/components/Logo.astro` bileşenindedir; çizim değişirse ikisi birlikte güncellenir.
