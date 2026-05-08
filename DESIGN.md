# Design System

Single-page dark-mode portfolio. No CSS framework — pure CSS with Astro's built-in scoped `<style>` blocks for component isolation.

---

## CSS Architecture

```
src/styles/
├── tokens.css      Design tokens (CSS custom properties) — edit here first
├── base.css        html / body / main resets
├── typography.css  Heading, paragraph, and anchor base styles
├── components.css  Shared structural patterns (.container, .grid, .card, .tag, .list-*)
├── utilities.css   Single-purpose helper classes (.text-secondary, .text-accent)
└── global.css      Entry point — @imports all of the above (imported once in Layout.astro)
```

Component-specific styles live in each file's `<style>` block. Astro automatically scopes them, so there are no naming collisions with global classes.

**Rule of thumb:**
- Touching a color or spacing value? → `tokens.css`
- Touching a base HTML element? → `base.css` or `typography.css`
- Adding a reusable structural pattern used in 2+ places? → `components.css`
- Adding a one-off helper class? → `utilities.css`
- Styling a single component? → that component's `<style>` block

---

## Design Tokens

All in `src/styles/tokens.css`.

### Colors

| Token | Value | Usage |
|---|---|---|
| `--bg-color` | `oklch(17% 0 0)` | Hero / page background |
| `--content-bg-color` | `oklch(20% 0 0)` | Scrolling content area |
| `--footer-bg` | `#111110` | Footer background |
| `--card-bg` | `#1b1a18` | Cards, inputs, buttons |
| `--text-color` | `#e6e4e0` | Primary text and headings |
| `--text-hover` | `#d0cdc6` | Hovered link / button text |
| `--accent-color` | `#a8a49c` | Links, focus rings, hover borders |
| `--secondary-text` | `oklch(70% 0.00777 67.486)` | Body copy, metadata, muted labels |
| `--tag-text` | `#b5b2ac` | Tag / badge text |
| `--card-border` | `#2c2b27` | Default border color |
| `--tooltip-bg` | `#3a3935` | Tooltip / popover background |
| `--tooltip-border` | `#52504b` | Tooltip / popover border |

The palette is intentionally monotone: warm dark grays with a single muted-gold accent. There is no light mode.

---

## Typography

Font: **Ubuntu** (Google Fonts, loaded non-blocking in `Layout.astro`).
Weights in use: 300 (light body), 400 (regular), 500, 600, 700, 800 (hero heading).
Fallback stack: `system-ui, -apple-system, sans-serif`.

| Element | Size | Weight | Notes |
|---|---|---|---|
| `h1` | `3rem` → `2.5rem` | 800 | Gradient fill `#e8e6e0 → #a8a49c`, tight letter-spacing |
| `h2` | `1.5rem` | default | Bottom border (`--card-border`) decoration, `3rem` top margin |
| `h3` | `1.2rem` | default | `--text-color` |
| `p` | inherited | default | `--secondary-text` |
| `a` | inherited | default | `--accent-color`, underline on hover |
| `.intro` (Hero) | `1.75rem` → `1.35rem` | 300 | Scoped to `Hero.astro` |

---

## Spacing

No token-based scale — values are authored directly in `rem`. The informal scale in use:

| Size | Value | Typical use |
|---|---|---|
| Tight | `0.25rem – 0.5rem` | Icon gaps, badge padding |
| Standard | `0.75rem – 1rem` | Inner padding, label gaps |
| Section | `1.5rem` | Card padding, list item margins |
| Section gap | `2rem – 3rem` | Between major headings and content |
| Page padding | `4rem` | Content wrapper top/bottom |

---

## Border Radius

| Value | Usage |
|---|---|
| `4px` | Tags, tooltips, small badges |
| `6px` | Minimal (job project) card |
| `8px` | Buttons, inputs, default card (Card.astro) |
| `0.75rem` | Global `.card` utility, featured work cards |
| `16px` | Pill badges (Badge solid variant) |
| `50%` | Avatar / profile photo |

