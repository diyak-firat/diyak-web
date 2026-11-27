// Kaynak türleri. content.config.ts de kullandığı için astro:content'e bağımlı olmayan ayrı dosyada.
export const TURLER = ['Yayın', 'Veri kümesi', 'Araç'] as const;
export type Tur = (typeof TURLER)[number];
