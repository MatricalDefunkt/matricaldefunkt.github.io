# Terminal Overlay — Implementation Plan

A keyboard-activated full-screen terminal that makes the entire portfolio navigable as a POSIX-style filesystem. Not the default experience — discoverable by curious visitors, rewarding to use.

---

## Activation

| Action | Effect |
|---|---|
| Press `` ` `` (backtick) anywhere on page | Open terminal overlay |
| `exit`, `q`, `Ctrl+C`, or `Escape` | Close overlay |
| `Ctrl+L` or `clear` | Clear screen (keep terminal open) |

The backtick is intentional: it is the classic game/devtools console key, muscle memory for developers, invisible to everyone else. A faint hint can optionally appear in the BlogCTA tooltip: `Press \` to go deeper`.

Terminal is **disabled on mobile** — small touchscreen keyboards make it unusable. The overlay simply never mounts on `window.innerWidth < 1000`.

---

## Visual Design

Fake terminal window, centered overlay, `z-index: 9998` (just below the page-loader spinner).

```
┌──────────────────────────────────────────────────────────┐
│  ● ● ●   portfolio.terminal — pramit@matricaldefunkt.me  │  ← title bar
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Welcome to portfolio.terminal                           │
│  pramit@matricaldefunkt.me | Node.js Core Contributor    │
│  Type `help` to see commands, `ls` to start exploring.   │
│                                                          │
│  Last login: Thu May  8 11:14:42 2026                    │
│                                                          │
│  pramit@portfolio:~$ _                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- **Font:** `ui-monospace, 'Cascadia Code', 'Fira Code', monospace`
- **Background:** `#0d0d0c` (slightly darker than `--bg-color`)
- **Text:** `--text-color` for output, `--accent-color` for prompt `$` and directory names, `--secondary-text` for metadata
- **Scrollback:** inner output area is scrollable; new output always scrolls to bottom
- **Cursor:** blinking block `▋` via CSS `animation: blink 1.2s step-end infinite`
- **Dot buttons:** decorative only (red/yellow/green circles); red one closes the terminal
- **Width:** `min(900px, 90vw)`, **height:** `min(600px, 80vh)`, border-radius `12px`
- **Backdrop:** `rgba(0,0,0,0.7)` with `backdrop-filter: blur(4px)` on the overlay

Prompt format changes with current directory:
```
pramit@portfolio:~$           (at root)
pramit@portfolio:~/blog$      (inside blog/)
pramit@portfolio:~/work/mobigic$
```

---

## Filesystem Schema

The portfolio content is mapped to a static virtual filesystem object at build time.

```
/home/pramit/                  (= ~, starting CWD)
├── about.txt                  Hero bio text
├── contact.txt                Email + social links
├── skills.txt                 Skills dump, grouped by category
├── awards.txt                 Awards list
├── education.txt              Education entries
├── blog/                      Blog posts directory
│   ├── <slug>.mdx             One file per post (cat shows full content)
│   └── ...
├── work/                      Experience
│   ├── <company-slug>/
│   │   ├── README.md          Role title, dates, summary
│   │   └── projects/
│   │       ├── <project>.md
│   │       └── ...
│   └── ...
└── projects/                  Featured work
    ├── <project-slug>/
    │   ├── README.md          Description, tech stack, stats
    │   └── links.txt          URLs
    └── ...
```

The data structure in TypeScript:

```ts
type FSFile = { type: 'file'; content: string };
type FSDir  = { type: 'dir';  children: Record<string, FSNode> };
type FSNode = FSFile | FSDir;

const filesystem: FSDir = {
  type: 'dir',
  children: {
    'about.txt':   { type: 'file', content: '...' },
    'blog':        { type: 'dir',  children: { 'post-slug.mdx': { type: 'file', content: '...' } } },
    // ...
  }
};
```

Content is inlined at build time — no runtime fetching. Blog post content is pre-rendered as plain text (strip MDX components, keep prose + code blocks).

---

## Commands Specification

### Navigation

| Command | Behaviour |
|---|---|
| `ls` | List current directory (names only) |
| `ls -l` | Long listing: type, name, size/word-count |
| `ls -la` | Long listing including hidden files (`.gitconfig` easter egg) |
| `cd <path>` | Change directory; supports `..`, `~`, absolute paths |
| `pwd` | Print working directory |