---

## Transitions

| Duration | Easing | Usage |
|---|---|---|
| `0.2s` | `ease` | Color, border, transform hover effects |
| `0.3s` | `ease` | Slightly heavier state changes |
| `0.4s` | `ease` | Sidebar / overlay show/hide |
| `0.6s` | `cubic-bezier(0.4, 0, 0.2, 1)` | Page-level entrance animations (footer social links, floating links) |

---

## Breakpoints

One breakpoint: `@media (max-width: 1000px)` for mobile layout.

Changes at that breakpoint: `h1` shrinks, `.list-header` stacks vertically, `.container` widens to `90%`, floating links hide desktop sidebar and show inline row, footer stacks.

---

## Shared Component Patterns (`components.css`)

### `.container`

Max-width content wrapper (`900px`, centered). Narrows to `90%` on mobile.

### `.grid`

Auto-fill grid: `repeat(auto-fit, minmax(300px, 1fr))` with `1.5rem` gap.

### `.card`

Dark surface tile. `--card-bg` background, `1px solid --card-border` border, `0.75rem` radius, `1.5rem` padding. Hover: lift (`translateY(-2px)`) + accent border.

Paired helpers: `.card-body` (flex-grows to fill height) and `.card-footer` (wraps tags at bottom).

### `.tag`

Inline pill. Semi-transparent dark background, `4px` radius, `--tag-text` color. Used for tech stack labels.

### `.list-item` family

Structured entry pattern for Experience, Education, Awards. Items are separated by `--card-border` bottom borders. `.list-header` holds `.list-title` / `.list-date` side-by-side (stacks on mobile). Supplemental classes: `.list-subtitle`, `.list-desc`, `.list-summary`.

---

## UI Components (`src/components/ui/`)

| Component | Props / Variants | Notes |
|---|---|---|
| `Badge` | `variant: "solid" \| "outline"` | Solid = pill tag; outline = rectangular type label |
| `Card` | `variant: "default" \| "minimal"` | Default = featured work tile; minimal = job project card |
| `ChevronToggle` | — | Animated chevron for collapsible sections |
| `FloatingLinks` | `mobile: boolean` | Desktop: fixed left sidebar; mobile: inline centered row |
| `IconButton` | `variant: "default" \| "modal-close"` | Icon-only buttons |
| `Link` | `variant: "project" \| "social"` | Optional arrow decoration |
| `ListItem` | — | Thin wrapper that applies `.list-item` pattern |
| `Spinner` | `size: string` | SVG spinner sized via inline style |
| `Stat` | — | Value + label pair used in FeaturedWork modal |

---

## Page Sections (`src/pages/_index/`)

| Section | Key styles | Interactive |
|---|---|---|
| `Hero` | Centered layout, `64px` circular profile photo | CTA button scrolls to footer contact form |
| `FeaturedWork` | Project grid, full-screen image modal with zoom / pan / touch | Modal, keyboard nav (Escape), touch gestures |
| `Skills` | Tech grid, SVG icons via CSS `mask-image` | — |
| `Experience` | Collapsible job details | `ChevronToggle` expand/collapse |
| `Leadership` | Same pattern as Experience | `ChevronToggle` expand/collapse |
| `Awards` | `.list-item` list | — |
| `Education` | `.list-item` list | — |
| `TechnicalWriting` | Currently disabled (commented out) | — |

---

## Adding to the System

1. **New color or surface** → add a token to `tokens.css`; consume it via `var(--token-name)` everywhere
2. **New structural pattern** used in 2+ places → add to `components.css`
3. **New page section** → `src/pages/_index/MySectionName.astro` with a scoped `<style>` block
4. **New reusable UI element** → `src/components/ui/MyComponent.astro` with a scoped `<style>` block
5. **Do not hardcode** color hex values or rgba in component `<style>` blocks — always use a token
