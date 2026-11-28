# DİYAK Yönetim Paneli Kullanım Rehberi

Bu rehber paneli kullanacak Yönetim Kurulu üyeleri, birim editörleri, akademik danışman ve teknik sorumlular içindir. Kod bilmeniz gerekmez.

> **Bu rehber herkese açık bir depoda durur.** İçindeki isimler ve e-postalar uydurmadır (ör. Ayşe Yılmaz, `ornek@firat.edu.tr`). Rehbere gerçek kişi adı, e-posta, şifre, davet bağlantısı, sunucu bilgisi veya gerçek verinin ekran görüntüsü eklenmez. Ayrıntı: [Bu rehberi güncellerken](#bu-rehberi-güncellerken).

Panel aşama aşama geliştiriliyor. Şu an kullanılabilen bölümler: giriş ve iki adımlı doğrulama, Duyurular, Ekip, Kullanıcılar, Hesabım ve İşlem kaydı. Etkinlik formları ve yanıtlar sırayla eklenecek; her biri eklendiğinde bu rehbere de bölümü yazılacak.

## İçindekiler

1. [Panele nereden girilir](#1-panele-nereden-girilir)
2. [Hesabınızı açmak](#2-hesabınızı-açmak)
3. [İki adımlı doğrulamayı (2FA) kurmak](#3-iki-adımlı-doğrulamayı-2fa-kurmak)
4. [Giriş yapmak](#4-giriş-yapmak)
5. [Telefonunuz kaybolursa veya değişirse](#5-telefonunuz-kaybolursa-veya-değişirse)
6. [Roller: kim ne yapabilir](#6-roller-kim-ne-yapabilir)
7. [Hesabım](#7-hesabım)
8. [Kullanıcılar (Başkan, Başkan Yardımcısı, Teknik sorumlu)](#8-kullanıcılar-başkan-başkan-yardımcısı-teknik-sorumlu)
9. [İşlem kaydı](#9-işlem-kaydı)
10. [Duyurular](#10-duyurular)
11. [Ekip sayfası](#11-ekip-sayfası)
12. [Yakında eklenecek bölümler](#12-yakında-eklenecek-bölümler)
13. [Sık sorulanlar](#13-sık-sorulanlar)

---

## 1. Panele nereden girilir

Adres: **`panel.<alan-adi>`** (alan adı Bilgi İşlem'den alınınca kesinleşecek). Sitenin alt bilgisinde panelin bağlantısı yoktur; adres size davetle birlikte iletilir.

Panelde kendi kendine kayıt yoktur. Hesaplar yalnızca davetle açılır.

## 2. Hesabınızı açmak

1. Size "DİYAK Panel daveti" konulu bir e-posta gelir. İçindeki bağlantı **48 saat** geçerlidir ve **tek kullanımlıktır**.
2. Bağlantıyı açın. Hangi rolle ve hangi tarihe kadar davet edildiğiniz yazar.
3. Adınızı, soyadınızı ve şifrenizi girin.
   - Şifre en az **12 karakter** olmalı. Yaygın şifreler (ör. `sifre123456789`) ve yalnızca rakamdan oluşan şifreler kabul edilmez.
   - Uzun bir cümle iyi bir şifredir: `kahvaltida-iki-simit-yedim`.
4. "Hesabı aç"a basın. Sizi iki adımlı doğrulama kurulumu karşılar (sonraki bölüm).

Bağlantının süresi dolduysa veya "Davet bağlantısı geçersiz" görüyorsanız sizi davet eden kişiden yeni bir davet isteyin. Davet bağlantısını kimseyle paylaşmayın; bağlantıyı açan kişi hesabı sizin adınıza açabilir.

## 3. İki adımlı doğrulamayı (2FA) kurmak

Panele girmek için şifrenize ek olarak telefonunuzdaki bir uygulamanın ürettiği 6 haneli kod gerekir. Şifreniz bir yerde ele geçse bile telefonunuz olmadan hesabınıza girilemez. 2FA kurulmadan panelin hiçbir sayfası açılmaz.

**Bir kez yapılır:**

1. Telefonunuza bir doğrulama uygulaması kurun. Hangisi olduğu fark etmez: Google Authenticator, Microsoft Authenticator, Aegis (Android) vb.
2. Uygulamada **"+"** veya **"Hesap ekle"**, ardından **"QR kodu tara"**yı seçin.
3. Bilgisayar ekranındaki karekodu telefonla okutun. Uygulamada **"DİYAK Panel"** adıyla bir hesap belirir.
   - Kamera okumuyorsa sayfadaki **"Karekod okutamıyorum"**a basın. Uygulamada "Kurulum anahtarı gir" seçeneğiyle oradaki anahtarı yazın; tür olarak **zaman tabanlı** seçili olsun.
4. Uygulamada görünen 6 haneli kodu sayfaya yazıp **"Doğrula ve devam et"**e basın.

**Bilmeniz gerekenler:**

- Uygulama **her 30 saniyede yeni bir kod gösterir ve bunu hep yapar**; giriş yapsanız da yapmasanız da. Panel telefonunuza bir şey göndermez: kod telefonun saatinden hesaplanır, internet bile gerekmez. Kodu yalnızca giriş sırasında, panel sorduğunda yazarsınız.
- Bir kod yalnızca bir kez kullanılabilir.
- Kod "hatalı" çıkıyorsa telefonun saatinin **otomatik** ayarlı olduğundan emin olun.
- Karekodun ekran görüntüsünü almayın ve kimseyle paylaşmayın: karekodu okutan herkes sizin kodlarınızı üretebilir.

## 4. Giriş yapmak

1. `panel.<alan-adi>/giris/` adresinde e-postanızı ve şifrenizi girin.
2. Telefonunuzdaki uygulamada "DİYAK Panel" hesabının o anki kodunu yazın.

**Güvenlik kuralları:**

| Durum | Ne olur |
| --- | --- |
| Aynı e-postayla art arda **5 kez hatalı şifre** | Giriş **30 dakika** kapanır. Süre dolunca yeniden deneyin ya da teknik sorumludan kilidi açmasını isteyin |
| **1 saat** hiçbir şey yapmazsanız | Oturum kapanır, yeniden giriş yaparsınız |
| Girişten **8 saat** sonra | Oturum her durumda kapanır |
| İlk kez kullandığınız bir tarayıcı veya cihazdan giriş | E-postanıza "yeni cihazdan giriş" uyarısı gelir |
| Şifreniz değiştirildiğinde | E-postanıza bilgilendirme gelir |

Uyarı e-postası size ait olmayan bir girişi bildiriyorsa hemen şifrenizi değiştirin (Hesabım → Şifremi değiştir) ve teknik sorumluya haber verin.

Ortak kullanılan bilgisayarlarda işiniz bitince menünün altındaki **"Çıkış yap"**a basın.

## 5. Telefonunuz kaybolursa veya değişirse

**Teknik sorumluya yazın.** Teknik sorumlu, kimliğinizden emin olduktan sonra (yüz yüze ya da bildiği bir telefon numarasından) 2FA'nızı sıfırlar. Sonraki girişinizde şifrenizden sonra yeni bir karekod gelir; [3. bölümdeki](#3-iki-adımlı-doğrulamayı-2fa-kurmak) adımları yeni telefonunuzla tekrarlarsınız.

- Teknik sorumlu sizin şifrenizi öğrenmez ve bilmesine gerek yoktur. Kimse sizden şifrenizi veya doğrulama kodunuzu istemez; isteyen olursa bu bir dolandırıcılık girişimidir.
- Şifrenizi unuttuysanız da teknik sorumluya yazın.
- Eski telefonunuz hâlâ elinizdeyse, sıfırlamadan sonra uygulamadaki eski "DİYAK Panel" hesabını silebilirsiniz.

## 6. Roller: kim ne yapabilir

Her rolün bir **bitiş tarihi** vardır, genellikle dönem sonu (bir sonraki Olağan Genel Kurul). Tarih geçince rol kendiliğinden düşer ve hiçbir yetki vermez. Yeni dönemde roller yeniden atanır. Bir kişinin birden çok rolü olabilir.

| Rol | Kimdir | Panelde ne yapar |
| --- | --- | --- |
| **Yönetim Kurulu** | Seçilmiş Yönetim Kurulu üyeleri | Yayına giden her şeyi onaylar; işlem kaydını görür. **Başkan** ve **Başkan Yardımcısı** ayrıca kişi davet eder, rol atar ve kaldırır |
| **Editör** | Birim üyeleri (iletişim, medya, etkinlik, proje) | Duyuru, form ve ekip sayfası taslağı hazırlar ve onaya gönderir* |
| **Danışman** | Akademik danışman | Her şeyi görüntüler, işlem kaydını izler, değiştirmez |
| **Teknik sorumlu** | 1–2 kişi | Hesap bakımı: 2FA sıfırlama, giriş kilidi açma, teknik sorumlu daveti. İçeriklere ve form yanıtlarına erişmez |

\* Form ekranları henüz eklenmedi ([12. bölüm](#12-yakında-eklenecek-bölümler)).

**Kimse kendi rolünü değiştiremez.** Başkan kendine rol veremez, kendi rolünü uzatamaz veya kaldıramaz; bunu Başkan Yardımcısı yapar (ya da tersi). Kimse kendi hesabını kapatamaz.

Menüde yalnızca açabildiğiniz ekranlar görünür.

## 7. Hesabım

Herkes görür. Burada:

- Rolleriniz ve bitiş tarihleri,
- 2FA cihazınız (ne zaman eklendiği, en son ne zaman kullanıldığı),
- Son giriş olaylarınız: başarılı girişler, hatalı denemeler, yeni cihazdan girişler, şifre değişiklikleri.

Tanımadığınız bir giriş veya hatalı deneme görürseniz şifrenizi değiştirin ve teknik sorumluya haber verin.

**Şifre değiştirmek:** Hesabım → **Şifremi değiştir**. Mevcut şifrenizi ve yeni şifrenizi iki kez girin. Şifre değişince diğer cihaz ve tarayıcılardaki oturumlarınız kapanır; e-postanıza bilgilendirme gider.

## 8. Kullanıcılar (Başkan, Başkan Yardımcısı, Teknik sorumlu)

Menüde **Kullanıcılar** yalnızca bu kişilere görünür. Ekranda üç liste vardır:

- **14 gün içinde bitecek roller:** dönem sonu yaklaşınca kimlerin yetkisinin düşeceğini gösterir. Ayrıca rol bitişinden 14 ve 3 gün önce Başkan ve Başkan Yardımcısı'na hatırlatma e-postası gider.
- **Hesaplar:** herkes ve etkin rolleri. Kapatılmış hesaplar "Kapalı" etiketiyle görünür.
- **Bekleyen davetler:** henüz kabul edilmemiş, süresi dolmamış davetler.

### Kişi davet etmek

1. **Kişi davet et**e basın.
2. E-postayı yazın (mümkünse üniversite e-postası). Örnek: Ayşe Yılmaz, `ornek@firat.edu.tr`.
3. Rolü seçin. Listede yalnızca sizin atayabildiğiniz roller vardır: Başkan ve Başkan Yardımcısı Yönetim Kurulu, editör ve danışman atar; teknik sorumlu yalnızca teknik sorumlu atar.
4. **Görev adı** isteğe bağlıdır (ör. "İletişim Birimi", "Sayman"). Dikkat: Yönetim Kurulu rolünde **"Başkan"** veya **"Başkan Yardımcısı"** görev adı, kişiye davet ve rol atama yetkisi verir.
5. **Rolün bitişi** olarak dönem sonunu seçin. Varsayılan olarak sizin rolünüzün bitişi gelir.
6. **Daveti gönder**e basın. Kişiye 48 saat geçerli bağlantı gider.

Daveti yanlış e-postaya gönderdiyseniz doğru e-postaya yeniden gönderin; aynı e-postaya yeni davet gönderilirse eskisi geçersiz olur. Zaten hesabı olan birine davet gönderilmez; ona rolü kişi sayfasından atayın.

### Rol atamak ve kaldırmak

Listede kişinin adına basın.

- **Rol ata:** rolü, görev adını ve bitiş tarihini girip **Rolü ata**ya basın.
- **Rolü kaldır:** rol satırındaki **Kaldır**a basın; açılan sayfada ne olacağı yazar, **Rolü kaldır** ile onaylayın. Yetkiler hemen kalkar.
- Bir kişinin görevi sürüyorsa ama rolü bitiyorsa, yeni bitiş tarihiyle rolü yeniden atayın.

### Hesabı kapatmak

Topluluktan ayrılan veya panele artık girmemesi gereken kişi için: kişi sayfası → **Hesabı kapat** → onay. Kişinin açık oturumları hemen sona erer. Kapatılan hesap panelden yeniden açılamaz; gerekirse teknik sorumlu açar.

### Yalnızca teknik sorumlu için

- **2FA'yı sıfırla:** telefonunu kaybeden kişi için ([5. bölüm](#5-telefonunuz-kaybolursa-veya-değişirse)). **Önce kişinin kimliğinden emin olun.** Kendi 2FA'nızı sıfırlayamazsınız; bunu diğer teknik sorumlu yapar.
- **Giriş kilidini aç:** art arda hatalı şifre nedeniyle kilitlenen hesap için. Kişi sayfasında "Giriş kilidi: Kilitli" yazıyorsa düğme görünür.

Bu işlemlerin hepsi işlem kaydına yazılır.

## 9. İşlem kaydı

Yönetim Kurulu, Danışman ve Teknik sorumlu görür. Kim, neyi, ne zaman yaptı: girişler, hatalı denemeler, davetler, rol atama ve kaldırmalar, hesap kapatmalar, 2FA sıfırlamaları, şifre değişiklikleri. Duyurularda ve ekip sayfasında onaya gönderme, onaylama, düzeltme isteme, yayımlama ve yayından kaldırma da buraya düşer. İleride yanıt görüntüleme ve indirmeleri de eklenecek.

- Eyleme ve kişiye göre filtreleyebilirsiniz.
- Kayıtlar değiştirilemez ve silinemez; 1 yıl sonra kendiliğinden silinir.
- Kayıtta kişisel veri (form yanıtı, IP adresi) tutulmaz.

## 10. Duyurular

Duyurular sitenin **Gündem** bölümünde yayımlanan gönderilerdir. Editörler ve Yönetim Kurulu yazar; Danışman okur ama değiştirmez. Yayına çıkan her duyuruyu bir Yönetim Kurulu üyesi onaylar.

```
Taslak ──▶ Onaya gönder ──▶ Yönetim Kurulu: Onayla ve yayımla ──▶ Sitede
              ▲                        │
              └──── Düzeltme iste ◀────┘
```

### Duyuru yazmak (Editör, Yönetim Kurulu)

1. Menüden **Duyurular** → **Yeni duyuru**.
2. **Başlık** (en fazla 140 karakter) ve **etiketi** seçin: Etkinlik, Duyuru, Çağrı veya Yayın.
3. Etiket **Etkinlik** ise etkinliğin **tarihini, saatini** ve **yerini** girin. Sitede gönderinin altında gri bir kutuda görünür.
4. **Özet**: gündem listesinde başlığın altında görünen bir iki cümle (en fazla 300 karakter).
5. **Metin**: araç çubuğuyla biçimlendirin. Kalın, italik, başlık, alt başlık, madde ve numaralı liste, alıntı ve bağlantı kullanılabilir.
   - **İç içe liste:** Bir liste maddesindeyken **İçeri al** (ya da klavyede Tab) o maddeyi bir üsttekinin altına alır; **Dışarı al** (Shift+Tab) geri çıkarır. Alt maddelerin türünü değiştirmek için imleç alt maddedeyken **Madde listesi** veya **Numaralı liste**ye basın; örneğin numaralı maddelerin altında madde işaretli bir alt liste olur.
   - **Bağlantı:** **Bağlantı**ya basın. **Görünecek metin**i ve adresi yazıp **Bağlantıyı ekle**ye basın. Önce metni seçerseniz görünecek metin kendiliğinden dolar. Var olan bağlantıyı değiştirmek veya kaldırmak için imleci bağlantının üzerine getirip **Bağlantı**ya basın. Adres `https://` veya `mailto:` ile başlamalıdır.
6. Sayfanın altındaki **Önizleme** siz yazdıkça güncellenir ve duyurunun sitede nasıl görüneceğini gösterir. **Tam sayfa önizleme** son kaydedilen hali gösterir.
7. **Kaydet**: taslak olarak saklar, istediğiniz zaman dönüp devam edersiniz. **Onaya gönder**: Yönetim Kurulu'na iletir; Yönetim Kurulu üyelerine "onay bekleyen 1 duyuru var" e-postası gider.

Başka bir yerden (Word, e-posta) yapıştırdığınız metindeki renk, yazı tipi, görsel gibi biçimler atılır; yalnızca yukarıdaki biçimler kalır.

**Onay beklerken** duyuru düzenlenemez. Bir şeyi değiştirmek isterseniz duyuruyu açıp **Taslağa geri al**a basın, düzeltip yeniden onaya gönderin.

**Düzeltme istenirse** e-postanıza bildirim gelir. Duyuruyu açtığınızda Yönetim Kurulu'nun notu en üstte görünür; düzeltip yeniden **Onaya gönder**e basın. Ana ekrandaki **Taslaklarım** listesinde bu duyurular "Düzeltme istendi" etiketiyle görünür.

Hiç yayımlanmamış bir taslağı **Taslağı sil** ile silebilirsiniz (yalnızca kendi taslaklarınızı; Yönetim Kurulu tüm taslakları).

### Onaylamak (Yönetim Kurulu)

1. Ana ekranın en üstündeki **Onay bekleyenler** listesinden duyuruyu açın (ya da e-postadaki bağlantıdan; e-postadaki bağlantı yalnızca paneli açar, onay vermez).
2. Duyuruyu sitede görüneceği haliyle okuyun.
3. Uygunsa **Onayla ve yayımla**. Değilse kutuya neyin düzeltilmesi gerektiğini yazıp **Düzeltme iste**; duyuru notla birlikte hazırlayana döner.

Tek bir Yönetim Kurulu üyesinin onayı yeterlidir. Kendi yazdığınız duyuruyu düzenleme ekranındaki **Onayla ve yayımla** ile doğrudan yayımlayabilirsiniz; işlem kaydında "kendi içeriğini onayladı" olarak görünür.

### Yayındaki duyuru

- **Değiştirmek:** Yayındaki duyuruyu yalnızca Yönetim Kurulu üyeleri düzenleyebilir; kaydettiğiniz değişiklik onay beklemeden sitede görünür ve işlem kaydına yazılır. Editörler yayındaki duyuruyu değiştiremez; değişiklik gerekiyorsa Yönetim Kurulu'na yazın.
- **Yayından kaldırmak** (Yönetim Kurulu): duyuruyu açın → **Yayından kaldır** → onay. Duyuru sitedeki gündemden kalkar. Kaldırılan duyuru düzenlenip yeniden onaya gönderilebilir.

> Not: Panel şu an sitenin kendisine bağlı değil. Onaylanan duyurular panelde "Yayında" görünür; sitenin gündemi bu duyurulardan beslenmeye ileride geçecek. O zamana kadar sitedeki gündem eski yöntemle güncellenir.

## 11. Ekip sayfası

Sitedeki **Ekip** sayfası panelden yönetilir. Editörler ve Yönetim Kurulu düzenler, Danışman görür, Yönetim Kurulu onaylar.

**En önemli kural:** Ekip ekranında yaptığınız her değişiklik (kişi ekleme, silme, fotoğraf, sıra) **onaya gönderilip Yönetim Kurulu onaylayana kadar sitede görünmez.** Rahatça düzenleyebilirsiniz; site, en son onaylanan haliyle kalır.

### Dönem

Ekip sayfası dönem dönem tutulur (ör. 2026–2027). Yeni dönem başlarken **Ekip** → **Yeni dönem**:
- **Önceki dönemi kopyala:** gruplar ve kişiler kopyalanır; ayrılanları silin, yenileri ekleyin.
- **Sitedeki bölümlerle boş başlat:** Akademik Danışman, Yönetim ve dört birim boş olarak açılır (ilk kurulum için).

Önceki dönemin kayıtları silinmez ama panelde yalnızca aktif dönem düzenlenir.

### Kişi eklemek ve düzenlemek

1. İlgili grubun yanındaki **Kişi ekle**ye basın (ya da kişinin adına basarak düzenleyin).
2. **Ad soyad**, **görev** (ör. Başkan, Birim Sorumlusu, Üye) ve isterseniz **e-posta**. Akademik danışman için **fakülte / bölüm**.
3. **Fotoğraf** (isteğe bağlı): JPEG, PNG veya WebP, en fazla 10 MB. Panel fotoğrafı ortadan kare kırpar, küçültür ve telefonun eklediği konum ve cihaz bilgilerini siler. Fotoğraf yoksa sitede gri bir yer tutucu görünür.
4. **Bağlantılar** (isteğe bağlı): ORCID, LinkedIn, GitHub, Google Scholar, Scopus, DergiPark, Web of Science, YÖK Akademik, kişisel sayfa. Adresler `https://` ile başlamalı.
5. **Kişinin yayın için yazılı onayı alındı:** Kişinin adı, fotoğrafı, e-postası ve bağlantılarının sitede yayımlanmasına **yazılı** onay verdiyse işaretleyin. **İşaretli değilse kişi sitede görünmez** (KVKK). Yazılı onay belgesini topluluk dosyasında saklayın.
6. **Kaydet**.

Gruplardaki ve gruplar arasındaki sırayı **Yukarı** / **Aşağı** ile değiştirin. Sitede aynı sırayla görünür. Grup eklemek, adını değiştirmek veya silmek için **Grup ekle** ve **Grubu düzenle**.

**Önizleme** düğmesi, şu anki halin onaylanırsa sitede nasıl görüneceğini gösterir (yalnızca yayın onayı olan kişilerle).

### Onaya göndermek

Ekip ekranının altındaki **Onaya gönder** bölümüne değişikliği bir cümleyle özetleyin (ör. "İletişim Birimi'ne iki yeni üye eklendi.") ve gönderin. O anki hal dondurulur; gönderdikten sonra yaptığınız düzenlemeler bu onaya dahil olmaz, bir sonrakinde gönderilir. Yönetim Kurulu'na e-posta gider.

Aynı anda tek bir onay bekleyen ekip değişikliği olabilir. Yeni bir şey eklemek isterseniz onay bekleyen değişikliği açıp **Geri çek**in, sonra yeniden gönderin.

### Onaylamak (Yönetim Kurulu)

Ana ekrandaki **Onay bekleyenler**de ekip değişikliğini açın. Ekranda:
- **Sitedeki halden farkı:** hangi gruba kim eklendi, kim çıktı, kimin bilgisi değişti.
- **Sitede görünecek hal:** kartlar, fotoğraflar, bağlantılar.

Kişilerin bilgilerini ve fotoğraflarını kontrol edip **Onayla ve yayımla**ya basın ya da notla **Düzeltme iste**yin. Onaylanan hal hemen sitedeki ekip sayfasının kaynağı olur.

## 12. Yakında eklenecek bölümler

Bu ekranlar eklendikçe rehbere adım adım bölümleri yazılacak:

| Bölüm | Kimler | Ne yapılacak |
| --- | --- | --- |
| **Etkinlikler ve formlar** | Editör, Yönetim Kurulu | Etkinlik kayıt formu oluşturma, onaya gönderme, kontenjan ve kapanış tarihi |
| **Yanıtlar** | Form sahibi, Yönetim Kurulu, Danışman | Yanıtları görme, CSV indirme, tek yanıt silme |

Ortak kural: yayına giden her şey (duyuru, form, ekip değişikliği) bir Yönetim Kurulu üyesinin panelde **Onayla**ya basmasıyla yayımlanır. E-postadaki bir bağlantıya tıklamak onay vermez.

## 13. Sık sorulanlar

**Doğrulama uygulaması sürekli kod üretiyor, bir sorun mu var?**
Hayır. Uygulama her 30 saniyede yeni kod gösterir; panel yalnızca giriş sırasında sorar ([3. bölüm](#3-iki-adımlı-doğrulamayı-2fa-kurmak)).

**Menüde Duyurular yok.**
Duyurular Editör, Yönetim Kurulu ve Danışman rollerine açıktır. Teknik sorumlu içerik görmez. Rolünüzü Hesabım'da kontrol edin.

**Onayladığım duyuru veya ekip değişikliği sitede görünmüyor.**
Panel henüz siteye bağlanmadı ([10. bölümdeki not](#yayındaki-duyuru)).

**Eklediğim kişi önizlemede yok.**
"Kişinin yayın için yazılı onayı alındı" kutusu işaretli değil. Yazılı onay olmadan kişi sitede gösterilmez.

**Bir sayfada "403" veya "yetkiniz yok" görüyorum.**
O ekran rolünüze açık değil ya da rolünüzün süresi dolmuş. Hesabım'da rollerinizi ve bitiş tarihlerini kontrol edin; gerekiyorsa Başkan veya Başkan Yardımcısı'na yazın.

**"Oturumunuzun süresi doldu" yazdı.**
1 saat hareketsiz kaldınız veya girişinizin üzerinden 8 saat geçti. Yeniden giriş yapın.

**Davet e-postası gelmedi.**
Gereksiz (spam) klasörüne bakın. Yoksa davet edenden e-postayı kontrol etmesini ve daveti yeniden göndermesini isteyin.

---

## Bu rehberi güncellerken

Bu dosya herkese açık bir depodadır. Rehbere yazılabilecekler: panele giriş, 2FA, telefon kaybolunca ne yapılacağı, ekranların adım adım kullanımı, rollerin yetkileri ve panel adresi (`panel.<alan-adi>`; alt alan adları sertifika kayıtlarından zaten görülebilir).

**Asla yazılmayacaklar:**

- Şifreler, davet bağlantıları, 2FA karekodları veya kurtarma kodları
- Sunucunun IP adresi, SSH kullanıcı adları, VPN yapılandırması ve anahtarları
- Yedek anahtarlarının kimde olduğu, yedeklerin kimlerin bilgisayarına çekildiği
- Gerçek kişilerin isimleri ve e-postaları (örnekte "Ayşe Yılmaz, `ornek@firat.edu.tr`" gibi uydurma bilgi kullanın)
- Gerçek veri içeren ekran görüntüleri (yanıt tablosu, gerçek kullanıcı listesi). Ekran görüntüleri deneme ortamında sahte veriyle alınır.

Git geçmişine bir kez giren bilgi, dosyadan silinse bile geçmişte kalır. Gizli kalması gereken operasyon bilgileri ayrı bir private depoda (ör. `diyak-ops`) veya parola yöneticisinde, yalnızca teknik sorumluların ve Başkan'ın erişebileceği yerde tutulur.

Rehber, panel tamamlanınca (PANEL.md §12, A6) panelin içinde bir **Yardım** sayfası olarak da gösterilecek.
