# STATUS

Projenin anlık durumu. Her iş bitince güncellenir. Agent'lar işe başlamadan önce bu dosyayı okur, iş bitince günceller.

**Faz:** 1 — statik site yayında değil; Faz 2 paneli geliştiriliyor (A1 bitti)
**Son güncelleme:** 2026-11-28

## Şu an

- [ ] **A4 · Etkinlikler ve formlar** (PANEL.md §12): başlamadan önce aydınlatma metni taslağının (hukuk birimi) durumu ve spam koruması için Redis'in eklenmesi konuşulacak

## Sıradaki

**Repo ve yayın**
- [ ] Organizasyonda en az iki owner (geliştirici + akademik danışman veya bir yönetim kurulu üyesi)
- [ ] Organizasyon ayarları → Code security: **Secret scanning** ve **Push protection**'ı organizasyon genelinde aç (`diyak-web` reposunda 2026-11-28'de açıldı)
- [ ] Gizli operasyon bilgileri için yer: organizasyonda private `diyak-ops` reposu veya parola yöneticisi; erişim yalnızca teknik sorumlular ve Başkan
- [ ] Bilgi İşlem'den alt alan adı talep et (ör. `diyak.firat.edu.tr`), `astro.config.mjs` içindeki `site` değerini güncelle. RSS ve canonical bağlantıları bu değerden üretilir; şu an `diyak.example.org`

**Gerçek içerik ve görseller**
- [ ] Topluluk e-postası ve sosyal medya bağlantıları → `frontend/src/config/site.ts`
- [ ] Üye kayıt formu (Ek-4) PDF → `frontend/public/belgeler/uye-kayit-formu.pdf`
- [ ] Örnek gündem gönderilerini (`ornek: true`) gerçek gönderilerle değiştir
- [ ] Kuruluş yılını ve Hakkımızda metnini yönetimle son kez gözden geçir

## Yayına hazırlanırken

Siteyi bir bağlantıyla ekibe/danışmana göstermek gerektiğinde veya alan adı geldiğinde yapılır (K-07 geçerli, yalnızca zamanı ertelendi).

- [ ] Cloudflare Pages'i repoya bağla: kök klasör `frontend`, komut `npm run build`, çıktı `dist`, ortam değişkeni `NODE_VERSION=22`; GitHub uygulaması yalnızca `diyak-web` reposuna izinli

## Masaüstü tamamlandıktan sonra

- [ ] **Mobil görünümü toparla** (K-20): sitenin tüm sayfaları ve panel telefon için ayrıca ele alınacak. Başlarken sorunlar sayfa sayfa listelenip buraya yazılacak.

## Birikmiş işler

- [ ] İngilizce sürüm (Astro i18n, `/en/` altında). Menüdeki EN bağlantısı o zaman eklenecek
- [ ] GitHub Actions'a testleri ekle (ilk testler yazıldığında, `.github/workflows/frontend.yml`)

## Faz 2 (backend)

Faz 1 kısa tutulur: Faz 1'de duyuru yazma aracı kurulmaz, hızla Faz 2'ye geçilir (K-18). Plan: [backend/README.md](backend/README.md), panel: [docs/PANEL.md](docs/PANEL.md).

