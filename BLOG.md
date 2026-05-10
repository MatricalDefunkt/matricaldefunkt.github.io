# Blog — Implementation Plan

Dark-mode, MDX-powered blog integrated into the existing Astro portfolio. Posts live alongside the portfolio as static pages. No CMS, no database.

---

## Dependencies

```sh
bun add @astrojs/rss
bun add @astrojs/sitemap
```

`@astrojs/mdx` is bundled with Astro 6 — no separate install needed. Shiki (syntax highlighting) is also built in.

Enable both integrations in `astro.config.mjs`:

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://matricaldefunkt.me',
  integrations: [sitemap()],
  build: { inlineStylesheets: 'always' },
});
```

---

## Directory Structure

```
src/
├── content/
│   ├── config.ts          Content Collections schema
│   └── blog/
│       ├── post-slug.mdx  Each post (filename = URL slug)
│       └── ...
├── pages/
│   ├── blog/
│   │   ├── index.astro    Post list  →  /blog
│   │   └── [slug].astro   Post page  →  /blog/<slug>
│   └── rss.xml.ts         RSS feed   →  /rss.xml
└── components/
    └── blog/
        ├── PostCard.astro      Card on the list page
        ├── PostHeader.astro    Title, date, tags, reading time
        ├── TableOfContents.astro
        ├── SeriesNav.astro     Previous / next in series
        └── Comments.astro      Giscus embed
```

---

## Content Schema (`src/content/config.ts`)

```ts
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title:       z.string(),
    description: z.string(),
    date:        z.coerce.date(),
    tags:        z.array(z.string()).default([]),
    draft:       z.boolean().default(false),
    series:      z.string().optional(),      // e.g. "Kubernetes at Home"
    seriesOrder: z.number().optional(),      // position within series
    ogImage:     z.string().optional(),      // path under /public; falls back to /profile.jpg
  }),
});

export const collections = { blog };
```

---

## Post Frontmatter Reference

```mdx
---
title: "How I Autoscale Gitea Runners on Kubernetes"
description: "A walkthrough of the event-driven autoscaler I built for self-hosted CI."
date: 2026-05-08
tags: [kubernetes, go, ci]
draft: false
series: "Self-Hosted Infra"
seriesOrder: 1
ogImage: /gitea-runner-autoscaling.png   # optional
---

Post content in MDX here. Astro components work inline.
```

Draft posts are excluded from production builds and the RSS feed. They're visible in `bun dev`.

---

## Pages

### `/blog` — Post List (`src/pages/blog/index.astro`)

- Fetch all non-draft posts, sort by date descending
- Render a `PostCard` for each
- Tag filter: client-side toggle (no page reload), same CSS-only expand/collapse pattern used for collapsibles elsewhere
- Search: commented out — add when there are 20+ posts (Pagefind, post-build step)

### `/blog/[slug]` — Post Page (`src/pages/blog/[slug].astro`)

- `getStaticPaths` from Content Collections
- Renders `<PostHeader>` (title, date, reading time, tags) + MDX content + `<TableOfContents>` + `<SeriesNav>` + `<Comments>`
- Reading time: `Math.ceil(post.body.split(/\s+/).length / 200)` minutes
- Layout: two-column on desktop (ToC sidebar right, prose left), single column on mobile

### `/rss.xml` (`src/pages/rss.xml.ts`)

```ts
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return rss({
    title: 'Pramit Sharma — Writing',
    description: 'Infrastructure, backend engineering, and open source.',
    site: context.site,
    items: posts
      .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf())
      .map(post => ({
        title: post.data.title,
        description: post.data.description,
        pubDate: post.data.date,
        link: `/blog/${post.slug}/`,
      })),
  });
}
```

Add RSS autodiscovery to `Layout.astro` `<head>`:

```html
<link rel="alternate" type="application/rss+xml" title="Pramit Sharma — Writing" href="/rss.xml" />
```

---

## SEO

Each post page passes its own props to `Layout.astro`:

```astro
<Layout
  title={`${post.data.title} | Pramit Sharma`}
  description={post.data.description}
  ogImage={post.data.ogImage ?? '/profile.jpg'}
  canonicalUrl={`https://matricaldefunkt.me/blog/${post.slug}/`}
