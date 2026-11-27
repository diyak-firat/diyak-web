# AGENTS.md

Bu dosya, bu repoda kod yazan agent'lar (Claude Code, Codex vb.) ve yeni katılan geliştiriciler içindir. Bir işe başlamadan önce bu dosyayı ve [STATUS.md](STATUS.md) dosyasını oku.

## Proje

Fırat Üniversitesi Doğal Dil İşleme ve Yapay Zekâ Araştırmaları Topluluğu (DİYAK) web sitesi. Site Türkçedir, hedef kitlesi öğrenciler, akademisyenler ve diğer üniversitelerin topluluklarıdır.

- **Faz 1 (şu an):** `frontend/` altında statik Astro sitesi. İçerik `frontend/src/content/` ve `frontend/src/data/` altındaki Markdown/JSON dosyalarında.
- **Faz 2 (sonra):** `backend/` altında Django + PostgreSQL API. Henüz kod yok, plan [backend/README.md](backend/README.md) dosyasında.

Mimari: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · Kararlar: [docs/DECISIONS.md](docs/DECISIONS.md) · Tasarım: [docs/DESIGN.md](docs/DESIGN.md)
Faz 2: Yönetim paneli ve formlar [docs/PANEL.md](docs/PANEL.md) · Operasyon [docs/OPERASYON.md](docs/OPERASYON.md)

## Komutlar

Tüm frontend komutları `frontend/` klasöründe çalışır.

```bash
npm install
npm run dev       # geliştirme sunucusu, http://localhost:4321
npm run check     # tip ve şablon denetimi — her işin sonunda çalıştır
npm run build     # üretim derlemesi — her işin sonunda çalıştır
npm run format    # Prettier
```

## Bir iş nasıl yapılır

1. `STATUS.md` dosyasında işin karşılığını bul. Yoksa kullanıcıya sor ya da "Şu an" bölümüne ekle.
2. Güncel main'den branch aç: `feat/…`, `fix/…`, `docs/…`, `refactor/…`, `chore/…`.
3. Küçük ve tek amaçlı değişiklikler yap. Bir PR tek bir iş yapar.
4. Bitirince `npm run check` ve `npm run build` hatasız geçmeli.
5. Sayfayı 1280px (masaüstü) genişlikte kontrol et. Telefonda (390px) yalnızca taşma ve kırılma olmadığına bak; mobil tasarımın toparlanması ayrı bir iş (STATUS.md, K-20). Kullanıcı istemedikçe mobil görünüm üzerinde ayrıca çalışma.
6. `STATUS.md` dosyasını güncelle: biten işi "Tamamlananlar"a taşı, yeni ortaya çıkan işleri ekle.
7. Yeni bir mimari karar aldıysan `docs/DECISIONS.md` dosyasına ekle.

## Commit mesajları

Türkçe, Conventional Commits biçiminde, emir kipinde ve küçük harfle:

```
feat(gundem): etiket filtresi ekle
fix(ekip): telefonda fotoğraf taşmasını düzelt
docs: kurulum adımlarını güncelle
refactor(header): menü betiğini sadeleştir
chore: bağımlılıkları güncelle
```

Türler: `feat` yeni özellik, `fix` hata düzeltme, `docs` doküman, `style` görünümü değiştirmeyen biçim düzenlemesi, `refactor` davranışı değiştirmeyen kod düzenlemesi, `chore` bakım işleri.

## Tasarım kuralları (kısa hali — ayrıntı DESIGN.md'de)

- Renkleri yalnızca `frontend/src/styles/tokens.css` içindeki değişkenlerden al. Yeni renk ekleme, kod içine sabit renk yazma.
- Yazı tipleri: başlıklar **Source Serif 4**, gövde **IBM Plex Sans**, tarih/etiket/kod **IBM Plex Mono**. Başka yazı tipi ekleme.
- Mercan vurgu rengi (`--accent`) az kullanılır: logodaki tek çizgi, kök biçimbirimi, aktif menü alt çizgisi gibi küçük yerlerde.
- **Yasak:** gradyanlar, glassmorphism, parlayan sinir ağı veya robot görselleri, emoji, hazır UI kitleri (Bootstrap, shadcn vb.), her kutuya gölge ve büyük köşe yuvarlaklığı, "Yapay zekânın gücünü keşfedin" tarzı pazarlama dili.
- İkonlar satır içi, çizgi (stroke) SVG olur ve `aria-hidden="true"` taşır.
- Her sayfa `lang="tr"`. CSS `text-transform: uppercase` bu sayede "i" harfini doğru şekilde "İ" yapar.
- Dokunma hedefleri en az 44px. Metin kontrastı en az 4.5:1. Klavye odağı görünür olmalı.
- Gereksiz JavaScript yok. Etkileşim (filtre, mobil menü) küçük, bağımsız `<script>` blokları ile yapılır ve JS kapalıyken de içerik okunabilir kalır.

## İçerik kuralları

