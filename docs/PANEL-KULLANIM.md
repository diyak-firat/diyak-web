# DİYAK Yönetim Paneli Kullanım Rehberi

Bu rehber paneli kullanacak Yönetim Kurulu üyeleri, birim editörleri, akademik danışman ve teknik sorumlular içindir. Kod bilmeniz gerekmez.

> **Bu rehber herkese açık bir depoda durur.** İçindeki isimler ve e-postalar uydurmadır (ör. Ayşe Yılmaz, `ornek@firat.edu.tr`). Rehbere gerçek kişi adı, e-posta, şifre, davet bağlantısı, sunucu bilgisi veya gerçek verinin ekran görüntüsü eklenmez. Ayrıntı: [Bu rehberi güncellerken](#bu-rehberi-güncellerken).

Panel aşama aşama geliştiriliyor. Şu an kullanılabilen bölümler: giriş ve iki adımlı doğrulama, Kullanıcılar, Hesabım ve İşlem kaydı. Duyurular, ekip sayfası, etkinlik formları ve yanıtlar sırayla eklenecek; her biri eklendiğinde bu rehbere de bölümü yazılacak.

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
10. [Yakında eklenecek bölümler](#10-yakında-eklenecek-bölümler)
11. [Sık sorulanlar](#11-sık-sorulanlar)

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

\* Duyuru, form ve ekip ekranları henüz eklenmedi ([10. bölüm](#10-yakında-eklenecek-bölümler)). Şu an bir editör panelde yalnızca Ana ekranı ve Hesabım'ı görür; bu beklenen durumdur.

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

Yönetim Kurulu, Danışman ve Teknik sorumlu görür. Kim, neyi, ne zaman yaptı: girişler, hatalı denemeler, davetler, rol atama ve kaldırmalar, hesap kapatmalar, 2FA sıfırlamaları, şifre değişiklikleri. İleride onaylar, yayınlar ve yanıt indirmeleri de buraya düşecek.

- Eyleme ve kişiye göre filtreleyebilirsiniz.
- Kayıtlar değiştirilemez ve silinemez; 1 yıl sonra kendiliğinden silinir.
- Kayıtta kişisel veri (form yanıtı, IP adresi) tutulmaz.

## 10. Yakında eklenecek bölümler

Bu ekranlar eklendikçe rehbere adım adım bölümleri yazılacak:

| Bölüm | Kimler | Ne yapılacak |
| --- | --- | --- |
| **Duyurular** | Editör, Yönetim Kurulu | Duyuru yazma, önizleme, onaya gönderme; Yönetim Kurulu onayıyla sitede yayımlama |
| **Ekip** | Editör, Yönetim Kurulu | Ekip sayfasındaki kişileri ve fotoğrafları düzenleme, onaya gönderme |
| **Etkinlikler ve formlar** | Editör, Yönetim Kurulu | Etkinlik kayıt formu oluşturma, onaya gönderme, kontenjan ve kapanış tarihi |
| **Yanıtlar** | Form sahibi, Yönetim Kurulu, Danışman | Yanıtları görme, CSV indirme, tek yanıt silme |

Ortak kural: yayına giden her şey (duyuru, form, ekip değişikliği) bir Yönetim Kurulu üyesinin panelde **Onayla**ya basmasıyla yayımlanır. E-postadaki bir bağlantıya tıklamak onay vermez.

## 11. Sık sorulanlar

**Doğrulama uygulaması sürekli kod üretiyor, bir sorun mu var?**
Hayır. Uygulama her 30 saniyede yeni kod gösterir; panel yalnızca giriş sırasında sorar ([3. bölüm](#3-iki-adımlı-doğrulamayı-2fa-kurmak)).

**Menüde Duyurular yok.**
Henüz eklenmedi ([10. bölüm](#10-yakında-eklenecek-bölümler)).

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
