# DİYAK Web Sitesi

Fırat Üniversitesi **Doğal Dil İşleme ve Yapay Zekâ Araştırmaları Topluluğu (DİYAK)** web sitesinin kaynak kodu.

Site şu an **Faz 1**'de: içerik Markdown/JSON dosyalarında duran, statik olarak derlenen bir Astro sitesi. Üyelik, proje başvurusu ve dosya yükleme gibi dinamik özellikler **Faz 2**'de Django tabanlı bir backend ile gelecek. Ayrıntılar: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Hızlı başlangıç

Gereksinim: **Node.js 22.22 veya üstü** (sürüm `.nvmrc` dosyasında).

```bash
cd frontend
npm install
npm run dev        # http://localhost:4321
```

| Komut | Ne yapar |
| --- | --- |
| `npm run dev` | Geliştirme sunucusunu başlatır, değişiklikleri anında yansıtır |
| `npm run build` | Yayına hazır statik siteyi `frontend/dist/` klasörüne üretir |
| `npm run preview` | Üretilen siteyi yerelde açar |
| `npm run check` | Tip ve şablon hatalarını denetler |
| `npm run format` | Kodu Prettier ile biçimlendirir |

## Klasör yapısı

```
diyak-web/
├── AGENTS.md            Kod yazan agent'lar (Claude Code vb.) için kurallar
├── CLAUDE.md            Claude Code'u AGENTS.md'ye yönlendirir
├── STATUS.md            Şu an yapılan, sıradaki ve bekleyen işler
├── CONTRIBUTING.md      Çalışma düzeni: branch, commit, PR, birleştirme
├── docs/
│   ├── ARCHITECTURE.md  Mimari ve teknoloji seçimleri (Faz 1 ve Faz 2)
│   ├── DECISIONS.md     Alınan kararlar ve gerekçeleri
│   ├── DESIGN.md        Tasarım sistemi: renkler, yazı tipleri, bileşenler
│   ├── OPERASYON.md     Veritabanı, yedekleme, yayın ve kurtarma (Faz 2)
│   ├── PANEL.md         Yönetim paneli ve formlar tasarımı (Faz 2)
│   └── CONTENT.md       Kod bilmeden içerik ekleme rehberi
├── design/
│   └── prototip.html    Onaylanan tasarımın tek dosyalık prototipi (referans)
├── frontend/            Astro sitesi (Faz 1)
├── backend/             Django API (Faz 2, henüz başlamadı)
└── .github/             PR ve issue şablonları
```

## Katkı

Çalışma düzeni için [CONTRIBUTING.md](CONTRIBUTING.md), içerik eklemek için [docs/CONTENT.md](docs/CONTENT.md) dosyasına bakın. Agent ile çalışıyorsanız agent önce [AGENTS.md](AGENTS.md) ve [STATUS.md](STATUS.md) dosyalarını okumalı.

## Kurumsal bilgi

Topluluk, Fırat Üniversitesi Sağlık Kültür ve Spor Daire Başkanlığı Öğrenci Toplulukları Birimi'ne bağlıdır. Sitede Fırat Üniversitesi ve SKS adının ve/veya logosunun bulunması tüzük gereğidir (Madde 9/7).
