import { getCollection, type CollectionEntry } from 'astro:content';

export type Kaynak = CollectionEntry<'kaynaklar'>;

export { TURLER, type Tur } from './kaynakTurleri';

/** Tüm kaynaklar, `sira` alanına göre. */
export async function kaynaklar(): Promise<Kaynak[]> {
  return (await getCollection('kaynaklar')).sort((a, b) => a.data.sira - b.data.sira);
}
