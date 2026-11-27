# Mimari

Bu belge sitenin teknik yapısını ve teknoloji seçimlerini anlatır. Kararların gerekçeleri [DECISIONS.md](DECISIONS.md) dosyasında.

## Hedefler

1. **Dayanıklılık:** Her yıl değişen yönetimlere rağmen site yaşamaya devam etmeli. Kod sıkıcı, yaygın ve iyi belgelenmiş teknolojilerle yazılır, yeni gelen biri kısa sürede devralabilir.
2. **Ölçeklenebilirlik:** Topluluk ulusal ölçeğe büyüse de (on binlerce kullanıcı, başvuru dönemlerinde birkaç yüz eşzamanlı istek) mimari değişmeden büyüyebilmeli.
3. **Güvenlik ve KVKK:** Üye ve başvuru verisi kişisel veridir. Yetkisiz erişime ve veri sızıntısına karşı baştan tasarlanır.
4. **Agent dostu:** Kodun büyük kısmı Claude Code gibi agent'larla yazılacak. Bu yüzden yaygın framework'ler, açık klasör yapısı, güncel dokümanlar ve otomatik denetimler tercih edilir.

"Ölçeklenebilir" burada mikroservis veya Kubernetes demek değil. Bu ölçekte tek bir PostgreSQL ve birkaç uygulama sunucusu yeterli. Asıl kural, uygulamanın **durumsuz (stateless)** olması: oturumlar Redis'te veya veritabanında, dosyalar object storage'da tutulur. Böylece büyüdükçe aynı container'dan bir tane daha açmak yeterli olur.

## Genel görünüm

```
                 ┌───────────────────────────────┐
  Ziyaretçi ───▶ │  CDN (Cloudflare Pages)        │   Faz 1: tüm site buradan sunulur
                 │  Astro'nun ürettiği statik HTML│
                 └──────────────┬────────────────┘
                                │ Faz 2: yalnızca dinamik sayfalar
                                ▼
                 ┌───────────────────────────────┐
                 │  Django API  (+ Django Admin)  │──▶ PostgreSQL
                 │  durumsuz, birden çok kopya    │──▶ Redis (oturum, kuyruk)
                 └──────────────┬────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
     Object storage       Arka plan işleri     E-posta servisi
     (S3 uyumlu, private) (Celery/RQ: virüs
                           taraması, e-posta)
```

## Faz 1: Statik site (şu an)

