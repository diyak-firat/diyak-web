// ekip.json dosyasını derleme sırasında doğrular. Hatalı alan varsa site derlenmez
// ve hata mesajı hangi alanın yanlış olduğunu gösterir.
import { z } from 'astro/zod';
import veri from '../data/ekip.json';

/** Bağlantı anahtarlarının ekranda görünen adları. Listede olmayan anahtar olduğu gibi gösterilir. */
export const BAGLANTI_ADLARI: Record<string, string> = {
  linkedin: 'LinkedIn',
  github: 'GitHub',
  kaggle: 'Kaggle',
  huggingface: 'Hugging Face',
  behance: 'Behance',
  web: 'Kişisel sayfa',
};

const kisi = z.object({
  rol: z.string(),
  ad: z.string(),
  eposta: z.string().optional(),
  foto: z.string().optional(),
  baglantilar: z.record(z.string(), z.string()).optional(),
});

const danisman = z.object({
  ad: z.string(),
  birim: z.string(),
  eposta: z.string(),
  foto: z.string().optional(),
  profiller: z.array(z.object({ ad: z.string(), url: z.string() })),
});

const ekipSemasi = z.object({
  donem: z.string(),
  danisman,
  yonetim: z.array(kisi),
  birimler: z.array(z.object({ ad: z.string(), uyeler: z.array(kisi) })),
});

export type Kisi = z.infer<typeof kisi>;
export type Danisman = z.infer<typeof danisman>;

export const ekip = ekipSemasi.parse(veri);
