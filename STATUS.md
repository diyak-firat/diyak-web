# STATUS

Projenin anlık durumu. Her iş bitince güncellenir. Agent'lar işe başlamadan önce bu dosyayı okur, iş bitince günceller.

**Faz:** 1 — statik site
**Son güncelleme:** 2026-11-27

## Şu an

- [ ] Fırat Üniversitesi ve SKS logolarını resmî kaynaklardan bul, doğrula, SVG olarak `frontend/public/logolar/` altına ekle
- [ ] Kaynaklar sayfası (`/kaynaklar`), BibTeX kopyalama düğmesi
- [ ] Gündem için RSS beslemesi (`@astrojs/rss`, onaylandı)

## Sıradaki

**Repo ve yayın**
- [ ] Organizasyonda en az iki owner (geliştirici + akademik danışman veya bir yönetim kurulu üyesi)
- [ ] Bilgi İşlem'den alt alan adı talep et (ör. `diyak.firat.edu.tr`), `astro.config.mjs` içindeki `site` değerini güncelle

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
- [ ] Sosyal medya önizlemesi için Open Graph görseli
- [ ] GitHub Actions'a testleri ekle (ilk testler yazıldığında, `.github/workflows/frontend.yml`)

## Faz 2 (backend)

Faz 1 kısa tutulur: Faz 1'de duyuru yazma aracı kurulmaz, hızla Faz 2'ye geçilir (K-18). Plan: [backend/README.md](backend/README.md), panel: [docs/PANEL.md](docs/PANEL.md).

- [ ] Hosting yeri kararı (KVKK — yurt içi / üniversite sunucusu / yurt dışı)
- [ ] Veri sorumlusunun kim olduğunu (topluluk mu, üniversite mi) SKS ile yazılı netleştir
- [ ] Aydınlatma metni ve açık rıza metni taslakları, üniversitenin hukuk birimiyle (formların ön şartı)
- [ ] E-posta gönderim servisi (davet, onay bildirimi, kayıt onayı): önce Bilgi İşlem'in SMTP sunucusu sorulur; yurt dışındaki bir servis KVKK açısından yurt dışına aktarım sayılır
- [ ] Bütçe: giderlerin nereden karşılanacağı (SKS?) ve ödeme yapılan hesapların topluluk adına açılması
- [ ] Django projesi iskeleti, roller, Django Admin
- [ ] Object storage ve dosya yükleme akışı
- [ ] Yurt içi VPS seç: 4 GB RAM; paket yükseltmeyi yeniden kurulum gerektirmeden destekleyen bir sağlayıcı (K-19)
- [ ] Deneme ortamı aynı sunucuda, ayrı Docker Compose projesi olarak (OPERASYON.md §12)
- [ ] Yedeklerin en az bir, mümkünse iki geliştirici bilgisayarına çekilmesi ve çekme sinyali (OPERASYON.md §7) — başlangıçta sunucu dışındaki tek kopya
- [ ] Kalıcı uzak yedek deposu: üniversiteden depolama alanı iste (bulununca `yedek.env` içindeki `UZAK` doldurulur)
- [ ] Canlıya ilk geçiş kontrol listesi (OPERASYON.md §12)
- [ ] Panel adresi (`panel.<alan-adi>`) ve teknik erişim için VPN (Django Admin, SSH)
- [ ] Yedek anahtarlarını en az iki kişi için üret (OPERASYON.md §4)
- [ ] Otomatik yedek, cron ve izleme servisi (OPERASYON.md §5)
- [ ] Yayın betiği: elle yedek olmadan migrate çalıştırmasın (OPERASYON.md §6)
- [ ] İlk geri yükleme provası (OPERASYON.md §8)
- [ ] Sentry ve uptime/disk izleme

**Yönetim paneli** (PANEL.md §12)
- [ ] A1 · Temel ve hesaplar: davet, dönemlik rol atama, 2FA, giriş kilidi, yeni cihaz uyarısı, işlem kaydı
- [ ] A2 · Onay altyapısı ve duyurular: Yönetim Kurulu onayı, metin editörü, önizleme, API, Astro bağlantısı, Markdown'dan aktarım
- [ ] A3 · Ekip sayfası: panelden yönetim, yayın onayı, fotoğraflar, `ekip.json`'dan aktarım. Akademik danışman ve ekip üyelerinin gerçek bilgileri ilk kez bu arayüzden girilecek; panelin ilk gerçek testi olur (o zamana kadar `ekip.json` yer tutucu kalır)
- [ ] A4 · Etkinlikler ve formlar: hazır ama kaldırılabilir alanlar, zorunlu aydınlatma onayı, onay kontrol listesi, herkese açık form sayfası
- [ ] A5 · Yanıtlar ve saklama: tablo, CSV, otomatik silme
- [ ] A6 · Cilalama ve kullanım rehberi

### Operasyon kayıtları

Aylık geri yükleme provaları buraya yazılır: `tarih · yedek adı · kayıt sayıları · sorun`

- (henüz yok)

## Bekleyen kararlar

- **API katmanı:** Django Ninja mı, Django REST Framework mü? (Faz 2 başında)
- **Panel metin editörü:** Konuşulacak. Öneri: Tiptap (çekirdeği MIT lisanslı, araç çubuğu kendi tasarımımızla yapılabiliyor); daha sade alternatif: Trix. A2'den önce karar verilip DECISIONS.md'ye yazılacak.

## Tamamlananlar

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
