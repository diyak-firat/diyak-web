// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  // TODO: Bilgi İşlem'den alınan alan adıyla değiştir (ör. https://diyak.firat.edu.tr)
  site: 'https://diyak.example.org',
  output: 'static',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
  },
});
