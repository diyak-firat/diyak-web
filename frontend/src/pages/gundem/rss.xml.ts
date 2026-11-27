// Gündem RSS beslemesi: /gundem/rss.xml
// Mutlak bağlantılar astro.config.mjs içindeki `site` değerinden üretilir.
import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { site } from '../../config/site';
import { gonderiler } from '../../lib/gundem';

export async function GET(context: APIContext) {
  const hepsi = await gonderiler();
  return rss({
    title: `${site.kisaAd} · Gündem`,
    description: `${site.resmiAd}: duyurular, etkinlikler, çağrılar ve topluluktan haberler.`,
    site: context.site ?? 'http://localhost:4321',
    items: hepsi.map((g) => ({
      title: g.data.baslik,
      description: g.data.ozet,
      pubDate: g.data.tarih,
      link: `/gundem/${g.id}/`,
      categories: [g.data.etiket],
    })),
    customData: '<language>tr</language>',
  });
}
