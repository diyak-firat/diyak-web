# Kararlar

Projede alınan önemli kararlar ve gerekçeleri. Yeni bir karar alındığında en alta eklenir. Bir karar değişirse eskisi silinmez, "Yerini aldı: K-xx" notu düşülür.

Biçim: **Karar** · **Gerekçe** · **Bedeli** (vazgeçtiğimiz şey)

---

### K-01 · Statik site ile başla, backend'i ihtiyaç doğunca ekle
**Tarih:** 2026-10-27
**Karar:** Faz 1 tamamen statik (Astro). Django backend, ilk dinamik ihtiyaçla (üyelik, başvuru, dosya yükleme) Faz 2'de eklenir.
**Gerekçe:** Bugünkü içerik seyrek değişiyor. Statik site ücretsiz barınır, bakım istemez, saldırı yüzeyi yok denecek kadar azdır.
**Bedeli:** Faz 2'de backend ile frontend'i bağlama işi ayrıca yapılacak.

### K-02 · Monorepo: `frontend/` ve `backend/` aynı repoda
**Tarih:** 2026-11-03
**Karar:** Tek repo, iki ana klasör.
**Gerekçe:** Küçük ekip, tek yerde doküman ve iş takibi. Agent'lar tüm bağlamı tek repoda görür.
**Bedeli:** Yayın ayarlarında kök klasörü belirtmek gerekiyor (`frontend`).

### K-03 · Frontend: Astro
**Tarih:** 2026-10-27
**Karar:** Astro, `output: 'static'`, TypeScript strict.
**Gerekçe:** İçerik odaklı sitelerde neredeyse hiç JS göndermeden hızlı HTML üretir. Markdown içerik ve i18n desteği yerleşik. Öğrenmesi kolay.
**Bedeli:** Hugo kadar "yıllarca dokunmadan çalışan" bir ikili değil; Node bağımlılıklarının güncel tutulması gerekir.

### K-04 · Stil: sade CSS ve tasarım değişkenleri, UI kit yok
**Tarih:** 2026-10-27
**Karar:** Renkler, yazı tipleri ve boşluklar `tokens.css` içinde. Bootstrap, Tailwind UI, shadcn gibi hazır kitler kullanılmaz.
**Gerekçe:** Hazır kitler sitenin "yapay zekâ ile üretilmiş" gibi görünmesinin başlıca nedeni. Tasarım sistemi küçük, sade CSS yeterli.
**Bedeli:** Bileşenleri kendimiz yazıyoruz.

### K-05 · Yazı tipleri kendi sunucumuzdan
**Tarih:** 2026-11-03
**Karar:** Source Serif 4, IBM Plex Sans, IBM Plex Mono `@fontsource` paketleriyle siteyle birlikte sunulur.
**Gerekçe:** Google Fonts'a istek, ziyaretçi IP'sinin yurt dışına gitmesi demek (KVKK). Ayrıca daha hızlı ve çevrim dışı çalışır.
**Bedeli:** Yok denecek kadar az; paket boyutu birkaç yüz KB artar.

### K-06 · Faz 1 içeriği repoda: Markdown ve JSON
**Tarih:** 2026-11-03
**Karar:** Gündem gönderileri `src/content/gundem/*.md`, ekip `src/data/ekip.json`, kaynaklar `src/data/kaynaklar.json`.
**Gerekçe:** Veritabanı gerekmez, her değişiklik git geçmişinde izlenir, şema hatası derlemede yakalanır.
**Bedeli:** Kod bilmeyenler için GitHub web arayüzü gerekir (bkz. CONTENT.md). İçerik paneli kararı bekliyor.

### K-07 · Yayın: Cloudflare Pages
**Tarih:** 2026-10-27
**Karar:** Statik site Cloudflare Pages'te. main'e birleşen her commit yayına çıkar, her PR için önizleme linki üretilir.
**Gerekçe:** Ücretsiz, sunucu bakımı yok, PR önizlemesi inceleme sürecini kolaylaştırıyor.
**Bedeli:** Statik site yurt dışında barınıyor. Faz 1'de kişisel veri toplanmadığı için sorun değil. Faz 2'de kişisel veri işleyen backend için ayrı karar gerekecek.

