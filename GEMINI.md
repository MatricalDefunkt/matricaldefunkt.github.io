# Project Guide

Personal portfolio site for Pramit Sharma. Single-page, dark-mode, fully static. Live at [matricaldefunkt.me](https://matricaldefunkt.me).

## Stack

- **[Astro](https://astro.build) 6.x** — static site generator, no JS framework
- **Vanilla TypeScript** — interactivity only (collapsibles, modal, scroll events)
- **Pure CSS** — design tokens via CSS custom properties, Astro scoped `<style>` blocks
- **Bun** — package manager and script runner
- **GitHub Pages** — deploy target; CI via `.github/workflows/`

## Commands

```sh
bun dev       # dev server at http://localhost:4321
bun build     # production build → ./dist/
bun preview   # serve ./dist/ locally
```

## Project Layout

```
src/
├── components/ui/    # Reusable primitives (Badge, Card, ChevronToggle, FloatingLinks, …)
├── layouts/
│   └── Layout.astro  # HTML shell: SEO meta, font load, page-loader spinner, footer
├── pages/
│   ├── index.astro   # Composes all sections — the only route
│   └── _index/       # One .astro file per section (Hero, FeaturedWork, Experience, …)
└── styles/
    ├── global.css    # Entry point — @imports the modules below
    ├── tokens.css    # All CSS custom properties (edit here first)
    ├── base.css      # html / body / main resets
    ├── typography.css
    ├── components.css # .container .grid .card .tag .list-*
    └── utilities.css  # .text-secondary .text-accent
public/               # Static assets: images, favicon
DESIGN.md             # Full design-system reference (tokens, typography, spacing, components)
```

## Content

All content lives as typed TypeScript arrays near the top of each section file in `src/pages/_index/`. No CMS, no external data fetching. To update a section, edit the array in that file.

Key content files:

| Section | File |
|---|---|
| Hero bio | `src/pages/_index/Hero.astro` |
| Work experience | `src/pages/_index/Experience.astro` |
| Featured projects | `src/pages/_index/FeaturedWork.astro` |
| Skills / tech stack | `src/pages/_index/Skills.astro` |
| Leadership | `src/pages/_index/Leadership.astro` |
| Awards | `src/pages/_index/Awards.astro` |
| Education | `src/pages/_index/Education.astro` |
| SEO / OG meta | `src/layouts/Layout.astro` (frontmatter props) |

## Styling Rules

- **Always use a token** (`var(--token)`) for colors. Never hardcode hex or rgba values in component styles.
- Token definitions are in `src/styles/tokens.css`. See `DESIGN.md` for the full token table.
- Component styles go in the component's own `<style>` block — Astro scopes them automatically.
- Shared patterns used in 2+ places belong in `src/styles/components.css`.
- Single breakpoint: `@media (max-width: 1000px)`.

## Key Behaviours

- **CSS is fully inlined at build time** (`inlineStylesheets: 'always'` in `astro.config.mjs`). There is no external stylesheet request; all styles ship inside `<style>` tags in the HTML.
- **Font loading is non-blocking.** Ubuntu is loaded via a `preload` → `onload` swap in `Layout.astro`. The page-loader spinner (`#page-loader`) hides once `document.fonts.ready` resolves.
- **Hero is sticky.** `.hero-wrapper` uses `position: sticky; height: 100vh`. The content section slides over it on scroll.
- **Collapsibles use a CSS grid trick** — height animates via `grid-template-rows: 0fr / 1fr`, no JS height calculation needed.
- **FeaturedWork image modal** has full zoom/pan (mouse + touch) implemented in inline TypeScript inside the component.

## Deploy

Push to `main`. The GitHub Actions workflow builds with Astro and publishes to GitHub Pages. Custom domain is set via the `CNAME` file (`matricaldefunkt.me`).
