# İçerik Ekleme Rehberi

Bu rehber kod bilmeyen ekip üyeleri içindir ve Faz 1 için geçerlidir. Faz 2'de duyurular, formlar ve ekip sayfası sitenin kendi yönetim panelinden hazırlanacak ([PANEL.md](PANEL.md)).

Bu aşamada tüm içerik GitHub üzerinden, tarayıcıdan düzenlenebilir. Yaptığınız değişiklik bir PR olarak açılır, biri baktıktan sonra yayına çıkar.

## GitHub'da tarayıcıdan düzenleme

1. Repoda ilgili dosyayı açın.
2. Sağ üstteki kalem simgesine ("Edit this file") basın. Yeni dosya için klasöre girip **Add file → Create new file** seçin.
3. Değişikliği yapın.
4. **Commit changes** düğmesine basın, açılan pencerede **Create a new branch** seçeneğini seçin ve kısa bir açıklama yazın (ör. `feat(gundem): okuma grubu duyurusu ekle`).
5. **Propose changes** → **Create pull request**. Ekipten biri bakıp birleştirdiğinde değişiklik birkaç dakika içinde sitede görünür.

## Gündem gönderisi eklemek

Klasör: `frontend/src/content/gundem/`

Dosya adı, gönderinin adresi olur. Küçük harf, Türkçe karakter ve boşluk olmadan, tire ile yazın: `2026-11-okuma-grubu.md` → `/gundem/2026-11-okuma-grubu`

**Duyuru, Çağrı veya Yayın:**

```markdown
---
baslik: "Yeni dönem üye kayıtları açıldı"
tarih: 2026-11-10
etiket: Duyuru
ozet: "Fırat Üniversitesine kayıtlı tüm öğrenciler başvurabilir."
---

Buraya gönderinin tamamı yazılır. Paragraflar arasına boş satır bırakın.

**Kalın**, *italik* ve [bağlantı](https://ornek.com) kullanabilirsiniz.
```

**Etkinlik** (tarih, saat ve yer de yazılır):

```markdown
---
baslik: "Okuma grubu: Makale başlığı"
tarih: 2026-11-10
etiket: Etkinlik
ozet: "Makaleyi birlikte okuyup tartışacağız."
etkinlik:
  zaman: 2026-11-14T15:00:00+03:00
  yer: "Mühendislik Fakültesi, Z-12"
---
```

Alanlar:

| Alan | Zorunlu | Açıklama |
| --- | --- | --- |
| `baslik` | evet | Gönderi başlığı |
| `tarih` | evet | Yayın tarihi, `YYYY-AA-GG` biçiminde |
| `etiket` | evet | `Etkinlik`, `Duyuru`, `Çağrı` veya `Yayın` |
| `ozet` | evet | Listede görünen bir iki cümle |
| `etkinlik` | yalnızca Etkinlik'te | `zaman` (saat dilimiyle) ve `yer` |
| `taslak` | hayır | `true` yazılırsa gönderi yayımlanmaz |

Yazım hatası yaparsanız (ör. etiketi `duyuru` diye küçük harfle yazarsanız) site derlenmez ve PR'da hata görünür. Hata mesajı hangi alanın yanlış olduğunu söyler.

## Ekip bilgilerini güncellemek

Dosya: `frontend/src/data/ekip.json`

Her kişi şu alanları taşır:

```json
{
  "rol": "Birim Sorumlusu",
  "ad": "Ad Soyad",
  "eposta": "ad.soyad@ornek.com",
  "foto": "/ekip/ad-soyad.jpg",
  "baglantilar": { "linkedin": "https://linkedin.com/in/...", "github": "https://github.com/..." }
}
```

- `foto` ve `baglantilar` isteğe bağlıdır. Yazılmazsa kartta silüet görünür ve bağlantı satırı çıkmaz.
- Fotoğraflar `frontend/public/ekip/` klasörüne kare (en az 400×400 px) olarak eklenir.
- Her dönem başında `donem` alanı güncellenir.

> **KVKK:** İsim, fotoğraf, e-posta ve bağlantılar ancak kişinin **yazılı onayıyla** yayımlanır. Kişi onayını geri çekerse bilgileri hemen kaldırılır.

## Yayın ve kaynak eklemek

Dosya: `frontend/src/data/kaynaklar.json`. Yeni öğeyi listenin başına ekleyin. `tur` alanı `Yayın`, `Veri kümesi` veya `Araç` olur.

## Belgeler

Üye kayıt formu ve tüzük PDF'leri `frontend/public/belgeler/` klasöründe durur. Dosya adı aynı kalacak şekilde yenisiyle değiştirilir.
