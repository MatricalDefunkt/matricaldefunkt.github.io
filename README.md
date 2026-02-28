# Portfolio

A fast, minimal, single-page tech portfolio site built with [Astro](https://astro.build). No JS framework; just Astro components and vanilla TypeScript. Deploys to GitHub Pages as a fully static site.

**Live:** [matricaldefunkt.me](https://matricaldefunkt.me)

## Features

- Sticky hero panel with scroll-reveal content sections
- Collapsible work experience cards with animated chevron (CSS grid trick, no JS height calculation)
- Expandable architecture diagrams with zoom/pan/pinch gesture support
- Zero render-blocking CSS (all styles inlined at build time)
- Dark-only, design-token driven theme via CSS custom properties

## Sections

| Section       | File                                  |
| ------------- | ------------------------------------- |
| Hero          | `src/pages/_index/Hero.astro`         |
| Skills        | `src/pages/_index/Skills.astro`       |
| Featured Work | `src/pages/_index/FeaturedWork.astro` |
| Experience    | `src/pages/_index/Experience.astro`   |
| Leadership    | `src/pages/_index/Leadership.astro`   |
| Awards        | `src/pages/_index/Awards.astro`       |
| Education     | `src/pages/_index/Education.astro`    |

## Use This as Your Own Portfolio

All content is plain TypeScript data arrays in each section file.

### 1. Fork & clone

```sh
git clone https://github.com/matricaldefunkt/matricaldefunkt.github.io my-portfolio
cd my-portfolio
bun install
```

### 2. Update your details

Each section file in `src/pages/_index/` contains a typed `const` array at the top. Edit those arrays with your own content, the types enforce the shape.

Key files to update:

- **[`Hero.astro`](src/pages/_index/Hero.astro)**: name, title, tagline, social links
- **[`Experience.astro`](src/pages/_index/Experience.astro)**: jobs (role, company, date, summary, project bullets)
- **[`Skills.astro`](src/pages/_index/Skills.astro)**: skill categories and items
- **[`FeaturedWork.astro`](src/pages/_index/FeaturedWork.astro)**: projects (title, challenge, solution, stats, tech, links, optional images)
- **[`Education.astro`](src/pages/_index/Education.astro)**: degrees
- **[`Awards.astro`](src/pages/_index/Awards.astro)**: recognitions
- **[`Leadership.astro`](src/pages/_index/Leadership.astro)**: leadership/volunteer roles (hidden until populated)
- **[`src/layouts/Layout.astro`](src/layouts/Layout.astro)**: SEO meta title, description, OG image URL

### 3. Update the site URL

Edit `astro.config.mjs`:

```js
export default defineConfig({
  site: "https://your-username.github.io", // or your custom domain
});
```

If using a custom domain, update `CNAME` with your domain name.

### 4. Run locally

```sh
bun dev      # http://localhost:4321
bun build    # production build -> ./dist/
bun preview  # preview the production build
```

### 5. Deploy

The repo is set up for **GitHub Pages**. Push to `main` if you have the GitHub Pages action configured, it deploys automatically. Otherwise go to **Settings -> Pages** and point it at the `gh-pages` branch or `./dist`.

## Project Structure

```
src/
├── components/ui/    # Shared primitives (Badge, Card, ChevronToggle, etc.)
├── layouts/          # HTML shell, SEO, global font load
├── pages/
│   ├── index.astro   # Composes all sections — the only page
│   └── _index/       # One .astro file per section
└── styles/
    └── global.css    # Design tokens (CSS vars), typography, .container
public/               # Static assets (images, favicon)
```

## Tech Stack

- [Astro](https://astro.build) static site generator
- Vanilla TypeScript
- Pure CSS with custom properties
- Deployed on GitHub Pages
