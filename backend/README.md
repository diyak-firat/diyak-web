# Backend (Faz 2 — henüz başlamadı)

Bu klasör, Faz 2'de kurulacak Django API için ayrıldı. Faz 2, ilk gerçek dinamik ihtiyaçla başlar: çevrim içi üyelik başvurusu, proje başvurusu, dosya yükleme veya üye paneli.

> Agent'lar için: Kullanıcı açıkça istemeden bu klasörde kod oluşturma.

Teknoloji seçimleri, roller, dosya yükleme akışı, güvenlik ve KVKK: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
Veritabanı, yedekleme, yayın ve kurtarma: [docs/OPERASYON.md](../docs/OPERASYON.md)
Yönetim paneli, formlar ve uygulama sırası: [docs/PANEL.md](../docs/PANEL.md)

## Planlanan yapı

```
backend/
├── pyproject.toml          Bağımlılıklar (uv veya pip-tools ile kilitlenir)
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py   check --deploy temiz olmalı
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── apps/
│   ├── accounts/           Kullanıcılar, roller, 2FA (django-otp)
│   ├── panel/              Yönetim paneli ekranları (PANEL.md)
│   ├── duyurular/          Gündem gönderileri
│   ├── etkinlikler/        Etkinlik bilgileri
│   ├── formlar/            Kayıt formları ve yanıtlar
│   ├── ekip/               Ekip sayfası
│   ├── denetim/            İşlem kaydı
│   ├── uyelik/             Üyelik başvuruları, üye kayıt defteri
│   ├── basvurular/         Proje başvuruları, hakem ataması
│   └── dosyalar/           Presigned upload, ClamAV taraması, süreli linkler
├── tests/                  pytest + pytest-django
├── Dockerfile
└── docker-compose.yml      Django, PostgreSQL, Redis, MinIO, ClamAV (yerel geliştirme)
```

## Başlamadan önce netleşmesi gerekenler

- [ ] Hosting yeri (KVKK): üniversite sunucusu, yurt içi bulut veya yurt dışı + yükümlülükler
- [ ] Veri sorumlusu: topluluk mu, üniversite mi (SKS ile yazılı)
- [ ] API katmanı: Django Ninja veya Django REST Framework
- [ ] Panel metin editörü bileşeni (PANEL.md A2)

## Başlangıç kuralları

- Django 5.2 LTS, Python 3.12+, PostgreSQL 17.
- Ayarlar ortam değişkenlerinden okunur (`django-environ` vb.). Gizli bilgi kodda yer almaz.
- Her model değişikliği migration ile gelir. Migration dosyaları repoya eklenir. Migration içeren her yayından önce elle yedek alınır (AGENTS.md, OPERASYON.md).
- Her yeni uç nokta için yetki testi yazılır: yetkisiz kullanıcı erişemiyor mu?
- İlk testlerle birlikte GitHub Actions eklenir (pytest, Bandit, `manage.py check --deploy`).
