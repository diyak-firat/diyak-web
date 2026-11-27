## Ne değişti, neden?

<!-- Kısa ve açık: bu PR ne yapıyor, hangi sorunu çözüyor? -->

## Nasıl test edilir?

<!-- İnceleyen kişinin izleyeceği adımlar. Ör: "/ekip sayfasını telefonda aç, kartların iki sütun olduğunu gör" -->

1.

## Migration

<!-- Migration yoksa "Yok" yazın. Varsa: hangi tablo/alan değişiyor, veri kaybı riski var mı, nasıl geri alınır? -->

Yok

> Migration varsa: yayından önce sunucuda `sudo /opt/diyak/ops/yedekle.sh elle migration-oncesi` çalıştırılmalı. Yayın betiği son 15 dakikada elle yedek görmezse durur (docs/OPERASYON.md).

## İlgili issue

Closes #

## Kontrol listesi

- [ ] `npm run check` ve `npm run build` hatasız geçiyor
- [ ] Masaüstünde (1280px) baktım; telefonda (390px) taşma veya kırılma yok
- [ ] Yeni renk veya yazı tipi eklemedim, `tokens.css` değişkenlerini kullandım
- [ ] Gizli bilgi (şifre, token, kişisel veri, yedek dosyası) eklemedim
- [ ] Migration varsa yukarıdaki bölümü doldurdum, main'e birleşmiş eski migration'lara dokunmadım
- [ ] Gerekiyorsa `STATUS.md` ve dokümanları güncelledim