>
```

`Layout.astro` needs a `canonicalUrl` prop wired to `<link rel="canonical">` and the OG `og:url` tag. Currently it hardcodes `siteUrl` — make it optional with the hardcoded value as fallback.

### JSON-LD (per post)

Add inside `[slug].astro`:

```astro
<script type="application/ld+json" set:html={JSON.stringify({
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": post.data.title,
  "description": post.data.description,
  "datePublished": post.data.date.toISOString(),
  "author": { "@type": "Person", "name": "Pramit Sharma" },
  "url": `https://matricaldefunkt.me/blog/${post.slug}/`,
})} />
```

Sitemap is handled automatically by `@astrojs/sitemap` once the integration is registered.

---

## Comments (Giscus)

[Giscus](https://giscus.app) uses GitHub Discussions as the comment store. Setup:

1. Enable Discussions on the GitHub repo
2. Install the [giscus app](https://github.com/apps/giscus) on the repo
3. Get config values from giscus.app (repo ID, category ID)

`Comments.astro`:

```astro
<script
  src="https://giscus.app/client.js"
  data-repo="MatricalDefunkt/matricaldefunkt.github.io"
  data-repo-id="REPO_ID"
  data-category="Blog Comments"
  data-category-id="CATEGORY_ID"
  data-mapping="pathname"
  data-strict="0"
  data-reactions-enabled="1"
  data-emit-metadata="0"
  data-input-position="top"
  data-theme="dark_dimmed"
  data-lang="en"
  crossorigin="anonymous"
  async
></script>
```

Fill in `REPO_ID` and `CATEGORY_ID` from giscus.app after enabling Discussions.

---

## Syntax Highlighting

Shiki is built into Astro — works automatically in MDX code fences. Choose a theme in `astro.config.mjs`:

```js
markdown: {
  shikiConfig: { theme: 'one-dark-pro' },
},
```

Good dark-mode options: `one-dark-pro`, `github-dark`, `dracula`, `tokyo-night`.

---

## Styling

Blog styles follow the existing design system:

- Prose: `--secondary-text`, `1.75rem` line-height (or Astro's `@tailwindcss/typography` equivalent in vanilla CSS)
- Post list uses `.grid` + a new `PostCard` variant of `.card`
- Tags use the existing `.tag` class
- Code blocks get a slightly darker background than `--card-bg` with `--card-border` border
- ToC sidebar: fixed on desktop (similar to `FloatingLinks`), collapsed accordion on mobile
- `h2` inside posts reuse the existing underline style from `typography.css`

No new tokens needed — everything maps to existing ones.

---

## Analytics

Umami is already wired in `Layout.astro` — no action needed. Blog post pages are tracked automatically. To track specific CTA clicks (e.g. the blog button), add `data-umami-event="blog-cta-click"` to the element.

---

## Implementation Order

1. `src/content/config.ts` — define schema
2. Write one real draft post (needed to test rendering end-to-end)
3. `src/pages/blog/index.astro` — list page, no filtering yet
4. `src/pages/blog/[slug].astro` — post page, no ToC or comments yet
5. `Layout.astro` — add `canonicalUrl` prop + RSS `<link>` autodiscovery
6. `src/pages/rss.xml.ts` — RSS feed
7. `astro.config.mjs` — add sitemap integration + Shiki theme
8. `PostHeader.astro`, `PostCard.astro` — styled components
9. `TableOfContents.astro` — desktop sidebar
10. `SeriesNav.astro` — only needed once a series exists
11. `Comments.astro` — Giscus (needs Discussions enabled on repo first)
12. JSON-LD on post pages
13. Tag filtering on list page
