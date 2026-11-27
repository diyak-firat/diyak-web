// Sitenin genel ayarları. İletişim ve bağlantılar buradan değiştirilir.
// '#' ile işaretli bağlantılar henüz doldurulmamış yer tutuculardır (bkz. STATUS.md).

export const site = {
  kisaAd: 'DİYAK',
  tamAd: 'Doğal Dil İşleme ve Yapay Zekâ Araştırmaları Topluluğu',
  resmiAd: 'Fırat Üniversitesi Doğal Dil İşleme ve Yapay Zekâ Araştırmaları Öğrenci Topluluğu',
  universite: 'Fırat Üniversitesi',
  bagliBirim: 'Sağlık Kültür ve Spor Daire Başkanlığı · Öğrenci Toplulukları Birimi',
  aciklama:
    'Fırat Üniversitesi Doğal Dil İşleme ve Yapay Zekâ Araştırmaları Topluluğu. Türkçe için açık veri kümeleri, modeller ve araçlar üretiyoruz.',
  eposta: '[topluluk@firat.edu.tr]',
  belgeler: {
    uyeKayitFormu: '/belgeler/uye-kayit-formu.pdf',
    tuzuk: '/belgeler/tuzuk.pdf',
  },
  kurumlar: [
    // logo: '/logolar/firat.svg' gibi bir yol verilince yer tutucunun yerine görsel çıkar
    { kisa: 'FÜ', ad: 'Fırat Üniversitesi', url: 'https://www.firat.edu.tr', logo: null },
    { kisa: 'SKS', ad: 'Sağlık Kültür ve Spor Daire Başkanlığı', url: '#', logo: null },
  ] as { kisa: string; ad: string; url: string; logo: string | null }[],
  sosyal: [
    { ad: 'LinkedIn', url: '#' },
    { ad: 'Instagram', url: '#' },
    { ad: 'GitHub', url: '#' },
    { ad: 'Hugging Face', url: '#' },
    { ad: 'Kaggle', url: '#' },
  ],
};

/** Üst menü. '/#...' bağlantıları ana sayfadaki bölümlere gider. */
export const menu = [
  { ad: 'Gündem', href: '/#gundem', sayfa: 'gundem' },
  { ad: 'Araştırma', href: '/#arastirma', sayfa: null },
  { ad: 'Kaynaklar', href: '/#kaynaklar', sayfa: null },
  { ad: 'Hakkımızda', href: '/#hakkimizda', sayfa: null },
  { ad: 'Ekip', href: '/ekip/', sayfa: 'ekip' },
] as const;

export type Sayfa = 'ana' | 'gundem' | 'ekip' | 'diger';
