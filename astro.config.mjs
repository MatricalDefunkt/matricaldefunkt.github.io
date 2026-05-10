// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://matricaldefunkt.me',
  integrations: [mdx(), sitemap()],
  build: {
    inlineStylesheets: 'always',
  },
  markdown: {
    shikiConfig: { theme: 'one-dark-pro' },
  },
});