### K-08 · Backend: Django 5.2 LTS + PostgreSQL (Faz 2)
**Tarih:** 2026-10-27
**Karar:** Django, PostgreSQL, Redis, Celery/RQ, S3 uyumlu object storage.
**Gerekçe:** Ekip Python biliyor. Kimlik doğrulama, yetkilendirme, CSRF, migration ve Django Admin hazır. Agent'lar Django'yu iyi yazıyor. LTS sürüm uzun süre güvenlik güncellemesi alır.
**Bedeli:** Node tabanlı bir full-stack çözüme göre iki ayrı dil ve çalışma ortamı.

### K-09 · Uygulama durumsuz (stateless)
**Tarih:** 2026-10-27
**Karar:** Oturumlar Redis'te veya veritabanında, dosyalar object storage'da. Uygulama sunucusunda kalıcı veri tutulmaz.
**Gerekçe:** Büyüdükçe kod değiştirmeden yeni kopya açılabilir. Ölçeklenebilirliğin asıl şartı bu.
**Bedeli:** Yerel geliştirmede de Redis ve MinIO gibi servisleri çalıştırmak gerekecek (Docker Compose ile).

### K-10 · Git çalışma düzeni
**Tarih:** 2026-11-03
**Karar:**
- Commit dili Türkçe, Conventional Commits biçiminde.
- Her iş branch'te, PR ile birleşir. Yalnızca "Squash and merge".
- CODEOWNERS yok; PR'ı müsait olan kişi inceler.
- Tek geliştirici varken onay şartı yok; ikinci geliştirici gelince en az 1 onay zorunlu.
- PR şablonu var; önce/sonra ekran görüntüsü zorunlu değil.
**Gerekçe:** Küçük ekip için yeterince düzenli, gereksiz yük getirmeyen bir akış.
**Bedeli:** —

### K-11 · Test ve CI zamanla eklenecek
**Tarih:** 2026-11-03
**Karar:** Başlangıçta GitHub Actions yok. İlk testler yazıldığında (en geç Faz 2 başında) her PR'da `check`, `build` ve testleri çalıştıran bir iş akışı eklenir.
**Gerekçe:** Henüz test edilecek mantık neredeyse yok. Yerelde `npm run check` ve `npm run build` yeterli.
**Bedeli:** Bu süreçte denetim geliştiricinin disiplinine kalıyor.

### K-12 · Akademik Danışman, Yönetim'den ayrı gösterilir
**Tarih:** 2026-10-29
**Karar:** Ekip sayfasında Danışman ayrı bölümde, Yönetim yalnızca Başkan ve Başkan Yardımcısı.
**Gerekçe:** Tüzük Madde 6'ya göre Yönetim Kurulu, Genel Kurul'un seçtiği öğrencilerden oluşur. Danışman Rektörlükçe görevlendirilir ve Genel Kurul'a denetçi olarak katılır. Diğer yönetim kurulu üyeleri birimlerde göründüğü için Yönetim bölümünde tekrar edilmez.
**Bedeli:** —

### K-13 · PostgreSQL'i kendimiz yönetiyoruz, yedekleme kurallara bağlı
**Tarih:** 2026-11-27
**Karar:** PostgreSQL yönetilen bir hizmette değil, kendi yurt içi VPS'imizde Docker içinde çalışır. Saatlik, günlük ve aylık otomatik yedek alınır; yedekler `age` ile şifrelenir ve yurt içinde sunucu dışına kopyalanır. Migration içeren her yayından önce elle yedek zorunludur; yayın betiği son 15 dakikada elle yedek görmezse migrate çalıştırmaz. Ayrıntı: OPERASYON.md.
**Gerekçe:** Veri çok küçük, yurt içinde yönetilen PostgreSQL seçeneği az. Kendi yönetimimizde veri yurt içinde kalır, ek maliyet olmaz. Elle yedek kuralı, işi agent'lara bıraktığımızda da yedeğin unutulmamasını garanti eder.
**Bedeli:** Yedek izleme, aylık geri yükleme provası ve sürüm yükseltmeleri bizim sorumluluğumuzda.

