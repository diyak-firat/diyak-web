// Gündem etiketleri. content.config.ts de bu dosyayı kullandığı için burada başka import olmamalı.
export const ETIKETLER = ['Etkinlik', 'Duyuru', 'Çağrı', 'Yayın'] as const;
export type Etiket = (typeof ETIKETLER)[number];