- [ ] Hosting yeri kararı (KVKK — yurt içi / üniversite sunucusu / yurt dışı)
- [ ] Veri sorumlusu: üniversitenin "Öğrenci Topluluğu Üyesi İlgili Kişi Aydınlatma Metni"nde Fırat Üniversitesi olarak geçiyor (2026-11-28). Etkinlik formları için uygun metin SKS ve kvkk@firat.edu.tr ile netleştirilecek (e-posta alanı, üye olmayan katılımcılar, saklama süresi)
- [ ] Aydınlatma metni ve açık rıza metni taslakları, üniversitenin hukuk birimiyle (formların ön şartı)
- [ ] E-posta gönderim servisi (davet, onay bildirimi, kayıt onayı): önce Bilgi İşlem'in SMTP sunucusu sorulur; yurt dışındaki bir servis KVKK açısından yurt dışına aktarım sayılır
- [ ] Bütçe: giderlerin nereden karşılanacağı (SKS?) ve ödeme yapılan hesapların topluluk adına açılması
- [ ] Yayın hazırlığı (Compose): Caddy (TLS, statik dosyalar ve `/medya/` altındaki yüklenen görseller), `collectstatic`, `manage.py gece_gorevleri` için her gece çalışan zamanlayıcı; sunucuda `secrets/` dosya izinleri (web konteyneri `uid 10001` ile çalışır, `chmod 600` + root sahipliği onun okumasını engeller; OPERASYON.md §3 buna göre güncellenmeli)
- [ ] Object storage ve dosya yükleme akışı
- [ ] Yurt içi VPS seç: 4 GB RAM; paket yükseltmeyi yeniden kurulum gerektirmeden destekleyen bir sağlayıcı (K-19)
- [ ] Deneme ortamı aynı sunucuda, ayrı Docker Compose projesi olarak (OPERASYON.md §12)
- [ ] Yedeklerin en az bir, mümkünse iki geliştirici bilgisayarına çekilmesi ve çekme sinyali (OPERASYON.md §7) — başlangıçta sunucu dışındaki tek kopya
- [ ] Kalıcı uzak yedek deposu: üniversiteden depolama alanı iste (bulununca `yedek.env` içindeki `UZAK` doldurulur)
- [ ] Canlıya ilk geçiş kontrol listesi (OPERASYON.md §12)
- [ ] Panel adresi (`panel.<alan-adi>`) ve teknik erişim için VPN (Django Admin, SSH)
- [ ] Yedek anahtarlarını en az iki kişi için üret (OPERASYON.md §4)
- [ ] Otomatik yedek, cron ve izleme servisi (OPERASYON.md §5)
- [ ] Yedeğe `media` volume'ünü (ekip fotoğrafları, K-27) ekle; OPERASYON.md §5 buna göre güncellenmeli (onay gerek)
- [ ] Gece görevi: hiçbir kişi kaydında ve onaylı/bekleyen ekip değişikliğinde kullanılmayan fotoğraf dosyalarını sil
- [ ] Yayın betiği: elle yedek olmadan migrate çalıştırmasın (OPERASYON.md §6)
- [ ] İlk geri yükleme provası (OPERASYON.md §8)
- [ ] Sentry ve uptime/disk izleme