### K-14 · Yedeklerin ek kopyası geliştirici bilgisayarına çekilir
**Tarih:** 2026-11-27
**Karar:** Uzak depoya ek olarak, şifreli günlük/aylık/elle yedekler yetkili bir geliştiricinin bilgisayarına her gün **çekilir** (pull). Sunucuda bu iş için yalnızca `/yedek` klasörünü salt okunur gören, komut çalıştıramayan bir kullanıcı vardır.
**Gerekçe:** Ucuz ve yurt içinde kalan ek bir kopya. Çekme yöntemiyle sunucu ele geçirilse bile bilgisayara erişilemez ve sunucuda silinen yedekler bilgisayarda kalır.
**Bedeli:** Kişisel cihazda kişisel veri tutulduğu için asgari kurallar var: yalnızca şifreli dosya, anahtar parolasız durmaz, Yönetim Kurulu'na yazılı bildirim, görev bitince silme (OPERASYON.md §7). Disk şifreleme önerilir ama zorunlu değil. Bu kopya uzak deponun yerini tutmaz.

### K-15 · Yönetim paneli: kendi panelimiz (Wagtail ve Sveltia yerine)
**Tarih:** 2026-11-27
**Karar:** Faz 2'de yönetimin ve birim ekiplerinin kullanacağı panel, Django üzerinde kendimiz yazdığımız dar kapsamlı bir paneldir: duyurular, etkinlik kayıt formları, yanıtlar ve ekip sayfası. Panel sitenin `tokens.css` dosyasını kullanır, tamamen Türkçedir. Giriş, oturum, 2FA, HTML temizleme ve dosya yükleme gibi güvenlik parçaları hazır kütüphanelerle (Django auth, `django-otp`, `django-axes`, `nh3`) yapılır, kendimiz yazmayız. Faz 2'de gündem gönderileri ve ekip bilgileri Markdown/JSON'dan Django'ya taşınır. Yayına giden her şey Yönetim Kurulu onayından geçer. Django Admin yalnızca teknik sorumlular içindir. Tasarım: PANEL.md.
**Gerekçe:** Editörlerin ihtiyacı birkaç işle sınırlı. Wagtail'i Astro ile kullanmak ek parçalar (API, önizleme kurulumu) gerektiriyordu ve kullanmayacağımız çok özellik getiriyordu. Kendi panelimiz sitemizle aynı görünür, editörler GitHub hesabı açmak zorunda kalmaz.
**Bedeli:** Panelin bakımı bizde. Kapsam dar tutulmazsa devralacak ekibe yük olur. Zamanlı yayın, sürüm geçmişi gibi hazır özelliklerden vazgeçiliyor. İçerik türleri çok artarsa Wagtail'e geçiş yeniden değerlendirilir.

### K-16 · Esnek form oluşturucu; yalnızca aydınlatma onayı zorunlu
**Tarih:** 2026-11-27
**Karar:** "Form oluştur"a basıldığında ad, soyad, e-posta, bölüm ve sınıf alanları hazır gelir ama kaldırılabilir veya isteğe bağlı yapılabilir. Alan sayısında sınır yoktur. Alan türleri sınırlıdır (kısa/uzun metin, e-posta, tek/çoklu seçim, onay kutusu). Kaldırılamayan tek alan **aydınlatma metni onayıdır**; açık rıza alanı form ayarında istenirse eklenir. Her formun zorunlu aydınlatma metni ve saklama süresi vardır, süre dolunca yanıtlar otomatik silinir. Form, Yönetim Kurulu'nun panelde işaretlediği bir kontrol listesiyle onaylanmadan yanıta açılmaz. Herkese açık form sayfaları (`/kayit/<slug>/`) Django tarafından, sitenin tasarımıyla sunulur.
**Gerekçe:** Ekiplerin farklı etkinlikler için farklı bilgilere ihtiyacı var. Alan türlerinin sınırlı olması doğrulamanın form tanımından sunucuda otomatik üretilmesini sağlıyor. KVKK'nın asgari gereği (aydınlatma) sistem tarafından zorunlu tutuluyor; gereksiz veri istenip istenmediğini Yönetim Kurulu onayda denetliyor. Form durumu (açık, kapalı, kontenjan) canlı olduğu için statik sitede değil backend'de sunulması gerekiyor.
**Bedeli:** Özel nitelikli veri istenmesini sistem tek başına engelleyemiyor, onay kontrol listesine dayanıyor. Dosya yükleme, ödeme ve koşullu sorular ilk sürümde yok.

