# Operasyon Rehberi: Veritabanı, Yedekleme ve Kurtarma

Bu rehber Faz 2'de, backend sunucusu kurulduğunda uygulanır. Üyelik başvuruları, proje başvuruları ve etkinlik kayıtları topluluğun en önemli verisidir; kaybolması ya da sızması kabul edilemez. Bu belge o verinin nasıl korunacağını adım adım anlatır.

> **Agent'lar için:** Bu belgedeki komutları sunucuda sen çalıştırmazsın. Sunucuya bağlanmak, erişim bilgisi istemek veya yedek dosyası açmak yasaktır. Migration içeren işlerde kuralların AGENTS.md dosyasındadır.

## İçindekiler

1. [Genel bakış](#1-genel-bakış)
2. [Sunucudaki yerleşim](#2-sunucudaki-yerleşim)
3. [PostgreSQL kurulumu](#3-postgresql-kurulumu)
4. [Yedek anahtarları](#4-yedek-anahtarları)
5. [Otomatik yedekleme](#5-otomatik-yedekleme)
6. [Elle yedek ve yayın adımları](#6-elle-yedek-ve-yayın-adımları)
7. [Yedeği geliştiricinin bilgisayarına çekmek](#7-yedeği-geliştiricinin-bilgisayarına-çekmek)
8. [Geri yükleme provası (ayda bir)](#8-geri-yükleme-provası-ayda-bir)
9. [Arıza anında](#9-arıza-anında)
10. [İzleme ve bakım](#10-izleme-ve-bakım)
11. [Kontrol listesi](#11-kontrol-listesi)
12. [Deneme ortamı ve canlıya ilk geçiş](#12-deneme-ortamı-ve-canlıya-ilk-geçiş)

---

## 1. Genel bakış

PostgreSQL'i yönetilen bir hizmette değil, kendi VPS'imizde Docker içinde çalıştırıyoruz (karar: [DECISIONS.md K-13](DECISIONS.md)). Bu yüzden yönetilen hizmetlerin bizim yerimize yaptığı işleri kendimiz yaparız:

| İş | Nasıl |
| --- | --- |
| Yedek almak | Saatlik, günlük ve aylık otomatik yedek + her yayın öncesi elle yedek |
| Yedeği korumak | `age` ile şifreleme, sunucu dışına kopya, geliştirici bilgisayarına ek kopya |
| Yedeğin çalıştığından emin olmak | Ayda bir geri yükleme provası |
| Yedek alınamazsa haberdar olmak | healthchecks.io benzeri izleme servisi |
| Veritabanını korumak | İnternete kapalı port, güçlü şifre, SSH anahtarıyla giriş |

**3-2-1 kuralı:** Verinin 3 kopyası, 2 farklı yerde, 1'i sunucunun dışında:

```
1. Canlı veritabanı                   (VPS)
2. Şifreli yedekler                   (VPS, /yedek)                     ← hızlı geri dönüş
3. Şifreli yedeklerin kopyası         (geliştirici bilgisayarları)      ← sunucu giderse
4. Kalıcı uzak depo                   (üniversite depolama alanı vb.)   ← ileride
```

**Başlangıç dönemi:** Kalıcı bir uzak depo kurulana kadar sunucu dışındaki kopya, yedeklerin en az bir, mümkünse **iki** geliştiricinin bilgisayarına her gün çekilmesidir (bölüm 7, karar K-19). Uzak depo kurulunca 3. madde ek kopya olarak devam eder.

KVKK nedeniyle **tüm kopyalar yurt içinde** durur.

**Ne kadar veri kaybedebiliriz?** Saatlik yedek alındığı için en kötü durumda son bir saatin verisi. Yayın öncesi elle yedek alındığı için hatalı bir yayında kayıp sıfıra yakındır.

## 2. Sunucudaki yerleşim

```
/opt/diyak/                 Repo ve docker-compose.yml
/opt/diyak/secrets/         db_password.txt (repoya girmez, yalnızca root okur)
/opt/diyak/ops/
  ├── yedekle.sh            Yedek betiği (bölüm 5)
  ├── yayinla.sh            Yayın betiği (bölüm 6)
  ├── yedek.env             Uzak depo adı, izleme adresleri
  └── alicilar.txt          Yedeği açabilecek kişilerin AÇIK anahtarları
/yedek/                     Şifreli yedekler (root:yedek, 750)
```

İlk kurulumda yedek klasörü ve grubu oluşturulur:

```bash
sudo groupadd -f yedek
sudo mkdir -p /yedek /opt/diyak/ops
sudo chown root:yedek /yedek && sudo chmod 750 /yedek
sudo apt install age rclone rsync   # Debian/Ubuntu
```

## 3. PostgreSQL kurulumu

```yaml
# docker-compose.yml (veritabanı kısmı)
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_DB: diyak
      POSTGRES_USER: diyak
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    secrets: [db_password]
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U diyak -d diyak']
      interval: 10s
      retries: 5
    # "ports" YOK: veritabanı internete açılmaz, yalnızca aynı ağdaki Django erişir.

volumes:
  pgdata:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

Kurallar:

- `ports:` satırı eklenmez. Veritabanına elle bakmak gerekirse sunucuya SSH ile girilip `docker compose exec db psql -U diyak diyak` kullanılır.
- Şifre en az 32 karakter rastgele üretilir: `openssl rand -base64 32 > secrets/db_password.txt && chmod 600 secrets/db_password.txt`
- **`docker compose down -v` asla çalıştırılmaz.** `-v` veritabanı volume'ünü siler.
- Sunucuya yalnızca SSH anahtarıyla girilir, parola ile giriş kapalıdır.

## 4. Yedek anahtarları

Yedekler kişisel veri içerdiği için [age](https://github.com/FiloSottile/age) ile şifrelenir. age'de iki tür anahtar vardır:

- **Açık anahtar** (`age1...`): Yalnızca şifreler. Sunucuda `alicilar.txt` içinde durur. Ele geçirilse bile yedeği açmaya yaramaz.
- **Gizli anahtar**: Yedeği açar. **Sunucuda asla durmaz.**

Kurulum, yedeği açabilecek **en az iki kişi** için yapılır (ör. teknik sorumlu ve başkan):

```bash
# Her kişi kendi bilgisayarında:
age-keygen -o diyak-yedek-anahtari.txt           # gizli anahtar üretir, açık anahtarı ekrana yazar
age -p -o diyak-yedek-anahtari.age diyak-yedek-anahtari.txt   # parola ile korur
shred -u diyak-yedek-anahtari.txt                # parolasız kopyayı siler
```

Ekrana yazılan açık anahtar (`age1...`) sunucudaki `/opt/diyak/ops/alicilar.txt` dosyasına satır satır eklenir. Parolalı gizli anahtar dosyası ve parolası iki ayrı güvenli yerde saklanır (ör. parola yöneticisi). Biri kaybolursa diğer kişinin anahtarı yedekleri açmaya yeter.

**Dönem değişiminde:** Yeni sorumlular kendi anahtarlarını üretir, `alicilar.txt` güncellenir, ayrılanların açık anahtarı çıkarılır. Eski yedekler eski anahtarlarla şifreli kalır; saklama süresi dolunca kendiliğinden silinir.

## 5. Otomatik yedekleme

### Yedek türleri ve saklama süreleri

| Tür | Ne zaman | Saklama |
| --- | --- | --- |
| `saatlik` | Her saat başı +15 dk | 2 gün |
| `gunluk` | Her gece 03:00 | 14 gün |
| `aylik` | Her ayın 1'i 03:30 | 6 ay |
| `elle` | Her yayın ve riskli işlem öncesi | 30 gün |

Saklama süreleri topluluğun kişisel veri saklama politikasıyla uyumlu olmalıdır: veritabanından silinen kişisel veri, yedeklerde bu süre kadar yaşamaya devam eder.

Veri küçük olduğu için (binlerce kayıt birkaç MB) sık ve tam yedek almak ucuzdur.

### Yedek betiği

`/opt/diyak/ops/yedekle.sh`:

```bash
#!/usr/bin/env bash
# DİYAK veritabanı yedeği.
# Kullanım: yedekle.sh <saatlik|gunluk|aylik|elle> [not]
#   örnek:  sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi
set -euo pipefail
umask 027

TUR="${1:?Kullanım: yedekle.sh <saatlik|gunluk|aylik|elle> [not]}"
case "$TUR" in saatlik|gunluk|aylik|elle) ;; *) echo "Geçersiz tür: $TUR" >&2; exit 2 ;; esac
NOT="$(printf '%s' "${2:-}" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-')"   # dosya adına güvenli hale getir

OPS=/opt/diyak/ops
YEDEK_DIZIN=/yedek
# shellcheck source=/dev/null
source "$OPS/yedek.env"          # UZAK, IZLEME_URL_SAATLIK, IZLEME_URL_GUNLUK, ...

AD="${TUR}_$(date +%Y-%m-%d_%H%M)${NOT:+_$NOT}.dump.age"
GECICI="$(mktemp "$YEDEK_DIZIN/.yarim.XXXXXX")"
trap 'rm -f "$GECICI"' EXIT

# 1. Yedeği al ve diske hiç şifresiz yazmadan şifrele
cd /opt/diyak
docker compose exec -T db pg_dump -U diyak -Fc diyak | age -R "$OPS/alicilar.txt" > "$GECICI"
[ -s "$GECICI" ] || { echo "Yedek boş çıktı" >&2; exit 1; }
mv "$GECICI" "$YEDEK_DIZIN/$AD"
chgrp yedek "$YEDEK_DIZIN/$AD"

# 2. Uzak depo tanımlıysa sunucu dışına kopyala
#    (Başlangıç döneminde UZAK boştur; sunucu dışındaki kopya bilgisayarlara çekilir, bölüm 7)
if [ -n "${UZAK:-}" ]; then
  rclone copy "$YEDEK_DIZIN/$AD" "$UZAK"
fi

# 3. Süresi dolanları sil (sunucuda ve varsa uzak depoda)
temizle() {
  find "$YEDEK_DIZIN" -maxdepth 1 -name "$1" -mtime "+$2" -delete
  if [ -n "${UZAK:-}" ]; then
    rclone delete "$UZAK" --include "$1" --min-age "${2}d"
  fi
}
temizle 'saatlik_*' 2
temizle 'gunluk_*'  14
temizle 'elle_*'    30
temizle 'aylik_*'   186

# 4. "Yedek alındı" sinyali
IZLEME_DEGISKENI="IZLEME_URL_${TUR^^}"
if [ -n "${!IZLEME_DEGISKENI:-}" ]; then
  curl -fsS -m 10 --retry 3 "${!IZLEME_DEGISKENI}" > /dev/null || true
fi

echo "Yedek hazır: $YEDEK_DIZIN/$AD"
```

`/opt/diyak/ops/yedek.env`:

```bash
UZAK=""                           # Başlangıçta boş. Kalıcı uzak depo kurulunca: "yurtici-depo:diyak-yedek"
IZLEME_URL_SAATLIK="https://hc-ping.com/<id>"
IZLEME_URL_GUNLUK="https://hc-ping.com/<id>"
IZLEME_URL_AYLIK="https://hc-ping.com/<id>"
```

### Zamanlama

`/etc/cron.d/diyak-yedek`:

```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
15 * * * *  root  /opt/diyak/ops/yedekle.sh saatlik >> /var/log/diyak-yedek.log 2>&1
0  3 * * *  root  /opt/diyak/ops/yedekle.sh gunluk  >> /var/log/diyak-yedek.log 2>&1
30 3 1 * *  root  /opt/diyak/ops/yedekle.sh aylik   >> /var/log/diyak-yedek.log 2>&1
```

### Yedek alınamazsa nasıl haberimiz olur

healthchecks.io (ücretsiz planı yeterli) gibi bir serviste her yedek türü için bir "check" açılır ve adresi `yedek.env` dosyasına yazılır. Betik her başarılı yedekte o adrese istek atar. Beklenen sürede istek gelmezse servis teknik sorumluya ve başkana e-posta atar. Böylece yedek sessizce başarısız olamaz.

### Uzak depo

Başlangıç döneminde kullanılmıyor (K-19). Kalıcı çözüm olarak yurt içinde S3 uyumlu bir depolama, ikinci küçük bir VPS veya üniversite sunucusu olabilir. rclone bunların hepsiyle çalışır (`rclone config`). Mümkünse depoda **sürümleme (versioning)** açılır: sunucu ele geçirilip yedekler silinse bile eski sürümler kurtarılabilir.

## 6. Elle yedek ve yayın adımları

### Ne zaman elle yedek alınır

- Migration içeren **her** yayından önce
- Veritabanında toplu güncelleme, silme veya veri taşıma öncesi
- PostgreSQL sürüm yükseltmesi öncesi
- Sunucu taşıma veya büyük ayar değişikliği öncesi
- Emin olmadığınız her işlemden önce

```bash
sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi
```

### Yayın betiği

Yayın betiği, **son 15 dakikada alınmış elle yedek yoksa migrate çalıştırmaz.** Bu kural, işi bir agent'a bıraktığımızda ya da aceleyle yayın yaptığımızda yedeğin unutulmasını engeller.

`/opt/diyak/ops/yayinla.sh` (özet):

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/diyak

git fetch origin
git checkout --detach origin/main
docker compose build web          # yeni kodla imajı derle (migration dosyaları imajın içinde)

# Bekleyen migration var mı?
if docker compose run --rm web python manage.py migrate --check > /dev/null 2>&1; then
  echo "Bekleyen migration yok."
else
  echo "Bekleyen migration'lar:"
  docker compose run --rm web python manage.py migrate --plan

  SON_ELLE="$(find /yedek -maxdepth 1 -name 'elle_*.age' -mmin -15 | head -n 1)"
  if [ -z "$SON_ELLE" ]; then
    echo "DURDURULDU: Son 15 dakikada alınmış elle yedek yok."
    echo "Önce çalıştırın: sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi"
    exit 1
  fi
  echo "Elle yedek bulundu: $SON_ELLE"
fi

docker compose run --rm web python manage.py migrate
docker compose up -d
docker compose run --rm web python manage.py check --deploy
echo "Yayın tamamlandı. Siteyi açıp kontrol edin."
```

### Yayın sırası (özet)

1. PR birleşti, staging'de denendi.
2. `sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi`
3. `sudo /opt/diyak/ops/yayinla.sh`
4. Siteyi açıp kritik akışları (giriş, başvuru formu, admin) kontrol et.
5. Sorun varsa [bölüm 9-B](#b-hatalı-yayın-veya-migration).

## 7. Yedeği geliştiricinin bilgisayarına çekmek

Son yedekler bir yönetim üyesinin veya teknik sorumlunun bilgisayarına her gün çekilir.

**Başlangıç döneminde bu, sunucu dışındaki tek kopyadır** (K-19). Bilgisayar kapalı, kayıp ya da bozuk olabileceği için:

- Mümkünse **iki kişinin** bilgisayarına çekilir. Sunucu tarafında her biri için ayrı bir anahtar satırı eklenir.
- Her başarılı çekme bir izleme servisine sinyal gönderir. 2 gün boyunca hiçbir bilgisayar çekmezse teknik sorumluya e-posta gider (aşağıdaki betik).
- Kalıcı bir uzak depo kurulunca bu kopya ek kopya olarak devam eder.

### Şartlar (KVKK)

Veri yurt içinde kalsa da kişisel bir cihazda kişisel veri saklanmış olur. KVKK belirli bir yöntem saymaz ama "uygun güvenlik düzeyi" ve "gerektiği kadar saklama" ister. Bunu karşılayan asgari kurallar:

- **Bilgisayara yalnızca şifreli `.age` dosyaları gelir.** Betik zaten böyle çalışır; asıl koruma budur.
- **Yedeği açan gizli anahtar aynı bilgisayarda parolasız durmaz** (bölüm 4). Anahtar başka yerdeyse veya parola korumalıysa, bilgisayar çalınsa bile dosyalar okunamaz.
- **Kopya kimdeyse yazılı olarak bilinir:** Yönetim Kurulu'na tek satırlık bir bildirim yeterli (toplantı notu veya e-posta). Bu, kopyayı topluluk adına tuttuğunuzu gösterir ve sizi kişisel olarak korur.
- **Görev bitince silinir:** `~/diyak-yedek` klasörü ve `~/.ssh/diyak_yedek` anahtarı silinir, sunucudaki `authorized_keys` satırı kaldırılır. Görev süresince eski yedekler betik tarafından zaten otomatik siliniyor.

Disk şifreleme (LUKS, FileVault, BitLocker) genel olarak önerilir ama yedekler zaten şifreli olduğu ve anahtar parolasız durmadığı sürece bu iş için zorunlu değildir.

### Neden "çekme" (pull) yöntemi

Bilgisayar yedeği sunucudan kendisi çeker, sunucu bilgisayara bir şey göndermez. Böylece:

- Sunucunun geliştiricinin bilgisayarına erişimi olmaz. Sunucu ele geçirilse bile bilgisayara ulaşılamaz.
- Bilgisayar kapalıyken iş kaçmaz, açıldığında tamamlanır.
- Bilgisayardaki anahtar sunucuda **yalnızca `/yedek` klasörünü okuyabilir**. Komut çalıştıramaz, dosya silemez.

### Sunucu tarafı (bir kez)

```bash
sudo useradd --system --create-home --shell /bin/bash --groups yedek yedekci

sudo -u yedekci mkdir -p ~yedekci/.ssh
# Geliştiricinin AÇIK SSH anahtarı, yalnızca /yedek'i salt okunur görecek şekilde eklenir.
# rrsync, rsync paketiyle gelir; yolu `which rrsync` ile doğrulayın.
echo 'command="/usr/bin/rrsync -ro /yedek/",restrict ssh-ed25519 AAAA... gelistirici-adi' \
  | sudo -u yedekci tee -a ~yedekci/.ssh/authorized_keys
sudo chmod 600 ~yedekci/.ssh/authorized_keys
```

### Bilgisayar tarafı (Linux)

Yalnızca bu iş için ayrı bir SSH anahtarı üretin:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/diyak_yedek -C "diyak-yedek-$(whoami)"
# ~/.ssh/diyak_yedek.pub içeriğini teknik sorumluya gönderin (yukarıdaki authorized_keys satırı)
```

`~/bin/diyak-yedek-cek.sh`:

```bash
#!/usr/bin/env bash
# Sunucudaki şifreli DİYAK yedeklerini bu bilgisayara çeker.
set -euo pipefail
SUNUCU="yedekci@diyak-sunucu.example"       # TODO: sunucu adresi
HEDEF="$HOME/diyak-yedek"
mkdir -p "$HEDEF" && chmod 700 "$HEDEF"

# Günlük, aylık ve elle alınan yedekleri çek (saatlikler gereksiz).
# --delete KULLANILMAZ: sunucuda yedekler silinirse buradaki kopyalar kalmalı.
rsync -a \
  --include='gunluk_*.age' --include='aylik_*.age' --include='elle_*.age' --exclude='*' \
  -e "ssh -i $HOME/.ssh/diyak_yedek -o BatchMode=yes" \
  "$SUNUCU:" "$HEDEF/"

# Saklama sürelerini burada da uygula (KVKK)
find "$HEDEF" -name 'gunluk_*.age' -mtime +14  -delete
find "$HEDEF" -name 'elle_*.age'   -mtime +30  -delete
find "$HEDEF" -name 'aylik_*.age'  -mtime +186 -delete

# En yeni günlük yedek 2 günden eskiyse uyar
if [ -z "$(find "$HEDEF" -name 'gunluk_*.age' -mtime -2 | head -n 1)" ]; then
  notify-send -u critical "DİYAK yedek" "Son 2 günde yeni günlük yedek gelmedi." 2>/dev/null || true
  echo "UYARI: Son 2 günde yeni günlük yedek yok." >&2
  exit 1
fi

# Başarılı çekme sinyali (healthchecks.io'da "yedek-cekme" check'i, 2 gün süreli)
IZLEME_URL_CEKME="https://hc-ping.com/<id>"   # TODO
curl -fsS -m 10 --retry 3 "$IZLEME_URL_CEKME" > /dev/null || true
```

```bash
chmod +x ~/bin/diyak-yedek-cek.sh
```

Her gün otomatik çalışması için systemd kullanıcı zamanlayıcısı:

`~/.config/systemd/user/diyak-yedek.service`

```ini
[Unit]
Description=DİYAK yedeklerini sunucudan çek

[Service]
Type=oneshot
ExecStart=%h/bin/diyak-yedek-cek.sh
```

`~/.config/systemd/user/diyak-yedek.timer`

```ini
[Unit]
Description=DİYAK yedeklerini günde bir kez çek

[Timer]
OnCalendar=*-*-* 10:00
Persistent=true
RandomizedDelaySec=15m

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now diyak-yedek.timer
systemctl --user list-timers diyak-yedek.timer   # bir sonraki çalışma zamanı
journalctl --user -u diyak-yedek.service         # son çalışmaların kaydı
```

`Persistent=true` sayesinde bilgisayar 10:00'da kapalıysa iş, bir sonraki açılışta yapılır. macOS veya Windows kullanan biri için aynı betik launchd veya Görev Zamanlayıcı ile çalıştırılabilir.

## 8. Geri yükleme provası (ayda bir)

Hiç denenmemiş yedek, çalıştığı bilinmeyen yedektir. Prova **canlı veritabanına dokunmadan**, yerel bir Docker PostgreSQL'e yapılır. Gizli anahtar sunucuya hiç gitmez.

```bash
# 1. Geçici bir PostgreSQL başlat
docker run -d --name diyak-prova -e POSTGRES_PASSWORD=prova postgres:17
sleep 5

# 2. En yeni günlük yedeği aç ve geri yükle (age, anahtar parolasını sorar)
SON="$(ls -t ~/diyak-yedek/gunluk_*.age | head -n 1)"
echo "Prova yedeği: $SON"
docker exec diyak-prova createdb -U postgres diyak
age -d -i ~/diyak-yedek-anahtari.age "$SON" \
  | docker exec -i diyak-prova pg_restore -U postgres -d diyak --no-owner

# 3. Mantıklı mı? Tablo ve kayıt sayılarına bak
docker exec diyak-prova psql -U postgres -d diyak -c '\dt'
docker exec diyak-prova psql -U postgres -d diyak -c 'SELECT count(*) FROM uyelik_basvuru;'

# 4. Temizle: içinde kişisel veri var
docker rm -f diyak-prova
```

Prova sonucu (tarih, yedek adı, kayıt sayıları, sorun) STATUS.md'deki operasyon bölümüne bir satır olarak yazılır.

## 9. Arıza anında

Önce sakin olun ve **hiçbir şeyi silmeyin.** Canlı veritabanına bir şey yapmadan önce, mümkünse o anki halinin de elle yedeğini alın (`yedekle.sh elle ariza-ani`): sonradan bir kaydın neden kaybolduğunu anlamak için gerekebilir.

### A. Yanlışlıkla silinen veya bozulan kayıt

Tüm veritabanı geri **yüklenmez**, yoksa o andan sonraki tüm kayıtlar kaybolur. Bunun yerine:

1. Kaydın sağlam olduğu en yakın yedeği bölüm 8'deki gibi **ayrı bir prova veritabanına** açın.
2. İlgili kaydı bulun (`psql` ile).
3. Yalnızca o kaydı canlı veritabanına geri ekleyin (Django Admin, Django shell veya `psql`).

### B. Hatalı yayın veya migration

1. Siteyi bakıma alın: `docker compose stop web`
2. Yayından hemen önce alınan `elle_*_migration-oncesi` yedeğini bulun.
3. Gizli anahtar sunucuya gitmeden, yedeği kendi bilgisayarınızda açıp sunucuya akıtın:
   ```bash
   age -d -i ~/diyak-yedek-anahtari.age elle_2027-03-01_1405_migration-oncesi.dump.age \
     | ssh yonetici@diyak-sunucu.example \
       'cd /opt/diyak && docker compose exec -T db pg_restore -U diyak -d diyak --clean --if-exists'
   ```
4. Önceki sürüme dönün: `git checkout --detach <önceki-commit>` → `docker compose up -d --build`
5. Siteyi kontrol edip açın. Yedek ile arıza arasında girilen kayıtlar kaybolmuş olabilir; bunu yönetime bildirin.

### C. Sunucu tamamen gitti

1. Yeni VPS açın (yurt içi), Docker kurun, repoyu `/opt/diyak` altına klonlayın.
2. `secrets/db_password.txt` ve `ops/` dosyalarını yeniden oluşturun.
3. `docker compose up -d db`
4. En yeni yedeği geliştirici bilgisayarından (kalıcı uzak depo kurulduysa oradan) alın ve B-3'teki gibi geri yükleyin.
5. `docker compose up -d`, ardından DNS kaydını yeni sunucuya yönlendirin.
6. Yedek zamanlamasını (bölüm 5) yeniden kurun.

### D. Sunucu ele geçirildi şüphesi

1. Sunucuyu ağdan ayırın ya da kapatın.
2. Tüm şifreleri ve anahtarları değiştirin (veritabanı, SSH, sağlayıcı hesapları, Django `SECRET_KEY`).
3. C'deki gibi temiz bir sunucuya, ele geçirmeden **önceki** bir yedekten kurun.
4. KVKK gereği kişisel veri ihlali olabileceği için Yönetim Kurulu, danışman ve SKS'ye hemen haber verin. Kişisel Verileri Koruma Kurulu'na bildirim süresi kısadır (72 saat); kararı veri sorumlusu verir.

## 10. İzleme ve bakım

- **Disk:** %80'i geçince uyarı gelsin. Disk dolarsa PostgreSQL yazmayı durdurur ve yeni başvurular kaydedilemez.
- **Küçük sürüm güncellemeleri:** `docker compose pull db && docker compose up -d db` (ayda bir, öncesinde elle yedek).
- **Büyük sürüm geçişi** (ör. 17 → 18): Önce deneme ortamında denenir (bölüm 12). Elle yedek alınır, yeni sürümle boş bir veritabanı açılıp yedek geri yüklenir. Yılda bir planlı iş olarak STATUS.md'ye yazılır.
- **Log:** `/var/log/diyak-yedek.log` ayda bir göz atılır.

## 11. Kontrol listesi

| Ne zaman | İş | Kim |
| --- | --- | --- |
| Her saat / gece / ay | Otomatik yedek, şifreleme, uzak kopya, izleme sinyali | Sunucu (cron) |
| Her gün | Yedeği bilgisayara çekme, izleme sinyali | Geliştirici bilgisayarları (systemd) |
| Her değişiklikte | Önce deneme ortamında dene (bölüm 12) | Değişikliği yapan kişi |
| Her migration ve riskli işlem öncesi | `yedekle.sh elle <not>` | Yayını yapan kişi |
| Ayda bir | Geri yükleme provası, sonucu STATUS.md'ye yaz | Teknik sorumlu |
| Ayda bir | Disk, log ve izleme servisine göz at | Teknik sorumlu |
| Dönem başında | Yedek anahtarlarını, `alicilar.txt`'yi, bilgisayar kopyası listesini ve erişimleri yeni yönetimle güncelle | Teknik sorumlu + başkan |

## 12. Deneme ortamı ve canlıya ilk geçiş

Başlangıçta tek bir sunucu kullanıyoruz (K-19). Değişiklikleri gerçek kullanıcılara ulaşmadan denemek için aynı sunucuda, canlı ortamdan tamamen ayrı bir **deneme ortamı** çalışır.

### Yerleşim

```
Ana sunucu (4 GB)
├── /opt/diyak           canlı ortam    panel.<alan-adi>          gerçek veri, hep açık        ~1,5 GB
└── /opt/diyak-deneme    deneme ortamı  deneme-panel.<alan-adi>   sahte veri, yalnızca denerken ~1 GB
```

| | Canlı | Deneme |
| --- | --- | --- |
| Docker Compose proje adı | `diyak` | `diyak-deneme` |
| Veritabanı, Redis | kendi volume'leri | kendi volume'leri (ayrı) |
| Şifreler, `SECRET_KEY`, `.env` | kendi | **ayrı**, canlıdakilerle aynı olamaz |
| Veri | gerçek | **yalnızca sahte veri** |
| E-posta | gerçek gönderim | **gönderilmez**: konsola yazılır ya da Mailpit'te toplanır |
| Site bağlantısı | canlı siteyi yeniden derletir | canlı siteyi derletmez; kendi önizleme sitesine bağlanır |
| Erişim | internete açık (2FA ile) | yalnızca VPN üzerinden |
| Yedek | saatlik/günlük/aylık | yok (veri atılabilir) |
| Arama motorları | açık | `noindex` |

**Tek ters vekil sunucu:** Caddy yalnızca canlı ortamda çalışır. Deneme ortamının web servisi ortak bir Docker ağına (`proxy`) bağlanır, Caddy `deneme-panel.` adresini ona yönlendirir. Deneme ortamı kapalıyken bu adres hata verir, bu normaldir.

### Deneme ortamını açma, kapama, sıfırlama

`/opt/diyak/ops/deneme.sh`:

```bash
#!/usr/bin/env bash
# Deneme ortamını yönetir. Kullanım: deneme.sh <ac|kapat|sifirla> [branch]
set -euo pipefail
cd /opt/diyak-deneme
DC=(docker compose -p diyak-deneme)

case "${1:-}" in
  ac)
    git fetch origin
    git checkout --detach "origin/${2:-main}"
    "${DC[@]}" up -d --build
    "${DC[@]}" run --rm web python manage.py migrate
    echo "Deneme ortamı açık: https://deneme-panel.<alan-adi> (VPN gerekir)"
    ;;
  kapat)
    "${DC[@]}" down              # veri kalır
    ;;
  sifirla)
    # Yalnızca deneme ortamının volume'lerini siler. Canlı ortama dokunamaz:
    # proje adı ve klasör sabittir.
    "${DC[@]}" down -v
    "${DC[@]}" up -d --build
    "${DC[@]}" run --rm web python manage.py migrate
    "${DC[@]}" run --rm web python manage.py sahte_veri   # PANEL.md A1'de yazılacak komut
    ;;
  *)
    echo "Kullanım: deneme.sh <ac|kapat|sifirla> [branch]" >&2; exit 2 ;;
esac
```

`docker compose down -v` yalnızca bu betik içinde ve yalnızca `diyak-deneme` projesi için kullanılır. Canlı ortamda asla (bölüm 3).

### Kurallar

- **Deneme ortamına gerçek veri kopyalanmaz.** Canlı yedekler deneme ortamına geri yüklenmez. Sahte veri `sahte_veri` komutuyla üretilir.
- **Deneme ortamı gerçek e-posta göndermez.** Aksi halde gerçek kişilere davet veya kayıt onayı gidebilir.
- **Başvuru ve kayıt dönemlerinde deneme ortamı kapalı tutulur**, bellek canlı ortama kalır.
- Deneme ortamı canlıyı yavaşlatmaya başlarsa veya sürekli açık kalması gerekirse ikinci bir sunucuya taşınır. İçindeki veri atılabilir olduğu için taşıma zahmetsizdir.

### Her değişikliğin yolu

```
yerel (Docker, sahte veri) → PR + inceleme → deneme ortamı (ac, dene, kapat) → elle yedek → canlı (yayinla.sh)
```

### Canlıya ilk geçiş

**1. Hazırlık (deneme ortamında)**
- [ ] Hesap açma, davet, 2FA, duyuru, form, onay ve yanıt akışları sahte hesaplarla uçtan uca denendi.
- [ ] Yetkisiz erişim testleri geçiyor, `manage.py check --deploy` temiz.
- [ ] Yedek betiği deneme veritabanıyla çalıştırıldı, geri yükleme provası (bölüm 8) yapıldı.

**2. Canlı ortamın kurulması**
- [ ] Alan adı, `panel.` alt alan adı ve TLS sertifikası çalışıyor.
- [ ] Teknik erişim için VPN (WireGuard) kuruldu; Django Admin ve SSH yalnızca VPN'den erişilebiliyor.
- [ ] Canlı `.env` ve `secrets/` dosyaları oluşturuldu (deneme ortamınınkilerden farklı).
- [ ] Yedek anahtarları en az iki kişi için üretildi, `alicilar.txt` dolduruldu (bölüm 4).
- [ ] Otomatik yedek ve cron çalışıyor, izleme servisi sinyal alıyor (bölüm 5).
- [ ] Yedekler en az bir, mümkünse iki geliştirici bilgisayarına çekiliyor ve çekme sinyali geliyor (bölüm 7).
- [ ] E-posta gönderimi test edildi (bir test hesabına davet).
- [ ] Aydınlatma metni ve açık rıza metni hukuk birimiyle hazırlandı ve panele girildi.

**3. İlk hesap**
- [ ] Canlı veritabanı boş olarak başlatıldı (`migrate`). İçinde hiç test verisi yok.
- [ ] Teknik sorumlu `manage.py ilk_yonetici` ile Başkan hesabını açtı.
- [ ] Başkan ilk girişte 2FA'yı kurdu, Başkan Yardımcısı'nı ve diğer Yönetim Kurulu üyelerini davet etti; onlar da birim üyelerini davet etti.
- [ ] İlk elle yedek alındı: `sudo /opt/diyak/ops/yedekle.sh elle ilk-kurulum`

**4. Sessiz açılış (1–2 hafta)**
- Panel yalnızca ekip tarafından kullanılır: duyurular yazılır, ekip sayfası doldurulur, bir deneme formu ekip içinde doldurulur.
- Herkese açık formlar henüz duyurulmaz. Sorunlar gerçek kullanıcılar gelmeden yakalanır.
- Ekip içi deneme formunun yanıtları gerçek kişilere ait olduğu için diğer yanıtlar gibi korunur ve saklama süresi sonunda silinir.

**5. Açılış**
- İlk herkese açık form ve duyuru yayımlanır. İlk hafta yedekler, izleme ve hata kayıtları her gün kontrol edilir.
