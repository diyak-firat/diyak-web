# Katkı Rehberi

Bu dosya, DİYAK web sitesinde nasıl birlikte çalıştığımızı anlatır. Kod bilmeden içerik eklemek istiyorsanız [docs/CONTENT.md](docs/CONTENT.md) dosyası yeterli.

## Temel kurallar

1. **main her zaman çalışır durumdadır.** main'e giren her şey yayına çıkabilir. Yarım iş main'e girmez.
2. **Her iş kendi branch'inde yapılır** ve **PR ile** main'e birleşir. main'e doğrudan push kapalıdır.
3. **İşler küçük tutulur.** Bir PR tek bir iş yapar. Büyük bir işi parçalara bölün.
4. **Gizli bilgi repoya girmez.** Şifre ve anahtarlar `.env` dosyasında durur, `.env` repoya eklenmez.

## İş akışı

```
issue → branch → commit'ler → PR → inceleme → squash merge → yayın
```

### 1. İşi seç

Yapılacak işler GitHub Issues ve proje panosunda (Yapılacak → Yapılıyor → İncelemede → Bitti) durur. [STATUS.md](STATUS.md) dosyası da genel durumu özetler. Bir işi alınca issue'yu kendinize atayın ve panoda "Yapılıyor"a taşıyın.

Yeni katılanlar için kolay işler `good first issue` etiketiyle işaretlenir.

### 2. Branch aç

Her zaman güncel main'den başlayın:

```bash
git switch main
git pull
git switch -c feat/gundem-filtre
```

Branch adları işin türüyle başlar:

| Önek | Ne için |
| --- | --- |
| `feat/` | Yeni özellik |
| `fix/` | Hata düzeltme |
| `docs/` | Doküman |
| `refactor/` | Davranışı değiştirmeyen kod düzenlemesi |
| `chore/` | Bağımlılık güncelleme, ayar gibi bakım işleri |

### 3. Commit at

Commit mesajları **Türkçe**, Conventional Commits biçiminde, emir kipinde ve küçük harfle yazılır:

```
<tür>(<kapsam>): <ne yapıldığı>

feat(gundem): etiket filtresi ekle
fix(ekip): telefonda fotoğraf taşmasını düzelt
docs: kurulum adımlarını güncelle
```

Kapsam isteğe bağlıdır ve değişikliğin yapıldığı yeri söyler (`gundem`, `ekip`, `header`, `footer`…).

İyi alışkanlıklar:
- Her commit tek bir değişikliği anlatsın. "çeşitli düzeltmeler" gibi mesajlardan kaçının.
- `git add -p` ile değişiklikleri parça parça gözden geçirerek ekleyin.
- Commit'ten önce `npm run check` ve `npm run build` çalıştırın.
- Birlikte çalıştığınız birinin katkısını commit mesajının sonuna şu satırla ekleyin:
  ```
  Co-authored-by: Ad Soyad <eposta@ornek.com>
  ```

### 4. PR aç

```bash
git push -u origin feat/gundem-filtre
gh pr create --fill     # ya da GitHub sayfasından "Compare & pull request"
```

PR açıklaması şablonla gelir. Doldurun:
- **Ne değişti, neden?** Kısa ve açık.
- **Nasıl test edilir?** İnceleyen kişinin izleyeceği adımlar.
- **İlgili issue:** `Closes #12` yazarsanız PR birleşince issue kendiliğinden kapanır.

### 5. İnceleme

- PR'ı ekipten **müsait olan** biri inceler. Ayrıca bir sahiplik dosyası (CODEOWNERS) kullanmıyoruz.
- Ekipte tek geliştirici varken onay şartı yoktur. İkinci geliştirici geldiğinde **en az 1 onay** zorunlu olur. Kimse kendi PR'ını onaylayamaz.
- İnceleme bir iki gün içinde yapılır. Bekleyen PR ekibi en çok yavaşlatan şeydir.
- Yorumlar koda yapılır, kişiye değil. Zorunlu olmayan küçük önerileri `nit:` diye başlatın.
- İnceleyen kişi üç seçenekten birini kullanır: **Approve** (onay), **Request changes** (düzeltme iste), **Comment** (yalnızca yorum).
- İstenen düzeltmeleri aynı branch'e yeni commit olarak atın. PR kendiliğinden güncellenir.

Agent ile (Claude Code vb.) yazılan kod da aynı incelemeden geçer. **PR'ı açan kişi içeriğinden sorumludur.**

### 6. Birleştirme

- Yalnızca **Squash and merge** kullanılır. PR, main'e tek bir commit olarak girer.
- Birleştirmeden önce sayfanın önizleme linkini (Cloudflare Pages her PR için üretir) telefonda ve masaüstünde açıp bakın.
- Birleşen branch otomatik olarak silinir.

## Branch'iniz main'in gerisinde kalırsa

Siz çalışırken başkasının PR'ı main'e birleşmiş olabilir. Branch'inizi güncel main'in üzerine taşıyın:

```bash
git fetch origin
git rebase origin/main
# çakışma çıkarsa: dosyayı düzeltin → git add <dosya> → git rebase --continue
git push --force-with-lease
```

`--force-with-lease`, başkasının o branch'e attığı commit'leri yanlışlıkla silmenizi engeller. Düz `--force` kullanmayın.

Rebase'e alışana kadar PR sayfasındaki **Update branch** düğmesini de kullanabilirsiniz. Squash merge kullandığımız için main'in geçmişi iki yolda da temiz kalır.

## Sık kullanılan komutlar

```bash
git status                       # ne değişti?
git diff                         # değişikliklerin ayrıntısı
git log --oneline -10            # son 10 commit
git switch -                     # bir önceki branch'e dön
git restore <dosya>              # dosyadaki commit edilmemiş değişikliği geri al
git commit --amend               # son commit'i düzelt (henüz push edilmediyse)
git stash / git stash pop        # yarım işi kenara koy / geri getir
```

## Yayın

main'e birleşen her değişiklik Cloudflare Pages üzerinden otomatik olarak yayına çıkar. Önemli sürümlerde (ör. Faz 1'in tamamlanması) GitHub'da bir sürüm etiketi açılır: `v1.0.0`.