**Yönetim paneli** (PANEL.md §12)
- [ ] **Astro'nun gündemi `/api/duyurular/`'dan, ekip sayfasını `/api/ekip/`'ten çekmesi** (K-26: hosting kararından sonra). Aynı işte: yayımla ve yayından kaldırda Cloudflare Pages deploy hook'u (1 dakikalık pencerede birleştirme, Redis veya zamanlayıcı gerekir); geçişte gündemde gerçek Markdown gönderisi varsa `faz1_aktar` ile panele aktarma (şu an hepsi `ornek: true`, aktarılacak gönderi yok)
- [ ] Duyuruya kapak görseli (dosya yükleme akışı A3'te kurulunca)
- [ ] A3 · Ekip sayfası: panelden yönetim, yayın onayı, fotoğraflar, `ekip.json`'dan aktarım. Akademik danışman ve ekip üyelerinin gerçek bilgileri ilk kez bu arayüzden girilecek; panelin ilk gerçek testi olur (o zamana kadar `ekip.json` yer tutucu kalır)
- [ ] A4 · Etkinlikler ve formlar: hazır ama kaldırılabilir alanlar, zorunlu aydınlatma onayı, onay kontrol listesi, herkese açık form sayfası; etkinliğe isteğe bağlı **harita bağlantısı** (yalnızca Google Maps adresleri; yer adı panelde ve sitede tıklanınca haritayı açar; gömülü harita ve API anahtarı yok, 2026-11-28 kararı)
- [ ] A5 · Yanıtlar ve saklama: tablo, CSV, otomatik silme
- [ ] A6 · Cilalama: rehberi (`docs/PANEL-KULLANIM.md`) panelin içinde **Yardım** sayfası olarak göster; rehbere deneme ortamında sahte veriyle alınmış ekran görüntüleri ekle

### Operasyon kayıtları

Aylık geri yükleme provaları buraya yazılır: `tarih · yedek adı · kayıt sayıları · sorun`

- (henüz yok)

## Bekleyen kararlar

- (şu an yok)

## Tamamlananlar

- [x] Önbellek ve kısa ömürlü sayaçlar için Valkey servisi ve `django-redis` (K-28)
- [x] **A3 · Ekip sayfası** (PR #29 ve bu PR; K-27): dönem, grup ve kişi modelleri, Pillow ile fotoğraf işleme (EXIF silinir), onaylanan halin dondurulması, `/api/ekip/` (yalnızca yazılı yayın onaylı kişiler), Ekip ekranı (dönem açma, sitedeki bölümlerle başlatma, kişi ve fotoğraf, sıralama, önizleme), onay ekranı (sitedeki halden fark), rehber. `ekip.json`'daki kişiler yer tutucu olduğu için aktarılmadı; grup yapısı "sitedeki bölümlerle başlat" seçeneğiyle geliyor. Astro'nun ekip sayfasını API'den çekmesi gündemle birlikte (K-26)
- [x] **A2 · Onay altyapısı ve duyurular, panel tarafı** (PR #25, #26 ve bu PR): `Duyuru`, yalın `Etkinlik`, ortak onay akışı, `nh3` temizliği, Tiptap editörü (K-26), duyuru ekranları, onay ekranı, e-posta bildirimleri, `/api/duyurular/` (yalnızca yayımlanmış). Astro bağlantısı ve deploy hook ayrı iş
- [x] Panel kullanım rehberi → `docs/PANEL-KULLANIM.md` (şimdilik A1 ekranları; her aşamada genişler). Public repo kuralları AGENTS.md'ye eklendi
- [x] Panel: İşlem kaydı ekranı (eylem ve kişi filtresi, sayfalama; Yönetim Kurulu, Danışman, Teknik)
- [x] **A1 · Temel ve hesaplar** (PR #17–#20): dönemlik roller, davet (48 saat, tek kullanımlık), yetki kuralları, `denetim` işlem kaydı; şifre + TOTP girişi (Admin dahil), `django-axes` kilidi (IP saklanmaz), yeni cihaz uyarısı, oturum süreleri, `ilk_yonetici`; panel iskeleti ve menüsü, Kullanıcılar ekranı (teknik için 2FA sıfırlama ve kilit açma), Hesabım, `gece_gorevleri` (K-25)
- [x] Compose yerelde ilk kez çalıştırıldı (2026-11-28): migrate, testler, `/api/saglik/`
- [x] Backend iskeleti: Django 5.2 LTS, DRF (K-23 varsayılanları), e-posta ile giriş yapan `accounts.Kullanici`, `/api/saglik/`, ayarlar (base/development/test/production), Dockerfile, Compose (K-24), CI (`backend testleri`: migration, pytest, `check --deploy`, Bandit)
- [x] API katmanı kararı: Django REST Framework (K-23)
- [x] Open Graph görseli → `frontend/public/og.png` (kaynak `design/og/`), `og:*` ve `twitter:card` etiketleri
- [x] Astro 7.4.1 → 7.4.13 (güvenlik düzeltmesi GHSA-mh32-jxcr-mh9f); `npm audit` temiz
- [x] Tüzük PDF'i bozuk başlık bilgisi olmadan yeniden üretildi (içerik birebir aynı)
- [x] Gündem RSS beslemesi → `/gundem/rss.xml` (`<head>` ve alt bilgide bağlantı)
- [x] Kaynaklar sayfası (`/kaynaklar`): türlere göre gruplu, BibTeX açılır kutusu ve kopyalama düğmesi
- [x] Gündem arşivinde yıla göre gruplama (`/gundem`); filtrede boş kalan yıl gizlenir
- [x] Fırat Üniversitesi logosu resmî kurumsal kimlik kılavuzundan SVG olarak eklendi; SKS adıyla alt bilgide (K-22)
- [x] Tüzüğün son hâli eklendi → `frontend/public/belgeler/tuzuk.pdf`
- [x] Repo ayarları: yalnızca squash merge, birleşen dallar otomatik silinir
- [x] main koruması: PR zorunlu (onay 0, ikinci geliştirici gelince 1), yöneticiler dahil, force push ve silme kapalı, `check ve build` geçmeli
- [x] GitHub Actions: her PR'da `npm run check` ve `npm run build` → `.github/workflows/frontend.yml`
- [x] Git reposu açıldı, GitHub'a (`diyak-firat/diyak-web`) push edildi
- [x] İskelet yerelde doğrulandı (`npm run check`, `npm run build`)
- [x] Logo ve favicon referans PNG'lere göre yeniden çizildi: 6 satırlık "D" motifi
- [x] Tasarım prototipi onaylandı → `design/prototip.html`
- [x] Mimari ve teknoloji kararları yazıldı → `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`
- [x] Çalışma düzeni belirlendi → `CONTRIBUTING.md`
- [x] Astro iskeleti: ana sayfa, gündem listesi ve detay sayfası, ekip sayfası, 404
- [x] Operasyon rehberi: yedekleme, yayın, kurtarma → `docs/OPERASYON.md`
- [x] Yönetim paneli tasarım belgesi → `docs/PANEL.md` (kararlar: K-15 kendi panelimiz, K-16 esnek form, K-17 giriş ve yetkiler, K-18 Faz 1 kısa + ekip panelden)
