# Yönetim Paneli Tasarım Belgesi (Faz 2)

Bu belge, yönetimin ve birim ekiplerinin duyuru yayımlamak, etkinlik kayıt formu açmak, yanıtları görmek ve ekip sayfasını güncellemek için kullanacağı **kendi panelimizin** tanımıdır. Kararlar ve gerekçeleri: [DECISIONS.md K-15, K-16, K-17, K-18](DECISIONS.md).

> **Agent'lar için:** Bu belge panelin kapsamını ve kurallarını tanımlar. Kapsam dışındaki bir özelliği eklemeden, veri modelini değiştirmeden veya §9'daki güvenlik kurallarından birini gevşetmeden önce kullanıcıya sor. Uygulama sırası §12'de; her aşamanın kabul ölçütleri sağlanmadan sonrakine geçme.

## İçindekiler

1. [Amaç ve ilkeler](#1-amaç-ve-ilkeler)
2. [Kapsam](#2-kapsam)
3. [Giriş ve hesaplar](#3-giriş-ve-hesaplar)
4. [Roller ve yetkiler](#4-roller-ve-yetkiler)
5. [Ekranlar](#5-ekranlar)
6. [Veri modeli](#6-veri-modeli)
7. [Form oluşturucu](#7-form-oluşturucu)
8. [Akışlar](#8-akışlar)
9. [Güvenlik kuralları](#9-güvenlik-kuralları)
10. [Arayüz kuralları](#10-arayüz-kuralları)
11. [Teknik yapı](#11-teknik-yapı)
12. [Uygulama sırası](#12-uygulama-sırası)

---

## 1. Amaç ve ilkeler

- **Kod bilmeyen biri eğitim almadan kullanabilmeli.** Bir birim üyesi ilk kez açtığında duyuru yazıp onaya gönderebilmeli.
- **İhtiyaç kadar.** Panel dört işi iyi yapar: duyuru, etkinlik kayıt formu, yanıtlar, ekip sayfası. Yeni özellik ancak gerçek bir ihtiyaç doğunca eklenir.
- **Sitenin parçası gibi görünür.** Aynı renkler, yazı tipleri ve bileşenler (`tokens.css`).
- **Güvenliğin zor kısmı hazır araçlarda.** Giriş, oturum, 2FA, HTML temizleme ve dosya yükleme sınanmış kütüphanelerle yapılır. Kendimiz yazmayız.
- **Yayına giden her şeyi Yönetim Kurulu onaylar.** Onay, panele kendi hesabıyla girmiş bir Yönetim Kurulu üyesi tarafından verilir.
- **Kişisel veri en az düzeyde.** Formlarda yalnızca aydınlatma metni onayı zorunludur. Her yanıtın bir silinme tarihi vardır.

## 2. Kapsam

**İlk sürümde var:**

- Duyuru yazma, düzenleme, önizleme, onaya gönderme, yayımlama, yayından kaldırma
- Etkinlik oluşturma ve etkinliğe bağlı (ya da bağımsız) kayıt formu
- Esnek form oluşturucu (§7)
- Herkese açık form sayfası, kontenjan ve kapanış tarihi
- Yanıtları tablo halinde görme, arama, CSV indirme
- Saklama süresi dolan yanıtların otomatik silinmesi
- **Ekip sayfasının yönetimi:** dönem, danışman, yönetim, birimler, kişiler, fotoğraflar
- Davetle hesap açma, dönemlik rol atama, 2FA
- İşlem kaydı (kim neyi ne zaman yaptı)

**İlk sürümde yok (bilinçli olarak):**

- Zamanlı yayın, sürüm geçmişi ve geri alma (işlem kaydı yeterli)
- Çok dilli içerik
- Formlarda dosya yükleme alanı (gerekirse sonra, `dosyalar` akışıyla)
- Koşullu sorular ("şunu seçerse bunu sor")
- Ödeme, bilet, QR kod
- Proje başvuruları ve hakem süreci (ayrı uygulama: `basvurular`, ARCHITECTURE.md)
- Sürükle-bırak sayfa düzenleyici
- Üniversite hesabıyla tek oturum (SSO): üniversite öğrencilere kurumsal hesap veriyorsa sonradan eklenebilir

## 3. Giriş ve hesaplar

### Panele nereden girilir

- Adres: **`panel.<alan-adi>`** (ör. `panel.diyak.org.tr`). Sitenin alt bilgisinde bağlantısı yoktur, adres ekiplere iletilir.
- Panel internete açıktır, VPN gerekmez. Koruma hesap düzeyindedir: güçlü şifre + **zorunlu 2FA** + hatalı giriş kilidi + yeni cihazdan girişte e-posta uyarısı (§9).
- **Django Admin ve sunucuya SSH** ise yalnızca teknik sorumlular içindir ve VPN arkasındadır. Burada daha geniş yetki olduğu için daha sıkı kısıtlama uygulanır.

### Hesap nasıl açılır

1. Hesaplar **yalnızca davetle** açılır, kendi kendine kayıt yoktur.
2. Davet eden kişi (§4, "Rol atama") davet edilenin e-postasını ve rolünü girer. Mümkünse üniversite e-postası kullanılır.
3. Davet edilene 48 saat geçerli bir bağlantı gider. Kişi şifresini belirler ve **2FA'yı kurmadan panele giremez** (telefon uygulaması: Google Authenticator, Microsoft Authenticator, Aegis vb.).
4. 2FA cihazını kaybeden kişinin 2FA'sını teknik sorumlu sıfırlar. Bu işlem işlem kaydına düşer.

### İlk kurulum

İlk Başkan hesabını teknik sorumlu bir yönetim komutuyla açar (`manage.py ilk_yonetici`). Sonraki tüm hesapları Başkan veya Başkan Yardımcısı panelden davetle açar.

## 4. Roller ve yetkiler

| Rol | Kimdir | Kısaca |
| --- | --- | --- |
| **Yönetim Kurulu** | Seçilmiş Yönetim Kurulu üyeleri | Onaylar ve yayına alır, tüm formların yanıtlarını görür |
| **Editör** | Birim üyeleri (iletişim, medya, etkinlik, proje) | Duyuru, form ve ekip içeriği taslağı hazırlar |
| **Danışman** | Akademik danışman | Her şeyi görüntüler, işlem kaydını izler, değiştirmez |
| **Teknik sorumlu** | 1–2 kişi | Hesap ve sistem bakımı; içerik ve yanıtlara erişmez |

**Form sahibi** bir rol değil, form bazında verilen bir yetkidir: formu hazırlayan editör ve onun seçtiği kişiler o formun yanıtlarını görür.

### Rol atama ve dönem

- **Rolleri Başkan ve Başkan Yardımcısı atar.** Teknik sorumlu yalnızca Teknik rolünü ve ilk Başkan hesabını yönetir.
- Her rol atamasının bir **bitiş tarihi** vardır, varsayılan olarak dönem sonu (bir sonraki Olağan Genel Kurul). Tarih gelince rol kendiliğinden düşer.
- Bu sayede her dönem başında yeni Yönetim Kurulu rolleri yeniden dağıtır. Ayrılan kişilerin yetkisi unutulup açık kalmaz.
- Dönem bitişinden 14 gün önce Başkan'a "şu kişilerin rolleri sona eriyor" e-postası gider.
- Her atama ve kaldırma işlem kaydına yazılır (kim, kime, hangi rol, ne zamana kadar).

### Yetki tablosu

| İşlem | Editör | Yönetim Kurulu | Danışman | Teknik |
| --- | :-: | :-: | :-: | :-: |
| Duyuru taslağı oluştur / düzenle / onaya gönder | ✓ | ✓ | | |
| Duyuruyu yayımla / yayından kaldır | | ✓ | | |
| Etkinlik ve form taslağı oluştur / onaya gönder | ✓ | ✓ | | |
| Formu onaylayıp yanıtlara aç | | ✓ | | |
| Formu erken kapat | form sahibi | ✓ | | |
| Yanıtları görüntüle / CSV indir | form sahibi | ✓ (tümü) | ✓ (görüntüleme) | |
| Tek bir yanıtı sil (kişi talebiyle) | | ✓ | | |
| Ekip sayfası taslağı düzenle | ✓ | ✓ | | |
| Ekip sayfası değişikliğini yayımla | | ✓ | | |
| Kullanıcı davet et, rol ata/kaldır | | Başkan, Başkan Yrd. | | yalnızca ilk Başkan ve Teknik rolü |
| İşlem kaydını görüntüle | | ✓ | ✓ | ✓ |
| 2FA sıfırla, hesap kilidini aç | | | | ✓ |

Teknik sorumlu **yanıtları ve form içeriklerini göremez**. Django Admin'de de yanıt içerikleri gösterilmez (§9).

## 5. Ekranlar

Tüm ekranlar Türkçe.

| Ekran | İçerik | Kimler |
| --- | --- | --- |
| **Giriş** | E-posta + şifre, ardından 2FA kodu | Herkes |
| **Ana ekran** | **Onay bekleyenler** (Yönetim Kurulu için en üstte), taslaklarım, açık formlar ve doluluk oranları, son 7 günün yanıt sayıları | Herkes (yetkisine göre) |
| **Duyurular** | Liste: başlık, etiket, durum, son değişiklik. Filtre: durum, etiket | Editör, Yönetim Kurulu |
| **Duyuru düzenle** | Başlık, etiket, özet, metin editörü, kapak görseli, bağlı etkinlik (isteğe bağlı). **Canlı önizleme** (sitedeki gönderi sayfasının görünümü). Düğmeler: Kaydet · Onaya gönder · (Yönetim Kurulu) Yayımla | Editör, Yönetim Kurulu |
| **Etkinlikler** | Liste: ad, tarih, yer, form durumu, kayıt sayısı / kontenjan | Editör, Yönetim Kurulu |
| **Form oluştur / düzenle** | Form ayarları (açılış, kapanış, kontenjan, saklama süresi, aydınlatma metni, açık rıza gerekli mi, form sahipleri) ve alanlar (§7). Formun **önizlemesi** | Editör, Yönetim Kurulu |
| **Onay ekranı** | Onaya gönderilen duyuru, form veya ekip değişikliğinin tam görünümü; formlar için kontrol listesi; Onayla / Düzeltme iste (not ile) | Yönetim Kurulu |
| **Yanıtlar** | Formun yanıt tablosu, arama, CSV indir, tek yanıt silme. Üstte: "Bu yanıtlar GG.AA.YYYY tarihinde otomatik silinecek" | Form sahibi, Yönetim Kurulu, Danışman |
| **Ekip** | Dönem; danışman; yönetim; birimler ve kişiler. Kişi: ad, görev, e-posta, fotoğraf, isteğe bağlı bağlantılar, **"yayın için yazılı onay alındı"** kutusu. Sıralama sürükleyerek. Değişiklikler onaya gönderilir | Editör, Yönetim Kurulu |
| **Kullanıcılar** | Davet et, rol ata (bitiş tarihiyle), rolü kaldır, hesabı kapat; rolü yakında bitecekler listesi | Başkan, Başkan Yrd., Teknik (kısıtlı) |
| **İşlem kaydı** | Tarih, kişi, işlem, nesne. Filtrelenebilir | Yönetim Kurulu, Danışman, Teknik |
| **Hesabım** | Şifre değiştir, 2FA cihazları, son girişler | Herkes |

**Herkese açık sayfalar** (panel dışında, sitenin tasarımıyla):

- `/kayit/<slug>/`: Form sayfası. Form kapalıysa veya kontenjan dolduysa bunu açıkça söyler.
- `/kayit/<slug>/tamam/`: Gönderim sonrası teşekkür sayfası.

## 6. Veri modeli

Django uygulamaları: `accounts`, `duyurular`, `etkinlikler`, `formlar`, `ekip`, `denetim`. Ekranlar `panel` uygulamasında.

```
accounts.Kullanici            Django'nun AbstractUser'ı
  e-posta (giriş kimliği), ad, soyad

accounts.RolAtamasi
  kullanici, rol (yonetim_kurulu | editor | danisman | teknik)
  gorev_adi         ör. "Başkan", "Başkan Yardımcısı", "İletişim Birimi" (Başkan/Yrd. davet ve atama yetkisini belirler)
  baslangic, bitis  bitis geçince rol etkisizdir
  atayan, olusturma

accounts.Davet
  eposta, rol, gorev_adi, bitis, token (tek kullanımlık, 48 saat), davet_eden, kullanildi

duyurular.Duyuru
  baslik            str ≤ 140
  slug              benzersiz, otomatik (Türkçe karakterler sadeleştirilir)
  etiket            Etkinlik | Duyuru | Çağrı | Yayın
  ozet              str ≤ 300
  govde             temizlenmiş HTML (§9)
  kapak_gorseli     dosya referansı, isteğe bağlı
  etkinlik          → etkinlikler.Etkinlik, isteğe bağlı
  durum             taslak | onay_bekliyor | yayinda | kaldirildi
  yayin_tarihi      yayımlanınca dolar
  olusturan, onaylayan, onay_notu, olusturma, guncelleme

etkinlikler.Etkinlik
  ad, aciklama (kısa), baslangic (tarih-saat), bitis (isteğe bağlı), yer
  cevrim_ici        bool

formlar.AydinlatmaMetni       Sürümlü: yanıt hangi metne onay verdiyse o kayıtlıdır
  baslik, metin, surum, yururluk_tarihi

formlar.Form
  etkinlik          → Etkinlik, isteğe bağlı
  baslik, aciklama, slug
  durum             taslak | onay_bekliyor | acik | kapali | arsiv
  acilis, kapanis   tarih-saat
  kontenjan         int, boşsa sınırsız
  alanlar           JSON (§7 şeması), sayı sınırı yok
  tekil_alan        alan kimliği, isteğe bağlı (ör. "eposta": aynı değerle ikinci gönderim engellenir)
  aydinlatma_metni  → AydinlatmaMetni (zorunlu)
  acik_riza_gerekli bool + acik_riza_metni
  saklama_gun       int, zorunlu (önerilen: etkinlik bitişinden 90 gün sonra)
  silinme_tarihi    hesaplanır: etkinlik bitişi (yoksa kapanış) + saklama_gun
  sahipler          → Kullanici (çoka çok)
  olusturan, onaylayan, onay_notu, zaman damgaları

formlar.Yanit
  form              → Form
  cevaplar          JSON {alan_id: değer}   (tüm alanlar, varsayılanlar dahil)
  tekil_deger       tekil_alan seçildiyse onun normalize edilmiş değeri; (form, tekil_deger) benzersiz
  aydinlatma_surumu → AydinlatmaMetni (zorunlu)
  acik_riza         bool (gerekliyse true olmalı)
  gonderim          tarih-saat

ekip.Donem
  ad ("2026–2027"), baslangic, bitis, aktif

ekip.Grup                     Danışman, Yönetim, birimler
  donem, ad, sira

ekip.Kisi
  grup, ad, gorev ("Başkan", "Birim Sorumlusu", "Üye"…), eposta, foto, sira
  baglantilar       JSON {linkedin, github, orcid, scholar, …} (isteğe bağlı)
  yayin_onayi_tarihi  doluysa sitede görünür; boşsa görünmez
  kullanici         → Kullanici, isteğe bağlı (panel hesabıyla bağlantı)

ekip.Degisiklik               Ekip sayfası değişiklikleri onaydan geçer
  durum (taslak | onay_bekliyor | yayinda), olusturan, onaylayan, ozet

denetim.IslemKaydi
  kullanici, eylem, nesne_turu, nesne_id, zaman, ayrinti (JSON, kişisel veri içermez)
```

IP adresi **saklanmaz**. Spam sınırlaması için gereken sayaçlar Redis'te kısa süreli tutulur.

## 7. Form oluşturucu

### Nasıl çalışır

"Form oluştur"a basıldığında form, sık kullanılan alanlar **hazır eklenmiş** olarak açılır. Editör bunları istediği gibi kaldırabilir, sırasını değiştirebilir, zorunlu/isteğe bağlı yapabilir ve sınırsız sayıda yeni alan ekleyebilir.

**Hazır gelen alanlar (kaldırılabilir):**

| Alan | Tür | Varsayılan |
| --- | --- | --- |
| Ad | kısa metin | zorunlu |
| Soyad | kısa metin | zorunlu |
| E-posta | e-posta | zorunlu, tekil alan |
| Bölüm | kısa metin | isteğe bağlı |
| Sınıf | tek seçim (Hazırlık, 1–4, Yüksek lisans, Doktora, Mezun, Diğer) | isteğe bağlı |

**Her formda bulunan, kaldırılamayan alanlar:**

| Alan | Kural |
| --- | --- |
| Aydınlatma metnini okudum ve anladım | **Her zaman zorunlu.** Formun sonunda, aydınlatma metni bağlantısıyla birlikte. Kaldırılamaz, isteğe bağlı yapılamaz |
| Açık rıza | Yalnızca form ayarında "açık rıza gerekli" seçilirse görünür ve o zaman zorunludur |

### Alan türleri

| Tür | Kural |
| --- | --- |
| `kisa_metin` | ≤ 200 karakter |
| `uzun_metin` | ≤ 2000 karakter |
| `eposta` | E-posta biçimi doğrulanır |
| `tek_secim` | 2–50 seçenek, her biri ≤ 150 karakter |
| `coklu_secim` | 2–50 seçenek, isteğe bağlı en fazla seçim sayısı |
| `onay` | Tek onay kutusu |

Her alanın `id` (otomatik, değişmez), `tur`, `etiket` (≤ 200), `aciklama` (isteğe bağlı) ve `zorunlu` bilgisi vardır. **Alan sayısında sınır yoktur.**

```json
{
  "surum": 1,
  "alanlar": [
    { "id": "ad", "tur": "kisa_metin", "etiket": "Ad", "zorunlu": true },
    { "id": "eposta", "tur": "eposta", "etiket": "E-posta", "zorunlu": true },
    { "id": "q7k2", "tur": "tek_secim", "etiket": "Dizüstü bilgisayar getirebilecek misiniz?",
      "zorunlu": true, "secenekler": ["Evet", "Hayır"] },
    { "id": "q9m4", "tur": "uzun_metin", "etiket": "Bu atölyeden beklentiniz nedir?",
      "zorunlu": false }
  ]
}
```

### Kurallar

- Form tanımı sunucuda bir şemaya göre doğrulanır. Şemaya uymayan tanım kaydedilemez.
- Yanıt doğrulaması form tanımından **sunucu tarafında** otomatik üretilir. Tarayıcıdaki doğrulama yalnızca kolaylıktır.
- Etiketler ve seçenekler düz metindir. HTML ve bağlantı girilemez, ekranda kaçışlanarak gösterilir.
- Formda `eposta` türünde alan yoksa onay e-postası gönderilmez ve tekil alan seçilemez (ya da başka bir alan seçilir).
- **Özel nitelikli veri ve gereksiz kimlik bilgisi istenmez:** TC kimlik no, sağlık, din, etnik köken, siyasi görüş, adres ve benzerleri. Bunlar için ayrı alan türü yoktur. Biri bunları metin alanıyla sormaya çalışırsa Yönetim Kurulu'nun onay kontrol listesi yakalar (§8).
- Yanıt gelmeye başladıktan sonra var olan alanlar silinemez ve türü değiştirilemez; yalnızca yeni alan eklenebilir ve etiketler düzeltilebilir. Böylece eski yanıtların anlamı bozulmaz.

## 8. Akışlar

### Onay ilkesi

Yayına giden her şey (duyuru, form, ekip sayfası değişikliği) **Yönetim Kurulu onayından** geçer:

- Onay, Yönetim Kurulu üyesinin panele **kendi hesabıyla, 2FA ile girip** onay ekranında "Onayla"ya basmasıyla verilir. E-postadaki bir bağlantıya tıklayarak onay verilemez.
- Bir şey onaya gönderildiğinde Yönetim Kurulu üyelerine bilgilendirme e-postası gider: "Onay bekleyen 1 form var". E-postada yalnızca başlık ve panel bağlantısı bulunur, içerik yoktur.
- Tek bir Yönetim Kurulu üyesinin onayı yeterlidir.
- Yönetim Kurulu üyesi kendi hazırladığı içeriği de onaylayabilir. Bu durum işlem kaydında "kendi içeriğini onayladı" olarak görünür.
- "Düzeltme iste" denirse içerik not ile birlikte taslağa döner ve hazırlayan kişiye e-posta gider.

### Duyuru

```
Editör: taslak ──▶ onaya gönder ──▶ Yönetim Kurulu: onayla (yayımla) ──▶ site yeniden derlenir (1–2 dk)
                         ▲                         │
                         └──── düzeltme iste ◀─────┘
```

- Yayımlanan duyuru Django API'den (`/api/duyurular/`) okunur. Astro sitesi bu API'yi derleme sırasında çeker.
- Yayımla veya yayından kaldır işlemi Cloudflare Pages'in **deploy hook**'unu tetikler. Art arda gelen tetiklemeler 1 dakikalık pencerede birleştirilir.

### Etkinlik kayıt formu

```
Editör: form taslağı ──▶ onaya gönder ──▶ Yönetim Kurulu: kontrol listesi + onayla ──▶ açık
   ──▶ yanıtlar ──▶ kapanış tarihi veya kontenjan dolunca otomatik kapalı
   ──▶ silinme tarihinde yanıtlar otomatik silinir ──▶ arşiv
```

**Onay kontrol listesi** (onay ekranında işaretlenir; hepsi işaretlenmeden "Onayla" düğmesi açılmaz):

- [ ] İstenen bilgiler etkinlik için gerçekten gerekli mi? Gereksiz kişisel veri isteniyor mu?
- [ ] Özel nitelikli veri (sağlık, din, TC no vb.) soruluyor mu? Soruluyorsa form onaylanmaz.
- [ ] Aydınlatma metni doğru ve güncel mi?
- [ ] Saklama süresi makul mü?
- [ ] Form sahipleri doğru kişiler mi?

**Gönderim:**

- Tekil alan seçildiyse (varsayılan: e-posta) aynı değerle ikinci gönderim engellenir: "Bu e-postayla zaten kayıt olunmuş".
- Kontenjan ve kapanış kontrolü gönderim anında veritabanı kilidiyle yapılır, son yerde yarış durumu olmaz.
- Formda e-posta alanı varsa katılımcıya kısa bir onay e-postası gider (etkinlik adı, tarih, yer, kaydı iptal etmek için iletişim adresi).

### Ekip sayfası

Editör kişileri ekler, düzenler veya sıralar ve değişikliği onaya gönderir. Yönetim Kurulu onaylayınca site yeniden derlenir. "Yayın için yazılı onay alındı" kutusu işaretli olmayan kişi sitede görünmez. Yeni dönem başlarken önceki dönem kopyalanıp düzenlenebilir.

### Kişi verilerinin silinmesini isterse

Yönetim Kurulu ilgili yanıtı panelden siler. Silme işlemi işlem kaydına yazılır (kimin yanıtı olduğu değil, yalnızca yanıt kimliği). Yedeklerden de saklama süresi sonunda kendiliğinden silinir (OPERASYON.md).

### Gece görevleri

- Kapanış tarihi geçen formları kapat.
- Silinme tarihi geçen formların yanıtlarını sil, formu arşivle.
- Bitiş tarihi geçen rol atamalarını etkisizleştir; 14 gün içinde bitecekler için Başkan'a e-posta gönder.
- 1 yıldan eski işlem kayıtlarını sil.

## 9. Güvenlik kuralları

Bu kurallar zorunludur. Gevşetmek için önce kullanıcıya sorulur.

**Erişim**
- Panel internete açıktır; Django Admin ve SSH yalnızca VPN üzerinden erişilir.
- Tüm panel kullanıcılarında **2FA zorunlu** (`django-otp`, TOTP). 2FA kurmayan kullanıcı panelde hiçbir ekranı göremez.
- Hatalı giriş kilidi: `django-axes` (ör. 5 hatalı denemede 30 dakika).
- Yeni bir cihaz veya tarayıcıdan giriş yapıldığında kullanıcıya e-posta uyarısı gider.
- Oturum 8 saatte veya 1 saat hareketsizlikte sona erer. Çerezler `Secure`, `HttpOnly`, `SameSite=Lax`.
- Şifre en az 12 karakter, Django'nun şifre doğrulayıcıları açık (yaygın şifre listesi dahil).
- Hesaplar davetle açılır. Kendi kendine kayıt olunamaz. Davet bağlantısı tek kullanımlık ve 48 saat geçerli.
- Rol atamalarının bitiş tarihi vardır; süresi dolan rol hiçbir yetki vermez.

**Yetki**
- Her görünümde yetki **nesne düzeyinde** kontrol edilir: form sahibi, URL'yi değiştirerek başka formun yanıtlarını göremez.
- **Her görünüm için yetkisiz erişim testi yazılır** (giriş yapmamış, yanlış rol, süresi dolmuş rol, başka formun sahibi). Test yoksa iş bitmiş sayılmaz.
- Onay işlemleri yalnızca POST ile, CSRF korumalı ve geçerli bir Yönetim Kurulu rolüyle yapılabilir.
- Django Admin yalnızca teknik sorumlulara açık. `Yanit` modeli Admin'e kaydedilmez veya içerik alanları gizlenir.

**Girdi ve çıktı**
- Duyuru metni editörden HTML olarak gelir ve **kaydedilmeden önce** `nh3` ile izin listesine göre temizlenir. İzin listesi: `p, br, h2, h3, strong, em, a[href], ul, ol, li, blockquote`. Bağlantılar `rel="noopener noreferrer"` alır, yalnızca `https:` ve `mailto:` adreslerine izin verilir.
- Form etiketleri ve yanıtlar her zaman kaçışlanarak gösterilir. Hiçbir yerde `|safe` / `mark_safe` kullanılmaz (temizlenmiş duyuru gövdesi hariç).
- **CSV dışa aktarımı:** `=`, `+`, `-`, `@`, tab veya satır başı ile başlayan hücrelerin başına `'` eklenir (Excel formül enjeksiyonu). Dosya UTF-8 BOM ile yazılır ki Türkçe karakterler Excel'de doğru açılsın.
- Görseller (duyuru kapağı, ekip fotoğrafları) güvenli yükleme akışıyla gelir (ARCHITECTURE.md). Sunucuda yeniden boyutlandırılır ve EXIF bilgisi silinir.

**Herkese açık formlar**
- Spam koruması: gizli tuzak alan + IP başına istek sınırı (Redis'te kısa süreli sayaç, IP veritabanına yazılmaz).
- CSRF koruması açık.
- Hata mesajları başka formlar veya kişiler hakkında bilgi vermez.

**İz ve kayıt**
- `IslemKaydi`'na yazılan eylemler: giriş, başarısız giriş, yeni cihazdan giriş, davet, rol atama/kaldırma, 2FA sıfırlama, onaya gönderme, onaylama, düzeltme isteme, yayımlama/kaldırma, form açma/kapama, **yanıtları görüntüleme**, **CSV indirme**, yanıt silme.
- Loglara ve Sentry'ye kişisel veri gitmez (`send_default_pii=False`, form verisi loglanmaz).

## 10. Arayüz kuralları

- Renk, yazı tipi ve boşluklar sitenin `tokens.css` dosyasından gelir (DESIGN.md). Panel için yeni renk eklenmez. Durum bilgisi (taslak, onay bekliyor, yayında, kapalı) mevcut lacivert ve gri tonlarla, etiket (chip) biçiminde gösterilir.
- **Düzen:** Solda dar bir menü (Ana ekran, Duyurular, Etkinlikler, Yanıtlar, Ekip, Kullanıcılar, İşlem kaydı), sağda içerik. 900px altında menü üstte açılır bir menüye dönüşür. Editörler ve Yönetim Kurulu telefondan da duyuru yazıp onay verebilmeli.
- **Form oluşturucu:** Alanlar alt alta kartlar halinde; her kartta tür, etiket, zorunlu anahtarı, yukarı/aşağı ve sil. Sona "Alan ekle". Sağda/altta formun canlı önizlemesi. Kaldırılamayan aydınlatma alanı kilit simgesiyle gösterilir.
- **Tablolar:** Satır çizgileri, kart yok (sitenin liste diliyle aynı). Dar ekranda yatay kaydırma kutusu içinde.
- **Metinler:** Düğmeler ne olacağını söyler: "Onaya gönder", "Onayla ve yayımla", "Formu kapat". Hata mesajları neyin yanlış olduğunu ve nasıl düzeltileceğini söyler.
- **Geri dönüşsüz işlemler** (yayından kaldırma, yanıt silme, formu kapatma, rol kaldırma) sayfa içinde bir onay adımı ister. Tarayıcının `confirm()` penceresi kullanılmaz.
- **Boş durumlar:** "Henüz duyuru yok. İlk duyuruyu yazmak için Yeni duyuru'ya basın." gibi yol gösterir.
- Erişilebilirlik kuralları sitedekiyle aynı: etiketli form alanları, klavye ile kullanım, görünür odak, 4.5:1 kontrast.

## 11. Teknik yapı

- **Sunucu tarafında şablonlar:** Panel ve herkese açık form sayfaları Django şablonlarıyla üretilir. Etkileşim (önizleme, alan ekleme/sıralama) için küçük JavaScript veya htmx kullanılır. Ayrı bir React/SPA uygulaması kurulmaz. Metin editörü bileşeni bu kuralın tek istisnasıdır.
- **Ortak stil:** `frontend/src/styles/tokens.css` tek kaynaktır. Backend derlenirken bu dosya backend'in statik dosyalarına kopyalanır. Panel için ek stiller `backend/panel/static/panel/panel.css` içinde, yalnızca bu değişkenleri kullanır.
- **Metin editörü:** Henüz seçilmedi (STATUS.md, Bekleyen kararlar). Seçilen editörün araç çubuğu §9'daki izin listesiyle sınırlı tutulur: kalın, italik, başlık (h2/h3), liste, alıntı, bağlantı. Seçim DECISIONS.md'ye yazılır.
- **Önizleme:** Duyurunun panel içindeki önizlemesi, sitedeki gönderi sayfasının HTML yapısını ve sınıflarını kullanan bir şablonla gösterilir. Site tasarımı değiştikçe bu şablon da güncellenir.
- **Site ile bağlantı:** Astro, derleme sırasında `/api/duyurular/`, `/api/etkinlikler/` ve `/api/ekip/` uç noktalarından yayımlanmış içeriği çeker. Bu uç noktalar yalnızca yayımlanmış içeriği döndürür; ekip uç noktası yalnızca yayın onayı olan kişileri ve sitede görünmesi gereken alanları içerir. Gündem gönderisindeki "Kayıt ol" düğmesi `/kayit/<slug>/` sayfasına gider.
- **Faz 1'den geçiş:** `frontend/src/content/gundem/` altındaki Markdown gönderileri ve `frontend/src/data/ekip.json` bir yönetim komutuyla (`manage.py faz1_aktar`) Django'ya aktarılır. Geçişten sonra Astro'daki gündem ve ekip verisi API'den beslenir.

## 12. Uygulama sırası

Her aşama ayrı PR'lar halinde, kabul ölçütleri sağlanınca tamamlanır. Her aşama sonunda STATUS.md güncellenir.

**A1: Temel ve hesaplar**
- `accounts` (davet, rol atamaları ve bitiş tarihleri), 2FA zorunluluğu, giriş kilidi, yeni cihaz uyarısı, `denetim`, `ilk_yonetici` komutu, panelin iskeleti ve menüsü, Kullanıcılar ekranı.
- *Kabul:* 2FA'sız kullanıcı hiçbir panel sayfasını açamıyor. 5 hatalı girişte kilit devreye giriyor. Süresi dolmuş rol hiçbir yetki vermiyor. Yalnızca Başkan ve Başkan Yardımcısı davet ve rol atama yapabiliyor. Giriş, davet ve rol değişiklikleri işlem kaydına düşüyor. Yetkisiz erişim testleri geçiyor.

**A2: Onay altyapısı ve duyurular**
- Ortak onay akışı (onaya gönder, onayla, düzeltme iste, e-posta bildirimleri), `duyurular`, metin editörü + `nh3`, önizleme, `/api/duyurular/`, deploy hook, Astro'nun API'den beslenmesi, Markdown'dan aktarım.
- *Kabul:* Editör yayımlayamıyor, Yönetim Kurulu yayımlayabiliyor. E-postadaki bağlantı onay vermiyor, yalnızca panele götürüyor. `<script>` içeren metin temizlenerek kaydediliyor. Yayımlanan duyuru 2 dakika içinde sitede görünüyor. API taslakları döndürmüyor.

**A3: Ekip sayfası**
- `ekip` modelleri, Ekip ekranı, fotoğraf yükleme, onay akışı, `/api/ekip/`, Astro ekip sayfasının API'den beslenmesi, `ekip.json`'dan aktarım.
- *Kabul:* Yayın onayı olmayan kişi API'de ve sitede görünmüyor. Değişiklik onaylanmadan sitede görünmüyor. Fotoğrafların EXIF bilgisi siliniyor.

**A4: Etkinlikler ve formlar**
- `etkinlikler`, `formlar` (hazır alanlar, alan türleri, şema doğrulaması, onay kontrol listesi), herkese açık form sayfası, kontenjan ve kapanış, onay e-postası, spam koruması.
- *Kabul:* Aydınlatma metni onayı kaldırılamıyor ve işaretlenmeden form gönderilemiyor. Şemaya uymayan form kaydedilemiyor. Kontenjan aşılamıyor (eşzamanlı gönderim testiyle). Tekil alanla ikinci kayıt engelleniyor. Kapanış tarihinden sonra gönderim kabul edilmiyor. Yanıt geldikten sonra alan silinemiyor.

**A5: Yanıtlar ve saklama**
- Yanıt tablosu, arama, CSV indirme (formül enjeksiyonu korumalı), tek yanıt silme, gece görevleri.
- *Kabul:* Form sahibi başka formun yanıtlarını göremiyor (test). Görüntüleme ve indirme işlem kaydına düşüyor. `=HYPERLINK(...)` içeren yanıt CSV'de etkisizleşiyor. Silinme tarihi geçen yanıtlar gece görevinde siliniyor.

**A6: Cilalama**
- Ana ekran özetleri, boş durumlar, telefon görünümü, erişilebilirlik kontrolü, editörler ve Yönetim Kurulu için kısa kullanım rehberi (`docs/PANEL-KULLANIM.md`).
