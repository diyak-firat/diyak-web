/*
 * Duyuru düzenleme ekranı: canlı önizleme ve etkinlik alanlarının gösterimi.
 * JavaScript kapalıyken form olduğu gibi çalışır; önizleme son kaydedilen hali gösterir.
 */
(() => {
  const form = document.querySelector('[data-duyuru-formu]');
  const onizleme = document.querySelector('.onizleme');
  if (!form || !onizleme) return;

  const alan = (ad) => form.elements.namedItem(ad);
  const hedef = (ad) => onizleme.querySelector(`[data-onizleme-${ad}]`);
  const etkinlikAlanlari = form.querySelector('[data-etkinlik-alanlari]');
  // Sitedeki etkinlikZamani() ile aynı biçim: "14 Kasım 2026, 15:00" (frontend/src/lib/tarih.ts)
  const gunBicimi = new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
  const saatBicimi = new Intl.DateTimeFormat('tr-TR', { hour: '2-digit', minute: '2-digit' });
  const zamanBicimi = { format: (d) => `${gunBicimi.format(d)}, ${saatBicimi.format(d)}` };

  function metin(ad, yerTutucu) {
    hedef(ad).textContent = alan(ad).value.trim() || yerTutucu;
  }

  function guncelle() {
    metin('baslik', '[Başlık]');
    metin('ozet', '[Özet]');
    const etiket = alan('etiket');
    const etkinlik = etiket.value === 'etkinlik';
    const etiketOge = hedef('etiket');
    etiketOge.textContent = etiket.options[etiket.selectedIndex].text;
    etiketOge.classList.toggle('etkinlik', etkinlik);
    etkinlikAlanlari.hidden = !etkinlik;
    hedef('etkinlik').hidden = !etkinlik;
    const zaman = alan('etkinlik_baslangic').value;
    hedef('zaman').textContent = zaman ? zamanBicimi.format(new Date(zaman)) : '[Tarih ve saat]';
    hedef('yer').textContent = alan('etkinlik_yer').value.trim() || '[Yer]';
  }

  form.addEventListener('input', guncelle);
  form.addEventListener('change', guncelle);
  // Gövde editörden gelir (editor.js). Editörün ürettiği HTML yalnızca izin listesindeki öğeleri
  // içerir; sunucu kaydederken ayrıca temizler.
  form.addEventListener('editor-degisti', (olay) => {
    hedef('govde').innerHTML = olay.detail.html;
  });
  guncelle();
})();
