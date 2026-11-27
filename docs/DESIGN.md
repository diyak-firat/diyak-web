# Tasarım Sistemi

Onaylanmış tasarımın tek dosyalık prototipi: [design/prototip.html](../design/prototip.html). Tarayıcıda açıp bakabilirsiniz. Astro sürümü bu prototipe birebir uymalı.

## İlkeler

- **Akademik ve sade.** Referanslar: Stanford NLP, Edinburgh NLP, ACL Anthology gibi lab siteleri. İçerik önde, tarihli listeler, bolca boşluk.
- **İçerik kartlarla değil çizgilerle ayrılır.** Liste satırları ince yatay çizgilerle bölünür. Kutu, gölge ve köşe yuvarlaklığı yalnızca öne çıkması gereken tek öğede kullanılır (biçimbirim kutusu, üyelik paneli).
- **Topluluğa özgü bir ayrıntı:** Girişteki "anla·ya·ma·dık·lar·ımız" biçimbirim ayrıştırması, Türkçe NLP odağını tek bakışta anlatır ve logodaki çizgi motifini sürdürür.
- **Yapay zekâ klişesi yok:** gradyan, parlayan ağ görseli, robot, glassmorphism, emoji, "geleceği keşfedin" tarzı pazarlama dili kullanılmaz.

## Renkler

Tüm renkler `frontend/src/styles/tokens.css` içinde tanımlıdır. Kodda sabit renk yazılmaz.

| Değişken | Değer | Kullanım |
| --- | --- | --- |
| `--navy` | `#1E2142` | Ana renk: başlıklar, birincil düğmeler, logo, koyu bantlar |
| `--navy-2` | `#282C55` | Koyu bant içindeki panel (üyelik) |
| `--navy-3` | `#161935` | Alt bilgi zemini |
| `--navy-line` | `#3A3D63` | Koyu zemindeki çizgiler |
| `--accent` | `#E5533A` | Mercan vurgu — **çok az kullanılır** |
| `--hover` | `#C2412B` | Bağlantı üzerine gelince |
| `--ink` | `#1A1A1F` | Gövde metni |
| `--text` | `#3A3C4A` | İkincil metin |
| `--muted` | `#55586A` | Tarih, etiket, açıklama |
| `--line` | `#E3E3E8` | Ayırıcı çizgiler |
| `--line-strong` | `#C9CBDA` | Çerçeveli düğmeler |
| `--tint` | `#F5F5F7` | Açık gri bant ve kutular |
| `--chip` | `#EEEEF3` | Etiket zemini, fotoğraf yer tutucusu |
| `--paper` | `#FFFFFF` | Sayfa zemini |
| `--on-navy` | `#C9CBDA` | Koyu zemindeki metin |
| `--on-navy-muted` | `#A3A6C2` | Koyu zemindeki küçük etiketler |

**Mercan nerede kullanılır:** logodaki kısa çizgi, biçimbirim kutusunda kök çizgisi, aktif menü öğesinin alt çizgisi, alt bilgideki çizgi motifi, bağlantı hover rengi. Başka yerde kullanılmaz.

## Yazı tipleri

| Rol | Yazı tipi | Nerede |
| --- | --- | --- |
| Başlık | Source Serif 4 (600, italik 400) | h1, h2, gönderi başlıkları, isimler |
| Gövde | IBM Plex Sans (400, 500, 600) | Metin, menü, düğmeler |
| Yardımcı | IBM Plex Mono (400, 500) | Tarihler, etiketler, küçük üst başlıklar, numaralar |

Üçü de Türkçe karakterleri tam destekler. Yazı boyutları:

| Öğe | Boyut |
| --- | --- |
| Sayfa başlığı (h1) | `clamp(32px, 5vw, 52px)`, satır yüksekliği 1.1 |
| Bölüm başlığı (h2) | 30px (Ekip sayfasında 26px) |
| Gönderi başlığı | 21px |
| Giriş metni | 18px / 1.6 |
| Gövde | 15–17px |
| Üst başlık (eyebrow) | 13px mono, büyük harf, harf aralığı 0.07em |
| Etiket | 12px mono, büyük harf |

## Düzen

- İçerik genişliği en fazla **1120px**, yan boşluk en az **20px**.
- Bölüm iç boşluğu: 56px (Hakkımızda bandı 80px). Bölümler içindeki gruplar arasında 72px.
- Satır listelerinde sol sütun 120px (tarih veya tür), sağ sütun içerik. Telefonda alt alta geçer.
- Izgaralar: masaüstünde 4 sütun → 900px altında 2 → 560px altında 1. Ekip kartları: 4 → 3 → 2.
- Telefon genişliğinde (390px) sayfa yatay kaydırma yapmaz ve kırılmaz. Mobil görünümün ayrıntılı tasarımı, masaüstü tamamlandıktan sonra ayrıca ele alınacak (K-20).

