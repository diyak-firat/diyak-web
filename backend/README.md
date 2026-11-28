# Backend (Faz 2)

Django yönetim paneli ve API. Plan ve kurallar:

- Teknoloji seçimleri, roller, güvenlik ve KVKK: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- Veritabanı, yedekleme, yayın ve kurtarma: [docs/OPERASYON.md](../docs/OPERASYON.md)
- Yönetim paneli, formlar ve uygulama sırası: [docs/PANEL.md](../docs/PANEL.md)

Şu an yalnızca iskelet var: ayarlar, e-posta ile giriş yapan kullanıcı modeli (`accounts.Kullanici`), Django Admin ve `/api/saglik/`. Panel ekranları PANEL.md §12'deki sırayla (A1 → A6) eklenecek.

## Yerelde çalıştırma (Docker)

Repo kökünde, bir kez:

```bash
cp .env.example .env            # COMPOSE_FILE ile geliştirme eklentisini açar
sed -i "s/^DIYAK_UID=.*/DIYAK_UID=$(id -u)/;s/^DIYAK_GID=.*/DIYAK_GID=$(id -g)/" .env
mkdir -p secrets && chmod 700 secrets
openssl rand -base64 48 | tr -d '\n' > secrets/db_password.txt
openssl rand -base64 48 | tr -d '\n' > secrets/django_secret_key.txt
```

Sonra:

```bash
docker compose up -d                              # PostgreSQL + Django (http://localhost:8000)
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose run --rm web pytest                # testler
docker compose run --rm web python manage.py makemigrations
```

Kod `backend/` klasöründen konteynere bağlıdır; değişiklikler sunucuyu yeniden başlatmadan görünür.

> **`docker compose down -v` çalıştırmayın.** `-v` veritabanını siler. Durdurmak için `docker compose down` yeterli. Yerel veritabanını sıfırlamak gerekirse önce AGENTS.md'deki yerel yedek komutunu çalıştırın.

## Docker olmadan (yalnızca testler)

[uv](https://docs.astral.sh/uv/) ve erişilebilir bir PostgreSQL gerekir:

```bash
cd backend
uv sync
DB_HOST=127.0.0.1 DB_PASSWORD=... uv run pytest
```

## Dosyalar

```
backend/
├── pyproject.toml, uv.lock   Bağımlılıklar (uv ile kilitli; eklemeden önce sorulur)
├── Dockerfile                prod (gunicorn, yetkisiz kullanıcı) ve dev (test araçları) hedefleri
├── config/settings/          base · development · test · production; ayarlar ortam değişkenlerinden
│                             (gizli bilgiler AD_FILE ile dosyadan: ortam.py)
├── config/api.py             /api/saglik/ (izleme servisi için)
├── apps/accounts/            Kullanici (e-posta ile giriş), dönemlik RolAtamasi, Davet
│                             yetki.py: panel yetki kuralları · servisler.py: davet ve rol işlemleri
├── apps/denetim/             IslemKaydi ve kaydet() (kişisel veri yazılmaz)
├── conftest.py               Ortak test fixture'ları (sahte kullanıcı ve roller)
└── tests/                    Ayar ve uç nokta testleri (uygulama testleri apps/*/tests/ altında)
```

Repo kökündeki `docker-compose.yml` sunucuda da kullanılan servis tanımıdır; `docker-compose.dev.yml` yalnızca yerel geliştirme içindir (K-24).

## Kurallar

- Django 5.2 LTS, Python 3.13, PostgreSQL 17.
- Ayarlar ortam değişkenlerinden okunur. Gizli bilgi kodda yer almaz; sunucuda `secrets/` altındaki dosyalardan gelir.
- Her model değişikliği migration ile gelir. Migration dosyaları repoya eklenir. Migration içeren her yayından önce elle yedek alınır (AGENTS.md, OPERASYON.md).
- Her yeni görünüm ve uç nokta için yetkisiz erişim testi yazılır.
- CI (`.github/workflows/backend.yml`): eksik migration denetimi, pytest, `check --deploy`, Bandit.

## Hedef yapı

Uygulamalar PANEL.md'deki sırayla `apps/` altına eklenecek:

| Uygulama | Sorumluluk | Aşama |
| --- | --- | --- |
| `accounts` | Kullanıcılar, roller, davet, 2FA (`django-otp`) | iskelet ✓, A1 |
| `denetim` | İşlem kaydı | A1 |
| `panel` | Yönetim paneli ekranları | A1 |
| `duyurular` | Gündem gönderileri | A2 |
| `ekip` | Ekip sayfası | A3 |
| `etkinlikler`, `formlar` | Etkinlikler, kayıt formları ve yanıtlar | A4–A5 |
| `uyelik`, `basvurular`, `dosyalar` | Üyelik, proje başvuruları, dosya yükleme | sonra |

Redis, MinIO ve ClamAV, onları kullanan ilk özellikle birlikte Compose'a eklenir.

## Başlamadan önce netleşmesi gerekenler

- [ ] Hosting yeri (KVKK): üniversite sunucusu, yurt içi bulut veya yurt dışı + yükümlülükler
- [ ] Veri sorumlusu: topluluk mu, üniversite mi (SKS ile yazılı)
- [x] API katmanı: Django REST Framework (K-23)
- [ ] Panel metin editörü bileşeni (PANEL.md A2)
