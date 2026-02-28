// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://matricaldefunkt.github.io',
  build: {
    // Inline all CSS into <style> tags - eliminates the render-blocking
    // external stylesheet request that Lighthouse flags.
    inlineStylesheets: 'always',
  },
});