## Bileşenler

**Üst menü (Header)**
- Solda logo + "DİYAK / Fırat Üniversitesi". Sağda bağlantılar, "Üye ol" düğmesi, ince bir çizgiyle ayrılmış Fırat Üniversitesi logosu (resmî kurumsal kimlik kılavuzundaki dairesel sürüm). SKS'nin ayrı logosu olmadığı için adı alt bilgide yazar (K-22).
- Sayfanın üstüne yapışır. Aşağı kaydırınca gizlenir, biraz yukarı kaydırınca geri gelir.
- 900px altında bağlantılar bir menü düğmesinin içine toplanır.
- Bulunulan sayfa mercan alt çizgiyle işaretlenir.

**Düğmeler**
- Birincil: lacivert zemin, beyaz yazı, 48px yükseklik, 4px köşe.
- İkincil: lacivert çerçeve, şeffaf zemin.
- Koyu zeminde: beyaz zemin + lacivert yazı, ya da açık çerçeve.

**Gündem satırı**
- Solda yayın tarihi (mono). Sağda etiket, başlık (serif), kısa özet.
- Etiketler: **Etkinlik** (lacivert zemin, beyaz yazı — diğerlerinden ayrışır), Duyuru, Çağrı, Yayın (açık gri zemin).
- Etkinlik gönderilerinde altta açık gri bir kutu içinde takvim ve konum ikonlarıyla tarih/saat ve yer.
- Üstte filtre düğmeleri (Tümü, Etkinlik, Duyuru, Çağrı, Yayın), seçili olan lacivert dolgulu.

**Kaynak satırı:** Solda tür (Yayın, Veri kümesi, Araç), sağda başlık, yazarlar/açıklama, mono bağlantılar (PDF, BibTeX, Kod, GitHub, Hugging Face, Kaggle).

**Hakkımızda bandı:** Lacivert zemin. Büyük serif ana cümle + iki kısa paragraf, dört ilke (i.–iv.), en altta üyelik paneli. Hemen ardından bir ton koyu alt bilgi gelir. Lacivert bant ile alt bilgi arasına beyaz bölüm girmez.

**Kişi kartı (Ekip):** Kare fotoğraf (yoksa silüet yer tutucu), rol (mono, büyük harf; sorumlular lacivert, üyeler gri), isim (serif), e-posta, isteğe bağlı bağlantılar. Teknik olmayan birimlerde bağlantı zorunlu değil.

**Danışman kartı:** Büyük fotoğraf, unvan ve isim, fakülte/bölüm, e-posta, akademik profil düğmeleri (ORCID, LinkedIn, Google Scholar, Scopus, DergiPark, Web of Science, YÖK Akademik).

## Sayfalar

**Ana sayfa:** Giriş (başlık + biçimbirim kutusu) → Gündem → Neler yapıyoruz → Yayınlar ve açık kaynaklar → Hakkımızda + Üyelik → Alt bilgi

**Ekip:** Başlık ve dönem etiketi → 01 Akademik Danışman → 02 Yönetim → 03 Proje ve Araştırma Birimi → 04 İletişim Birimi → 05 Etkinlik ve Sponsorluk Birimi → 06 Medya ve Tasarım Birimi → "Bir birimde görev almak ister misiniz?" → Alt bilgi

Ekip sayfasında açıklama metni, birim görev tanımları ve "Ana sayfa / Ekip" yol göstericisi **bilinçli olarak yok**.

**Gündem arşivi** (`/gundem`) ve **gönderi sayfası** (`/gundem/<ad>`): aynı satır düzeni ve tipografi.

## Erişilebilirlik

- Her sayfa `lang="tr"`.
- Dokunma hedefleri en az 44px, metin kontrastı en az 4.5:1.
- Klavye odağı mercan çerçeveyle görünür.
- Dekoratif SVG'ler `aria-hidden="true"`. Yalnızca ikondan oluşan düğmelerde `aria-label`.
- Hareketi azaltma tercihinde (`prefers-reduced-motion`) menü animasyonu ve yumuşak kaydırma kapanır.

## Metin dili

- Sade, doğrudan Türkçe. Kısa cümleler.
- Pazarlama dili yok. Topluluğun gerçekten yaptığını anlatan cümleler (tüzüğün 4. ve 5. maddelerinden).
- Bilinmeyen bilgi uydurulmaz, köşeli parantezle yer tutucu yazılır: `[Ad Soyad]`.