### K-17 · Panel girişi ve yetki dağıtımı
**Tarih:** 2026-11-27
**Karar:**
- Panel `panel.<alan-adi>` adresinde, internete açık; koruma hesap düzeyinde: zorunlu 2FA, hatalı giriş kilidi, yeni cihaz uyarısı. Django Admin ve SSH yalnızca VPN üzerinden.
- Hesaplar yalnızca davetle açılır. İlk Başkan hesabını teknik sorumlu açar; sonraki davetleri ve rol atamalarını **Başkan ve Başkan Yardımcısı** yapar.
- Roller: Yönetim Kurulu, Editör, Danışman (salt görüntüleme), Teknik. Form sahipliği form bazında verilir.
- Her rol atamasının bitiş tarihi vardır (varsayılan: dönem sonu). Süre dolunca rol kendiliğinden düşer; her dönem roller yeniden dağıtılır.
- Onaylar, Yönetim Kurulu üyesinin panele kendi hesabıyla girip onaylamasıyla verilir; e-postadaki bağlantıyla onay verilmez.
**Gerekçe:** Birim ekiplerinden teknik olmayan kişilerin VPN kurmasını istemek kullanımı zorlaştırır; 2FA'lı hesap koruması bu ölçekte yaygın ve yeterli bir yöntem. Rolleri tüzükteki görev sahiplerinin dağıtması yetkiyi topluluğun yapısıyla eşleştiriyor. Bitiş tarihli roller, öğrenci ekiplerinin her yıl değişmesine rağmen eski üyelerin yetkisinin açık kalmasını engelliyor.
**Bedeli:** Panel giriş sayfası internetten görülebilir; korumanın hesap düzeyinde iyi uygulanması (2FA zorunluluğu, kilit, testler) şart. Her dönem başında rollerin yeniden atanması gerekiyor.

### K-18 · Faz 1 kısa tutulur, ekip sayfası da panelden yönetilir
**Tarih:** 2026-11-27
**Karar:** Faz 1'de duyuru yazmak için ayrı bir araç (Sveltia vb.) kurulmaz; Faz 2'ye hızla geçilir. Faz 1'de gerekirse içerik GitHub web arayüzünden eklenir (CONTENT.md). Faz 2'de ekip sayfası da panelden, Yönetim Kurulu onayıyla yönetilir; sitede yalnızca yayın için yazılı onayı işaretlenmiş kişiler görünür.
**Gerekçe:** Kısa ömürlü geçici bir araç kurmak, sonradan sökülecek bir parça demek. Ekip bilgisi dönem başında toplu değiştiği için panelden ve onayla yönetilmesi ekip için kolaylık, KVKK açısından da kayıt sağlıyor.
**Bedeli:** Faz 2 gelene kadar içerik değişiklikleri geliştiricilerden geçiyor.

### K-19 · Başlangıçta tek sunucu: deneme ortamı aynı sunucuda, uzak yedek geliştirici bilgisayarlarında
**Tarih:** 2026-11-27
**Karar:** Başlangıçta 4 GB'lık tek bir yurt içi VPS kullanılır. Deneme (staging) ortamı aynı sunucuda, canlıdan tamamen ayrı bir Docker Compose projesi olarak çalışır: ayrı veritabanı, ayrı şifreler, yalnızca sahte veri, gerçek e-posta göndermez, yalnızca VPN'den erişilir ve yalnızca deneme yapılırken açıktır. Kalıcı bir uzak depo kurulana kadar yedeklerin sunucu dışındaki kopyası, şifreli yedeklerin en az bir, mümkünse iki geliştiricinin bilgisayarına her gün çekilmesidir (K-14); her çekme izleme servisine sinyal gönderir. Gerçek veri ilk günden canlı ortamda doğar, taşınması gerekmez. Ayrıntı: OPERASYON.md §7 ve §12.
**Gerekçe:** İkinci sunucu başlangıçta gereksiz maliyet. Trafik düşükken 4 GB iki ortama yetiyor. Deneme ortamındaki veri atılabilir olduğu için ileride ikinci sunucuya taşımak zahmetsiz.
**Bedeli:** Deneme ortamı canlıyla aynı kaynakları paylaşıyor; başvuru dönemlerinde kapalı tutulmalı. Sunucu dışındaki tek kopya kişisel bilgisayarlarda olduğu için çekmenin aksamadığı izleme servisiyle takip edilmeli. Kalıcı uzak depo (ör. üniversite depolama alanı) bulununca eklenecek.

