// Tarih biçimleri. Tüm tarihler Türkiye saatine göre gösterilir.

const TZ = 'Europe/Istanbul';

/** 10.11.2026 */
export function kisaTarih(d: Date): string {
  return new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: TZ,
  }).format(d);
}

/** 14 Kasım 2026, 15:00 */
export function etkinlikZamani(d: Date): string {
  const gun = new Intl.DateTimeFormat('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: TZ,
  }).format(d);
  const saat = new Intl.DateTimeFormat('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: TZ,
  }).format(d);
  return `${gun}, ${saat}`;
}

/** <time datetime="..."> için */
export function isoTarih(d: Date): string {
  return d.toISOString();
}
