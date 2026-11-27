# Kurum logoları

Fırat Üniversitesi ve SKS logoları, kullanım izniyle buraya eklenir (`firat.svg`, `sks.svg`).
Ardından `src/config/site.ts` içindeki `kurumlar` listesinde ilgili `logo` alanına yolu yazılır:

```ts
{ kisa: 'FÜ', ad: 'Fırat Üniversitesi', url: 'https://www.firat.edu.tr', logo: '/logolar/firat.svg' },
```

Tüzük 9/7 gereği bu logolar (veya kurum adları) sitede bulunmalıdır.