- Yer tutucular köşeli parantez içinde yazılır: `[Ad Soyad]`, `[GG Ay 2026]`. Uydurma isim, tarih, istatistik veya alıntı yazma.
- **Tüzük 9/7:** Sitede Fırat Üniversitesi ve SKS adı veya logosu bulunmalı (üst menü ve alt bilgi).
- **Tüzük 9/8:** Sponsor sözleşmesi yoksa ticari kuruluşların logosu kullanılmaz.
- Akademik Danışman, Yönetim Kurulu'nun parçası değildir (Tüzük Madde 6). Ekip sayfasında ayrı bölümde durur.
- Ekip sayfasındaki fotoğraf, e-posta ve bağlantılar ancak kişinin yazılı onayıyla yayımlanır (KVKK).

## Güvenlik ve KVKK

- Şifre, token, API anahtarı asla repoya girmez. `.env` dosyaları `.gitignore`'da. Örnek değerler `.env.example` dosyasına yazılır.
- Sitede form ile kişisel veri toplanmaz (Faz 1). Üyelik başvurusu PDF form ile yapılır.
- Faz 2'de kişisel veri işleyen her özellik için `docs/ARCHITECTURE.md` dosyasındaki güvenlik ve KVKK bölümü geçerlidir.

## Veritabanı ve yedek kuralları

Başvurular, üye kayıtları ve etkinlik kayıtları topluluğun en önemli verisidir. Bu kurallar istisnasız uygulanır. Ayrıntılı yedek ve kurtarma süreci: [docs/OPERASYON.md](docs/OPERASYON.md).

**Sunucular sana kapalı**
- Deneme (staging) veya canlı sunucuya asla bağlanma, orada komut çalıştırma, erişim bilgisi (SSH anahtarı, veritabanı şifresi, `.env`) isteme veya okumaya çalışma.
- Yedek dosyalarını (`*.dump`, `*.age`) açma, okuma, repoya ekleme.
- Gerçek kişisel veriyle çalışma. Yerel geliştirmede sahte veri (fixture, factory) kullan.

**Migration içeren her değişiklikte**
1. PR açıklamasının "Migration" bölümünü doldur: hangi tablo/alan değişiyor, veri kaybı riski var mı, nasıl geri alınır.
2. İş bittiğinde kullanıcıya açıkça şunu yaz:
   > Bu değişiklik migration içeriyor. Yayından önce sunucuda elle yedek alınmalı: `sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi`
3. Veri silen veya dönüştüren migration'larda (`RemoveField`, `DeleteModel`, tür değiştiren `AlterField`, `RunPython` ile veri taşıma) bunu PR'da **kalın** olarak belirt ve mümkünse iki aşamalı yap: önce yeni alanı ekle ve veriyi taşı, eski alanı ancak sonraki bir sürümde sil.
4. Var olan, main'e birleşmiş bir migration dosyasını asla düzenleme veya silme. Düzeltme yeni bir migration ile yapılır.

**Yerel geliştirmede bile geri dönüşsüz komutlardan önce**
Şu komutlardan önce kullanıcıdan açık onay al ve önce yerel bir yedek al:
`manage.py flush`, `manage.py migrate <app> zero`, `dropdb`, `DROP`/`TRUNCATE`/koşulsuz `DELETE`, migration dosyalarını silip yeniden üretmek, `docker compose down -v`, `docker volume rm`.

```bash
docker compose exec -T db pg_dump -U diyak -Fc diyak > yerel_yedek_$(date +%Y%m%d_%H%M).dump
```

Bu yerel yedek dosyası repoya girmez (`.gitignore`'da).

## Panel ve formlar (Faz 2)

Panel üzerinde çalışırken [docs/PANEL.md](docs/PANEL.md) tek kaynaktır.

- §9'daki güvenlik kuralları zorunludur. Hiçbirini gevşetme; gerekirse önce sor.
- Her yeni görünüm için yetkisiz erişim testi yaz (giriş yapmamış, yanlış rol, süresi dolmuş rol, başka formun sahibi). Test yoksa iş bitmiş sayılmaz.
- Giriş, oturum, 2FA, HTML temizleme ve dosya yükleme için hazır kütüphaneleri kullan, kendi çözümünü yazma.
- Yeni form alan türü ekleme, aydınlatma onayını isteğe bağlı yapma, Yönetim Kurulu onayını atlayan bir yol açma, kapsam dışı (§2) özellik ekleme. Önce sor.
- `|safe` / `mark_safe` yalnızca `nh3` ile temizlenmiş duyuru gövdesinde kullanılabilir.

## Sormadan yapma

Şunlar için önce kullanıcıya sor:

- Yeni bir npm/pip bağımlılığı eklemek
- Mimariyi, klasör yapısını veya teknoloji seçimini değiştirmek
- Tasarım sistemine (renk, yazı tipi, ana bileşen) dokunmak
- Backend (Faz 2) koduna başlamak
- Dosya silmek veya toplu yeniden adlandırma yapmak
- Veri silen veya dönüştüren bir migration yazmak
- Yukarıda sayılan geri dönüşsüz veritabanı komutlarını çalıştırmak
- `docs/OPERASYON.md` içindeki yedek, yayın veya kurtarma adımlarını değiştirmek
- `docs/PANEL.md` içindeki kapsamı, veri modelini veya güvenlik kurallarını değiştirmek