### K-20 · Önce masaüstü, mobil görünüm sonra toparlanacak
**Tarih:** 2026-11-27
**Karar:** Mevcut mobil görünüm yeterli değil. Sitenin masaüstü tasarımı ve işlevleri tamamlandıktan sonra tüm sayfaların mobil görünümü ayrı bir çalışma olarak ele alınacak. O zamana kadar değişiklikler masaüstünde kontrol edilir; telefonda yalnızca taşma ve kırılma olmaması (yatay kaydırma, üst üste binme, kullanılamayan düğme) aranır.
**Gerekçe:** Tasarım masaüstünde oturmadan mobil için ayrıntılı çalışmak iki kez iş yapmak demek.
**Bedeli:** Bu süreçte telefon kullanıcıları için deneyim sınırlı. Panelin telefondan kullanılabilirliği (PANEL.md) bu mobil çalışmanın parçası olarak ele alınır.

### K-21 · Logo renkleri sitenin renk tanımlarından gelir
**Tarih:** 2026-11-27
**Karar:** Logo, `design/logo/` altındaki SVG'ler ve sitedeki `Logo.astro` olarak kullanılır. Renkleri `tokens.css` ile aynıdır: lacivert `#1E2142`, mercan `#E5533A`. İlk referans PNG'lerdeki biraz farklı tonlar esas alınmaz.
**Gerekçe:** Logo ile sitenin renkleri tek kaynaktan gelir, iki ayrı lacivert ve mercan oluşmaz.
**Bedeli:** Eski PNG'ler kullanılırsa ton farkı görünür; yeni basılı ve dijital materyaller `design/logo/` dosyalarından üretilmeli.

### K-22 · Kurum logoları: üst menüde yalnızca FÜ logosu, SKS adıyla
**Tarih:** 2026-11-27
**Karar:** Üst menüde Fırat Üniversitesi'nin resmî kurumsal kimlik kılavuzundan alınan dairesel logosu durur (`frontend/public/logolar/firat.svg`). SKS Daire Başkanlığı'nın ayrı bir logosu bulunmadığı için SKS üst menüde yer almaz; tam adı alt bilgide yazar.
**Gerekçe:** Tüzük 9/7 "adı ve/veya logosu" der; ad yeterli. SKS'nin kendi sitesi de FÜ logosunu kullanıyor. Var olmayan bir logo uydurulmaz.
**Bedeli:** SKS ileride resmî bir logo yayımlarsa üst menüye eklenip eklenmeyeceği yeniden değerlendirilir.

### K-23 · API katmanı: Django REST Framework
**Tarih:** 2026-11-27
**Karar:** Faz 2'deki API, Django REST Framework (DRF) ile yazılır. API'nin kapsamı dardır: Astro'nun derleme sırasında okuduğu salt okunur, yalnızca yayımlanmış içeriği döndüren uç noktalar (`/api/duyurular/`, `/api/etkinlikler/`, `/api/ekip/`; PANEL.md). Panel, formlar, giriş ve yetki DRF'den değil, Django görünümleri ve şablonlarından geçer. DRF'nin tarayıcıdan gezilebilen API arayüzü (browsable API) kapalı tutulur, yalnızca JSON döner.
**Gerekçe:**
- Topluluk her yıl el değiştirir. DRF en yaygın Django API kütüphanesi; yeni gelen öğrencinin bilme, sorusuna yanıt bulma ve agent'ların doğru kod yazma olasılığı en yüksek olan seçenek (ARCHITECTURE.md ilke 4: yaygın framework).
- Uzun ömürlü ve geniş bakım ekibine sahip; Django sürümleriyle uyumu düzenli izleniyor. Django Ninja daha genç ve bakımı daha dar bir ekibe dayanıyor.
- Serializer'larda alanlar tek tek yazılır (`fields = [...]`, `__all__` yasak). Ekip uç noktasının yalnızca yayın onaylı alanları döndürmesi (KVKK) böylece kodda açıkça görünür ve test edilir.
- Ninja'nın üstünlükleri (daha az kod, tip ipuçları, hız, otomatik OpenAPI) üç salt okunur uç noktada belirgin bir kazanç sağlamıyor.
**Bedeli:** DRF'de aynı iş için biraz daha fazla kod yazılır (serializer + view/viewset). Kullanılmayan özellikler bilinçli olarak kapalı tutulmalı:
- Genel ayarda yalnızca `JSONRenderer` açık (browsable API yok); varsayılan izin **kapalı** (`DEFAULT_PERMISSION_CLASSES = [IsAdminUser]`), varsayılan kimlik doğrulama sınıfı yok.
- Herkese açık uç noktalar görünüm düzeyinde açıkça `AllowAny` alır ve yalnızca `ReadOnlyModelViewSet` / `ListAPIView` gibi salt okunur görünümlerdir. Yazma işlemi API'den yapılmaz.
- Her uç nokta için "taslak/onaysız kayıt dönmüyor" ve "izin verilmeyen alan dönmüyor" testleri yazılır.

