# Foundations — Images


## When to consult this file

- Inserting product imagery, illustrations, photos, screenshots
- Building a media-heavy surface (hero, gallery, marketing page)

## Core principles

- **Crisp at every density.** Ship at native resolution and let CSS scale down; never let the browser upscale.
- **One purpose per image.** Decorative vs. informative — assistive tech handles them differently.
- **Respect aspect ratio.** Use `aspect-ratio` to reserve space and prevent layout shift.
- **Mind both color schemes.** Pure white backgrounds shock in dark mode; provide a dark variant or a subtle plate.
- **Don't override system content with overlay text** that fails contrast.
- **Honor reduced-data preferences** — defer non-critical imagery on `prefers-reduced-data: reduce`.

## Concrete rules — web

1. **Use `<img>` with `width` and `height`** so the browser reserves space (no CLS).
2. **Decorative images**: `alt=""` and `role="presentation"`.
3. **Informative images**: `alt="…"` describes the content, not the file (`alt="Person walking a dog"` not `alt="dog.png"`).
4. **Responsive sources**: `srcset` + `sizes`, or `<picture>` for art direction / theme switching.
5. **Lazy-load below the fold**: `loading="lazy" decoding="async"`.
6. **Use modern formats** with fallback: AVIF → WebP → JPEG/PNG.
7. **Theme-aware images**: `<picture>` with `media="(prefers-color-scheme: dark)"`.
8. **Aspect ratio**: Tailwind `aspect-video`, `aspect-square`, or `aspect-[4/3]`.

## Patterns

### Responsive theme-aware image

```html
<picture>
  <source srcset="/hero-dark.avif" media="(prefers-color-scheme: dark)" type="image/avif">
  <source srcset="/hero.avif" type="image/avif">
  <source srcset="/hero.webp" type="image/webp">
  <img src="/hero.jpg" alt="Living room with warm sunset light"
       width="1600" height="900" class="aspect-video w-full rounded-2xl object-cover"
       loading="lazy" decoding="async">
</picture>
```

### Decorative image

```html
<img src="/pattern.svg" alt="" role="presentation" aria-hidden="true"
     class="pointer-events-none absolute inset-0 -z-10 h-full w-full object-cover opacity-20">
```

### Avatar with fallback

```html
<span class="grid h-10 w-10 place-items-center overflow-hidden rounded-full bg-surface-secondary text-sm font-medium text-label-secondary">
  <img src="/u/123.jpg" alt="" class="h-full w-full object-cover" onerror="this.replaceWith(this.nextElementSibling)">
  <span aria-hidden="true">WH</span>
</span>
```

## AI-drafted alt text

When the author has not supplied `alt`, the skill drafts it with a **local vision model running on Ollama** (default `gemma4:e2b`; `gemma4:e2b-mlx` on MLX-capable hardware). Local-only — nothing leaves the machine. Runtime is Node.js 18+, no `npm install`.

Install once:

| Shell | Command |
|---|---|
| Bash (Homebrew or curl installer) | `bash front/scripts/install-alt-ai.sh` |
| PowerShell (winget installer) | `powershell -ExecutionPolicy Bypass -File front\scripts\install-alt-ai.ps1` |

Generate alt for an image:

```bash
node front/scripts/alt-from-ollama.mjs ./public/hero.jpg
```

Output is one line ≤ 125 characters, or the literal token `EMPTY` for a purely decorative image (in which case emit `alt="" role="presentation" aria-hidden="true"`).

Full guidance — prompt rules, Node server-proxy pattern for browser calls, review workflow, failure modes — in `references/alt-text-ai.md`.

## Checklist

- [ ] Every `<img>` has explicit `width` and `height`.
- [ ] `alt` reflects meaning, or empty for decoration.
- [ ] Modern format with fallback.
- [ ] Lazy-loaded below the fold.
- [ ] Dark-mode variant where needed.
- [ ] No layout shift on load.
- [ ] AI-drafted `alt` tagged with `data-alt-source="ai"` until a human reviews.
