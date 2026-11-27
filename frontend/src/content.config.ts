// İçerik koleksiyonlarının şemaları. Alan ekleyip çıkarırken docs/CONTENT.md dosyasını da güncelle.
import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';
import { ETIKETLER } from './lib/etiketler';
import { TURLER } from './lib/kaynakTurleri';

const gundem = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/gundem' }),
  schema: z
    .object({
      baslik: z.string(),
      tarih: z.coerce.date(),
      etiket: z.enum(ETIKETLER),
      ozet: z.string(),
      etkinlik: z
        .object({
          zaman: z.coerce.date(),
          yer: z.string(),
        })
        .optional(),
      taslak: z.boolean().default(false),
      /** Yer tutucu örnek gönderi. Gerçek içerik gelince silinecek. */
      ornek: z.boolean().default(false),
    })
    .refine((d) => d.etiket !== 'Etkinlik' || d.etkinlik !== undefined, {
      message: 'Etkinlik gönderilerinde "etkinlik" alanı (zaman ve yer) zorunludur.',
      path: ['etkinlik'],
    }),
});

const kaynaklar = defineCollection({
  loader: file('src/data/kaynaklar.json'),
  schema: z.object({
    sira: z.number(),
    tur: z.enum(TURLER),
    baslik: z.string(),
    alt: z.string(),
    baglantilar: z.array(z.object({ ad: z.string(), url: z.string() })),
    /** Ham BibTeX kaydı. Verilirse satırda açılır kutu ve kopyalama düğmesi çıkar. */
    bibtex: z.string().optional(),
  }),
});

export const collections = { gundem, kaynaklar };