### K-24 · Compose dosyaları: sunucu tanımı kökte, yerel eklenti ayrı
**Tarih:** 2026-11-27
**Karar:** Repo kökündeki `docker-compose.yml` canlı ve deneme sunucusunda tek başına kullanılan servis tanımıdır (OPERASYON.md'deki `/opt/diyak/` yerleşimiyle uyumlu). Yerel geliştirme ayarları (`runserver`, kodun konteynere bağlanması, `127.0.0.1:8000` portu, test araçlarını içeren `dev` imajı) `docker-compose.dev.yml` içindedir ve yalnızca yerel `.env` dosyasındaki `COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml` satırıyla devreye girer. Sunucudaki `.env` bu satırı içermez. Gizli bilgiler Docker secrets ile `secrets/*.txt` dosyalarından okunur (`AD_FILE` ortam değişkenleri). Redis, MinIO ve ClamAV onları kullanan ilk özellikle eklenir.
**Gerekçe:** Yerelde ve sunucuda aynı servis tanımı çalışır; `docker compose exec -T db ...` gibi komutlar (AGENTS.md, OPERASYON.md) iki yerde de aynı kalır. `docker-compose.override.yml` kullanılmadı çünkü sunucuda repo çekildiğinde otomatik yüklenip geliştirme ayarlarını canlıya taşırdı.
**Bedeli:** Yerelde `.env` dosyası kurulmadan `docker compose` canlı ayarlarla başlar; kurulum adımı `backend/README.md` dosyasında.

### K-25 · Giriş güvenliği: django-otp, django-axes, segno; IP saklanmaz
**Tarih:** 2026-11-28
**Karar:** Panel girişi iki adımlıdır: Django'nun şifre doğrulaması, ardından `django-otp` ile TOTP kodu. Hatalı şifre kilidi `django-axes` ile yapılır (aynı e-postayla 5 hatalı denemede 30 dakika). Kurulum ekranındaki karekod `segno` ile üretilir. Django Admin de `OTPAdminSite` ile 2FA ister. Yeni cihaz uyarısı için tarayıcıya imzalı bir çerez bırakılır; sunucuda cihaz kaydı tutulmaz. Oturum süreleri (8 saat, 1 saat hareketsizlik) küçük bir ara katmanla uygulanır.
**Gerekçe:**
- Giriş, oturum ve 2FA için sınanmış kütüphaneler kullanılır (PANEL.md §1, AGENTS.md). `django-otp` hatalı kodlarda bekleme süresi uygular; ayrıca yazmaya gerek kalmaz.
- `segno` saf Python'dur, bağımlılığı yoktur ve `django-otp`'nin desteklediği iki karekod kütüphanesinden biridir. `qrcode` + Pillow'a göre daha hafif.
- PANEL.md §6 IP saklamayı yasaklar. Axes'in IP alanı `AXES_CLIENT_IP_CALLABLE` ile boş bırakılır, kilit yalnızca e-postaya göre uygulanır. Axes aynı e-postanın denemelerini tarayıcı bilgisinden bağımsız topladığı için tarayıcı değiştirerek kilit atlatılamaz (testi var); bu yüzden `axes.W006` uyarısı susturuldu. Axes'in ayrıntılı logları kapalıdır (`AXES_VERBOSE=False`), loglara e-posta yazılmaz.
**Bedeli:** IP'ye göre kilit olmadığı için biri bir kullanıcının e-postasını bilerek o hesabı 30 dakika kilitleyebilir. Küçük bir kullanıcı kitlesinde kabul edilebilir; sorun olursa yeniden değerlendirilir. Herkese açık formların IP başına sınırı (Redis'te kısa süreli sayaç) ayrı bir iştir (A4).

