# Copilot Instructions

## Project Overview

Single-page Astro portfolio site for Pramit Sharma. No JS framework (no React/Vue) — all interactivity is vanilla TypeScript in `<script>` blocks. Deployed to GitHub Pages. Package manager is **bun**.

## Commands

```sh
bun dev       # dev server at localhost:4321
bun build     # production build to ./dist/
bun preview   # preview production build
```

## Architecture

- **`src/pages/index.astro`** — composes all sections; the only real "page"
- **`src/pages/_index/*.astro`** — one file per section (Experience, FeaturedWork, Education, etc.); each is a self-contained `<section>` with its own scoped `<style>` and optional `<script>`
- **`src/components/ui/`** — shared primitives: `Badge`, `Card`, `ChevronToggle`, `IconButton`, `ListItem`, `Link`, `Stat`, `Spinner`
- **`src/layouts/Layout.astro`** — HTML shell, SEO meta, global font load, page-load spinner
- **`src/styles/global.css`** — CSS custom properties (design tokens), typography, `.container` layout. No utility framework.

## Design Tokens (global.css)

All colour/spacing decisions go through CSS variables:
`--bg-color`, `--content-bg-color`, `--text-color`, `--accent-color`, `--secondary-text`, `--card-bg`, `--card-border`.
Dark-only; `color-scheme: dark` is set globally.

## Key Component Variants

- **`Card`**: `variant="default"` (elevated, hover lift) | `variant="minimal"` (flush, used for project bullets in Experience/Leadership)
- **`Badge`**: `variant="solid"` (pill, default) | `variant="outline"` (square, deprecated — prefer solid)
- **`ChevronToggle`**: standalone button; add `.active` class to rotate 180°

## Collapsible Pattern

Used in Experience and Leadership sections. Animate with CSS grid trick — no JS height calculation needed:

```css
.details {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease-out;
}
.details.expanded {
  grid-template-rows: 1fr;
}
.details-inner {
  overflow: hidden;
  min-height: 0;
}
```

Make the entire trigger row clickable (not just the chevron button). Listener goes on the row; the chevron click bubbles up naturally.

## Adding a New Section

1. Create `src/pages/_index/MySecttion.astro` — wrap content in `<section>`, use `<h2>` for the title
2. If the section can be empty, guard with `{data.length > 0 && (<section>...</section>)}`
3. Import and place it in `src/pages/index.astro`
4. Data lives as a typed `const` array in the frontmatter of the section file — no external data fetching

## Prettier Quirk

Prettier mangles mixed JSX/HTML inline expressions. Suppress with a comment on the preceding line inside a JS expression block:

```astro
{ // prettier-ignore
  <><span>text (</span><span class="tooltip">abbr</span><span>)</span></>
}
```

## CSS Scope

All `<style>` blocks in `.astro` files are **scoped by default**. Global styles (typography, tokens, layout) live only in `global.css`. Do not add component-specific rules there.