### Content

| Command | Behaviour |
|---|---|
| `cat <file>` | Print file contents; renders markdown headings/bullets as styled text |
| `open <file>` | Navigate the actual page to the section/post corresponding to this file; closes terminal |
| `open <url>` | Opens URL in new tab |

### Meta

| Command | Behaviour |
|---|---|
| `help` | List all commands with one-line descriptions |
| `clear` | Clear output buffer |
| `history` | Print command history for this session |
| `whoami` | `pramit — infrastructure & backend engineer` |
| `uname -a` | Fake but plausible: `portfolio 6.1.0-astro #1 SMP PREEMPT Fri Jan 1 00:00:00 UTC 2027 x86_64` |
| `echo <text>` | Prints text back |
| `exit` / `q` | Close terminal |

### Easter eggs (hidden from `help`)

| Command | Response |
|---|---|
| `sudo rm -rf /` | `Nice try.` |
| `vim` | Opens a fake vim that requires `:q!` to exit |
| `git log` | Shows the actual repo's recent commits |
| `curl matricaldefunkt.me` | Prints raw HTML of the current page with a `--ascii` joke |
| `ls -la` in `~` | Reveals a `.secret` file |
| `cat .secret` | A short personal note |

---

## Keyboard UX

| Key | Action |
|---|---|
| `Enter` | Submit command |
| `↑` / `↓` | Walk command history |
| `Tab` | Autocomplete file/dir name (Phase 2) |
| `Ctrl+C` | Cancel current input / close if input empty |
| `Ctrl+L` | Clear screen |
| `Ctrl+A` / `Ctrl+E` | Jump to start / end of input line |
| `Escape` | Close terminal |

Focus is trapped inside the overlay while open (`Tab` cycles through interactive elements, `Shift+Tab` reverses).

---

## Technical Architecture

```
src/components/terminal/
├── Terminal.astro        Overlay markup + style; mounted in Layout.astro
├── fs.ts                 Static virtual filesystem built from content data
├── commands.ts           Command parser and handlers; returns HTML strings
└── renderer.ts           Formats output: colour classes, directory listings, file content
```

`Terminal.astro` is added to `Layout.astro` once, always in the DOM but `display: none` until activated. The activation listener is a single `keydown` on `document`.

The component is self-contained: it imports `fs.ts` and `commands.ts` and runs entirely client-side (`<script>` block). No framework reactivity needed — DOM manipulation is sufficient.

Output is appended as HTML nodes into a scrollback `<div>`. The prompt line is a `<div>` with a `contenteditable` `<span>` for the input.

---

## Implementation Phases

### Phase 1 — Core shell (MVP)
- Overlay mount + open/close (backtick / Escape)
- Terminal chrome (dot buttons, title bar, prompt)
- MOTD welcome message
- Command input with Enter to submit
- `pwd`, `ls`, `cd`, `cat`, `clear`, `help`, `exit`, `whoami`
- Static filesystem with `about.txt`, `skills.txt`, `contact.txt`

### Phase 2 — Full content
- `blog/`, `work/`, `projects/` directories populated from actual content
- `open <file>` routing to page sections
- Command history (↑ / ↓)
- `git log` easter egg (fetch from GitHub API or hardcode recent commits)

### Phase 3 — Polish
- Tab completion for file/directory names
- Keyboard shortcuts (Ctrl+A/E/L)
- Vim easter egg
- `.secret` easter egg
- Animated MOTD typewriter on first open

### Phase 4 — Blog integration
- Blog posts browsable and readable inside terminal
- `open <slug>` navigates to `/blog/<slug>`
- Post frontmatter shown in `ls -l` (date, reading time)

---

## Accessibility

- `role="dialog"` `aria-modal="true"` `aria-label="Terminal"` on overlay
- `aria-live="polite"` on output area so screen readers announce new lines
- Focus trap while open; focus returns to trigger element on close
- Skip link in `<head>`: "Skip terminal" for screen reader users
- Ensure the activation hint (if shown) has accessible text
