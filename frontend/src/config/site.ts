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
  // Üst menüde gösterilen kurum logoları. logo: null ise kesikli yer tutucu çıkar.
  // SKS'nin ayrı bir logosu yok; adı alt bilgide yazar (Tüzük 9/7 "adı ve/veya logosu", K-22).
  kurumlar: [
    {
      kisa: 'FÜ',
      ad: 'Fırat Üniversitesi',
      url: 'https://www.firat.edu.tr',
      logo: '/logolar/firat.svg',
    },
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
  { ad: 'Kaynaklar', href: '/#kaynaklar', sayfa: 'kaynaklar' },
  { ad: 'Hakkımızda', href: '/#hakkimizda', sayfa: null },
  { ad: 'Ekip', href: '/ekip/', sayfa: 'ekip' },
] as const;

export type Sayfa = 'ana' | 'gundem' | 'kaynaklar' | 'ekip' | 'diger';