### K-26 · Panel metin editörü: Tiptap; Astro–API bağlantısı sonra
**Tarih:** 2026-11-28
**Karar:** Panelde duyuru metni Tiptap ile yazılır. Araç çubuğu PANEL.md §9'daki izin listesiyle sınırlıdır: kalın, italik, başlık (h2/h3), madde ve numaralı liste, alıntı, bağlantı. Tiptap npm paketleri tek bir JavaScript dosyasına derlenir ve bu dosya backend'in statik dosyalarına konur; Docker imajı Node gerektirmez. Editör yalnızca kolaylıktır: sunucu, gelen HTML'i her kayıtta `nh3` ile temizler. Astro'nun gündemi `/api/duyurular/`'dan çekmesi A2'nin panel ve API kısmı bittikten sonra, hosting kararı verilince ayrı bir işte yapılır.
**Gerekçe:**
- Tiptap'ın çekirdeği MIT lisanslıdır, hazır bir arayüz dayatmaz; araç çubuğu sitenin tasarımıyla (`tokens.css`) yazılabilir. Trix daha sade ama kendi görünümünü ve izin listemizde olmayan öğeleri (ör. ek dosya) getirir.
- Astro'yu API'ye bağlamak site derlemesini çalışan bir backend'e bağımlı kılar. Hosting (KVKK) kararı verilmeden bunu yapmak siteyi yayınlanamaz hale getirebilir.
**Bedeli:** Panel için küçük bir JS derleme adımı olur (PANEL.md §11'deki "metin editörü tek istisnadır" kuralı). Derlenmiş dosya repoda tutulur; paket güncellenince yeniden derlenir.

### K-27 · Ekip fotoğrafları: Pillow ile işlenir, sunucu diskinde durur
**Tarih:** 2026-11-28
**Karar:** Panelden yüklenen ekip fotoğrafları Pillow ile açılıp doğrulanır, döndürme bilgisine göre çevrilir, kare kırpılıp 800×800'e küçültülür ve JPEG olarak **yeniden kodlanır** (EXIF ve gömülü ek veri atılır). Dosyalar şimdilik sunucu diskinde, Docker'ın `media` volume'ünde durur ve `/medya/` altından sunulur (canlıda Caddy). Her yükleme yeni bir dosyadır; onaylı ekip sayfası eski fotoğrafı göstermeye devam edebilir.
**Gerçekleşme şekli:** Ekip sayfası panelde serbestçe düzenlenen bir çalışma kopyasıdır. Onaya gönderilince o anki hali (yalnızca yazılı yayın onayı olan kişiler ve herkese açık alanlar) `ekip.Degisiklik` kaydına donmuş olarak yazılır; `/api/ekip/` en son onaylananı döndürür.
**Gerekçe:**
- ARCHITECTURE.md'deki akış (presigned URL, object storage, ClamAV) kişisel ve özel dosyalar (başvuru ekleri vb.) içindir. Ekip fotoğrafları herkese açık yayımlanacak görsellerdir ve yalnızca 2FA ile giriş yapmış panel kullanıcıları yükler.
- Object storage hosting kararına bağlı. Django'nun dosya depolama katmanı (`STORAGES`) sayesinde ileride kod değişmeden object storage'a geçilebilir.
- Yeniden kodlama, bir görüntü dosyasına gizlenmiş içeriğin yayına çıkmasını engeller; virüs taraması bu görseller için şart değildir.
**Bedeli:** `media` volume'ü veritabanı gibi yedeklenmeli (STATUS.md). Hiçbir sürümde kullanılmayan eski fotoğraf dosyaları birikir; temizliği gece görevine eklenecek.

### K-28 · Önbellek ve kısa ömürlü sayaçlar: Valkey + django-redis
**Tarih:** 2026-11-28
**Karar:** Herkese açık formların istek sınırı (IP başına sayaç) ve önbellek için Compose'a bir Valkey servisi eklendi; Django `django-redis` ile bağlanır (`REDIS_URL`). Kalıcılık kapalı (`--save ''`, `--appendonly no`), bellek 64 MB ile sınırlı. Port dışarı açılmaz. Testler bellek içi önbellek kullanır.
**Gerekçe:**
- PANEL.md §9 spam koruması için kısa süreli sayaç ister ve IP'nin veritabanına yazılmasını yasaklar (§6). Süreli anahtarlar (TTL) bunun için en basit yoldur; sayaçlar kendiliğinden silinir.
- Valkey, Redis'in Linux Foundation altındaki BSD lisanslı çatalıdır ve aynı protokolü konuşur. Redis 7.4 sonrası sürümlerin lisansı değişti; ileride lisans sorusu çıkmasın diye Valkey seçildi. `django-redis` ikisiyle de çalışır.
- Kalıcılık kapalı olduğu için yedeklenecek bir şey tutmaz; yeniden başlayınca sayaçlar sıfırlanır, bu kabul edilebilir.
**Bedeli:** Sunucuda bir konteyner daha (birkaç MB bellek). Valkey çökerse form gönderimi istek sınırı denetiminde hata vermemeli (A4'te ele alınır).

### K-29 · Form yanıtları 10 yıl saklanır; katılım işaretlenir
**Tarih:** 2026-11-28
**Karar:** Etkinlik formlarının ilk aydınlatma metni, Fırat Üniversitesi'nin "Öğrenci Topluluğu Üyesi İlgili Kişi Aydınlatma Metni"dir (üniversitenin açık rıza sistemi). Bu metin faaliyet ve üye kayıt listelerinin 10 yıl saklanacağını söyler; PANEL.md'deki "etkinlikten 90 gün sonra sil" önerisi kaldırıldı, varsayılan saklama süresi aydınlatma metnindeki süre (10 yıl) oldu. Süre dolunca yanıtlar yine otomatik silinir. Ayrıca etkinlikten sonra her kayıt için katılım (katıldı / katılmadı) işaretlenir; yeni formların yanıt tablosunda, tekil alanı daha önce "katılmadı" işaretli bir yanıtla eşleşen kişinin yanında bilgi notu çıkar.
**Gerekçe:** Kullanıcı kararı (2026-11-28). Kontenjanlı etkinliklerde, daha önce kayıt olup gelmeyen kişileri ikinci sıraya koymak topluluk için faydalı. Saklama süresi üniversitenin yayımladığı metinle uyumlu olmalı.
**Bedeli:**
- Katılımcı verisi 10 yıl panelde ve yedeklerde durur; yetki ve işlem kaydı kuralları bu yüzden daha önemli hale gelir.
- Metin e-posta adresini ve topluluk üyesi olmayan katılımcıları açıkça saymıyor. Formlarda yalnızca aydınlatma onayı zorunlu, diğer alanlar kaldırılabilir; hangi alanların sorulacağına form hazırlanırken ve Yönetim Kurulu onayında dikkat edilir. Etkinliklere özgü bir aydınlatma metni için SKS ve kvkk@firat.edu.tr'ye danışılması STATUS.md'de.

### K-30 · Form alan türleri, kayıt usulü ve editör ekleri
**Tarih:** 2026-11-28
**Karar:**
- Alan türlerine `acilir_liste`, `tarih` (tarih veya tarih-saat), `olcek` (başı ve sonu editörce ayarlanır, uç etiketleri isteğe bağlı) eklendi. Seçimli alanlarda isteğe bağlı "Diğer: ___" seçeneği var. `kisa_metin` alanına isteğe bağlı biçim denetimi geldi: öğrenci numarası veya telefon.
- Kayıt usulü form başına seçilir: **ilk gelen** (kontenjan dolunca yeni kayıtlar yedek listeye düşer, form kapanmaz) veya **başvuru** (kapanıştan sonra kabul / yedek / ret seçimi). Yanıtın `durum` alanı bu yüzden eklendi.
- Editör forma kapak görseli, sorulara görsel ve PDF ekleri ekleyebilir. Katılımcı tarafında dosya yükleme yok.
**Gerekçe:** Kullanıcı kararları (2026-11-28). Başvuru usulü, daha önce kayıt olup katılmayanları ikinci sıraya koyma isteğiyle (K-29) birlikte çalışır. Öğrenci numarası biçimi, formlar arası eşleştirmeyi e-postadan daha güvenilir yapar. Görseller K-27 akışından geçer.
**Bedeli:** PDF ekleri K-27'nin görsel istisnasını genişletir: PDF yeniden kodlanamaz. Bu yüzden yalnızca editör yükler, tür içerikten doğrulanır, boyut sınırlıdır ve ziyaretçiye indirme (`Content-Disposition: attachment`, `nosniff`) olarak sunulur, sayfa içinde açılmaz.
