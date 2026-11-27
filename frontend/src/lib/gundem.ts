import { getCollection, type CollectionEntry } from 'astro:content';

export { ETIKETLER, type Etiket } from './etiketler';

export type Gonderi = CollectionEntry<'gundem'>;

/** Yayımlanmış gönderiler, en yeni önce. Taslaklar yalnızca geliştirme sunucusunda görünür. */
export async function gonderiler(): Promise<Gonderi[]> {
  const hepsi = await getCollection('gundem', ({ data }) => import.meta.env.DEV || !data.taslak);
  return hepsi.sort((a, b) => b.data.tarih.getTime() - a.data.tarih.getTime());
}