| Katman | Seçim |
| --- | --- |
| Framework | **Astro 7**, `output: 'static'` |
| Dil | TypeScript (strict) |
| Stil | Sade CSS + tasarım değişkenleri (`src/styles/tokens.css`). UI kit yok |
| Yazı tipleri | `@fontsource` paketleriyle kendi sunucumuzdan (Google Fonts'a istek yok) |
| İçerik | Astro content collections: Markdown (`src/content/gundem/`) ve JSON (`src/data/`) |
| JavaScript | Yalnızca küçük, bağımsız betikler: mobil menü, kaydırınca gizlenen üst menü, gündem filtresi |
| Yayın | Cloudflare Pages: main'e birleşen her commit otomatik yayına çıkar, her PR için önizleme linki üretilir |
| Alan adı | Bilgi İşlem'den alt alan adı (ör. `diyak.firat.edu.tr`) |
| Paket yöneticisi | npm, `package-lock.json` repoda |
| Node | 22 LTS (`.nvmrc`) |

### Klasör yapısı

```
frontend/
├── astro.config.mjs
├── public/                 Olduğu gibi kopyalanan dosyalar
│   ├── favicon.svg
│   ├── belgeler/           Üye kayıt formu, tüzük (PDF)
│   ├── ekip/               Ekip fotoğrafları
│   └── logolar/            FÜ ve SKS logoları
└── src/
    ├── config/site.ts      Site adı, iletişim, sosyal bağlantılar, menü
    ├── content.config.ts   İçerik koleksiyonlarının şemaları
    ├── content/gundem/     Gündem gönderileri (her biri bir .md dosyası)
    ├── data/               ekip.json, kaynaklar.json
    ├── lib/                Yardımcı fonksiyonlar (tarih biçimi, ekip şeması)
    ├── styles/             tokens.css, global.css
    ├── layouts/            BaseLayout.astro
    ├── components/         Header, Footer, Logo ve bölüm bileşenleri
    └── pages/              index, ekip, gundem/, 404
```

### Neden backend olmadan başlıyoruz

Faz 1'deki her şey (gündem, ekip, yayınlar) birkaç haftada bir değişen içerik. Bunun için sunucu, veritabanı ve bakım yükü gerekmiyor. Statik site ücretsiz barınır, saldırı yüzeyi neredeyse sıfırdır ve trafik ne kadar artarsa artsın CDN'den sunulur. Faz 2 geldiğinde bu sayfalar yine statik kalır, backend yalnızca dinamik işleri üstlenir.

## Faz 2: Backend (planlanan)

Faz 2, ilk gerçek dinamik ihtiyaçla başlar: çevrim içi üyelik başvurusu, proje başvurusu, dosya yükleme, üye paneli.

| Katman | Seçim |
| --- | --- |
| Framework | **Django 5.2 LTS** (Python 3.12+) |
| API | Django REST Framework, yalnızca salt okunur uç noktalar (K-23) |
| Yönetim paneli | Kendi panelimiz (`panel.<alan-adi>`): duyurular, etkinlik kayıt formları, yanıtlar, ekip sayfası; sitenin tasarımıyla ([PANEL.md](PANEL.md)). Django Admin yalnızca teknik sorumlular için, VPN arkasında |
| Veritabanı | PostgreSQL 17, kendi VPS'imizde Docker içinde; yedekleme ve kurtarma [OPERASYON.md](OPERASYON.md) |
| Önbellek ve kuyruk | Redis |
| Arka plan işleri | Celery veya RQ: e-posta, virüs taraması, ileride veri işleme |
| Dosyalar | S3 uyumlu object storage (Cloudflare R2, MinIO vb.), private bucket |
| Çalıştırma | Docker Compose: Django + Redis + Caddy (otomatik TLS) |
| Sunucu (başlangıç) | Yurt içi VPS: 2 vCPU, 4 GB RAM, 40–80 GB SSD. Dosya yükleme ve virüs taraması (ClamAV) devreye girince 8 GB'a çıkılır |
| Ortamlar | yerel (geliştirici bilgisayarı), deneme (staging, canlıyla aynı sunucuda ayrı ortam), canlı ([OPERASYON.md §12](OPERASYON.md#12-deneme-ortamı-ve-canlıya-ilk-geçiş)) |

Neden Django: ekip Python biliyor (NLP); kimlik doğrulama, CSRF koruması, yetkilendirme, migration ve yönetim paneli hazır geliyor; güvenlik geçmişi uzun; agent'lar Django'yu çok iyi yazıyor.

### Planlanan Django uygulamaları

| Uygulama | Sorumluluk |
| --- | --- |
| `accounts` | Kullanıcılar, roller, 2FA |
| `panel` | Yönetim paneli ekranları ([PANEL.md](PANEL.md)) |
| `duyurular` | Gündem gönderileri; Faz 2'de Markdown'dan buraya taşınır |
| `etkinlikler` | Etkinlik bilgileri |
| `formlar` | Kayıt formları, yanıtlar, otomatik silme |
| `ekip` | Ekip sayfası: dönemler, gruplar, kişiler |
| `denetim` | İşlem kaydı: kim neyi ne zaman yaptı |
| `uyelik` | Üyelik başvuruları ve üye kayıt defteri |
| `basvurular` | Proje başvuruları, hakem ataması, değerlendirme |
| `dosyalar` | Yükleme akışı, virüs taraması, süreli indirme linkleri |

### Roller ve yetkiler

| Rol | Kimdir | Yetki |
| --- | --- | --- |
| Üye | Onaylanmış öğrenci | Kendi bilgileri ve kendi başvuruları |
| Hakem | Başvuru değerlendiren kişi | **Yalnızca kendisine atanan** başvurular |
| Editör | Birim üyeleri | Duyuru, form ve ekip sayfası taslağı hazırlama |
| Form sahibi | Bir formdan sorumlu kişi | **Yalnızca kendi formunun** yanıtları |
| Yönetim Kurulu | Seçilmiş yönetim kurulu üyeleri | Onay ve yayın, tüm form yanıtları, üye onayı, başvuru yönetimi; Başkan ve Başkan Yrd. rol atar |
| Danışman | Akademik danışman | Tüm kayıtları görüntüleme (denetim) |
| Süper yönetici | 1–2 teknik sorumlu | Sistem ayarları |

Panel rollerinin ayrıntılı yetki tablosu: [PANEL.md §3](PANEL.md#3-roller-ve-yetkiler). Yetkiler **nesne düzeyinde** kontrol edilir: bir kullanıcının bir başvuruyu görebilmesi, URL'yi bilmesine değil yetkisine bağlıdır. Başvuru sistemlerinde en sık görülen açık budur.

### Dosya yükleme akışı

1. Kullanıcı yüklemek istediğini bildirir. Sunucu dosya boyutunu ve türünü kontrol edip kısa süreli bir **presigned URL** üretir.
2. Tarayıcı dosyayı doğrudan object storage'a yükler. Dosya uygulama sunucusundan geçmez.
3. Arka plan işi dosyayı **ClamAV** ile tarar. Temiz değilse dosya silinir ve kullanıcıya bildirilir.
4. Dosya private bucket'ta durur. Yalnızca yetkili kişiye **süreli link** ile açılır.

Dosyalar asla veritabanına veya sunucu diskine yazılmaz.

## Güvenlik

- Yönetici, yönetim ve danışman hesaplarında **2FA zorunlu**.
- Tüm gizli bilgiler ortam değişkenlerinde. Production bilgileri yalnızca sunucuda ve 1–2 teknik sorumluda.
- **Agent'lar production erişim bilgilerini asla görmez.**
- CI (zamanla eklenecek): testler, Bandit/Semgrep statik güvenlik taraması, bağımlılık denetimi (Dependabot).
- main korumalı, değişiklikler PR ile.
- HTTPS zorunlu, güvenlik başlıkları (HSTS, CSP) açık.
- Django'nun `check --deploy` denetimi production'a çıkmadan önce temiz olmalı.

## KVKK

- **Faz 1:** Sitede form yok, kişisel veri toplanmıyor. Ekip sayfasındaki isim, fotoğraf, e-posta ve bağlantılar kişinin **yazılı onayıyla** yayımlanır. Yazı tipleri kendi sunucumuzdan geldiği için ziyaretçi IP'leri Google'a gitmez.
- **Faz 2:** Üye ve başvuru verisi kişisel veridir.
  - **Sunucu konumu:** Yurt dışındaki bir sunucu (AWS, Hetzner vb.) yurt dışına veri aktarımı sayılır. 2024 değişikliğinden beri standart sözleşme ve Kurum'a bildirim gerekir. Seçenekler: üniversite Bilgi İşlem sunucusu, yurt içi bulut sağlayıcı, ya da yurt dışı + bu yükümlülükler. **Karar bekliyor.**
  - **Veri sorumlusu:** Topluluk mu, üniversite mi? SKS ile yazılı olarak netleştirilecek.
  - Aydınlatma metni ve açık rıza metinleri formların yanında yer alır.
  - Saklama süreleri belirlenir. Süresi dolan veri silinir veya anonimleştirilir.
- Bu bölüm hukuki görüş değildir. Faz 2 öncesinde üniversitenin hukuk birimine danışılmalı.

## Operasyon (Faz 2)

Ayrıntılı rehber: [OPERASYON.md](OPERASYON.md)

- **Yedekleme:** Saatlik, günlük ve aylık otomatik yedek; her migration öncesi elle yedek. Yedekler şifreli; sunucu dışındaki kopya başlangıçta geliştirici bilgisayarlarında, ileride kalıcı bir yurt içi depoda. Geri yükleme ayda bir gerçekten denenir.
- **İzleme:** Sentry (hata takibi) ve bir uptime izleyici.
- **Deneme ortamı (staging):** Başlangıçta canlıyla aynı sunucuda, ayrı veritabanı ve sahte veriyle çalışır; yalnızca denerken açılır. Değişiklikler önce burada denenir (K-19).
- **Sahiplik:** GitHub organizasyonu, alan adı, hosting ve e-posta hesapları kişisel hesaplarda değil topluluk adına durur. Akademik danışman da owner'dır.
- **Devir:** Her yönetim değişiminde bu belge, STATUS.md ve erişim listesi yeni ekiple birlikte gözden geçirilir.
