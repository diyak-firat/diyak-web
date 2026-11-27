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
