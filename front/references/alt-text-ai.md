# AI-assisted Alt Text

The skill emits `<img>` tags with meaningful `alt`. When the author has not supplied one, the skill drafts alt text with a **local vision model running on Ollama** — nothing leaves the machine.

- **Model (default):** `gemma4:e2b`
- **MLX-capable hardware variant:** `gemma4:e2b-mlx` (selected automatically by the installers and the script)
- **Override anywhere:** `OLLAMA_MODEL=<tag>` (for example `gemma3n:e2b` to use a different on-device vision model).

Runtime: **Node.js 18+** (built-in `fetch`, no `npm install` required).

## Install Ollama + pull the model

### Bash systems (Homebrew or curl installer)

```bash
bash front/scripts/install-alt-ai.sh
```

The script detects Homebrew (`brew install ollama`) when present, and falls back to the official Linux installer (`curl -fsSL https://ollama.com/install.sh | sh`) elsewhere. If neither is available, download Ollama manually from <https://ollama.com/download>. On MLX-capable hardware the script automatically pulls the `-mlx` variant.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File front\scripts\install-alt-ai.ps1
```

The script uses `winget install Ollama.Ollama`. If `winget` is missing, install "App Installer" from the Microsoft Store, or download Ollama manually from <https://ollama.com/download>.

Each installer also: starts the daemon if it isn't running, then `ollama pull`s the right tag (with `-mlx` on MLX-capable hardware).

## Generate alt text

Same command on every platform:

```bash
node front/scripts/alt-from-ollama.mjs ./public/hero.jpg
node front/scripts/alt-from-ollama.mjs ./public/hero.jpg "Photo on a careers page"
node front/scripts/alt-from-ollama.mjs https://example.com/photo.jpg
```

Output: one line of alt text on stdout, ≤ 125 characters. The literal token `EMPTY` (no quotes) means the model judged the image **purely decorative**; the caller emits:

```html
<img src="…" alt="" role="presentation" aria-hidden="true">
```

## Use from the skill (vanilla JS, server-side proxy)

Calling Ollama from the browser is blocked by CORS in most setups. Run a small Node proxy that re-uses the script's `describe()` export:

```js
// server.mjs — Node 18+, no deps
import http from 'node:http';
import { describe } from './front/scripts/alt-from-ollama.mjs';

http.createServer(async (req, res) => {
  if (req.method !== 'POST' || req.url !== '/alt') {
    res.writeHead(404).end(); return;
  }
  let body = '';
  req.on('data', (c) => body += c);
  req.on('end', async () => {
    try {
      const { src, context = '' } = JSON.parse(body);
      const text = await describe(src, context);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ alt: text === 'EMPTY' ? '' : text, decorative: text === 'EMPTY' }));
    } catch (err) {
      res.writeHead(500).end(err.message);
    }
  });
}).listen(8787, () => console.log('alt-proxy on http://localhost:8787'));
```

Browser side:

```js
async function altFor(src, context = '') {
  const r = await fetch('http://localhost:8787/alt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ src, context }),
  });
  return r.json();   // { alt: "…", decorative: false }
}
```

## Rules the prompt enforces

1. ≤ 125 characters — long alt is fatiguing to listen to.
2. **Describe meaning, not pixels.** "Person walking a dog at sunset" beats "An image of a person, a dog, and orange sky".
3. **No "image of …", "picture of …", "photo of …"** prefixes — screen readers already announce "image".
4. **Don't guess race, gender, age, mood** unless contextually essential.
5. **Decorative recognition.** Texture / ornament / divider → model returns `EMPTY`.
6. **Text-in-image** is preserved verbatim.

The 125-character cap is enforced again in JS after generation, in case the model overshoots.

## Review workflow

AI-generated alt is a **draft**, not a final answer. Tag every AI-drafted attribute so the review tool can flag it:

```html
<img src="…" alt="Person walking a dog at sunset" data-alt-source="ai">
```

Strip `data-alt-source="ai"` once a human has reviewed and approved.

## Charts and diagrams

For data visualizations, the AI alt should describe the **takeaway**, not every label:

> "Active users rose from 1.2k to 1.9k over 7 weeks."

Pair complex charts with a longer text alternative in `<figcaption>` or `aria-describedby`.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `Could not reach Ollama at http://localhost:11434` | Daemon not running | `ollama serve` in another terminal, or re-run the installer. |
| `Error: model not found` | Tag mistyped or installer skipped | Re-run the installer, or pull manually: `ollama pull gemma4:e2b` (MLX-capable hardware: `gemma4:e2b-mlx`). |
| Garbled or hallucinated text | Image very small or low quality | Pre-resize to ≥ 512 px on the long edge. |
| Very slow first call | First inference loads weights into memory | Subsequent calls are fast; keep the daemon running between calls. |

## Checklist

- [ ] Installer ran successfully and the chosen model is listed in `ollama list`.
- [ ] `node front/scripts/alt-from-ollama.mjs <test image>` returns a non-empty string.
- [ ] Browser callers go through the Node proxy (CORS).
- [ ] Every AI-drafted `alt` carries `data-alt-source="ai"` until a human reviews it.
- [ ] Decorative responses (`EMPTY`) translate to `alt="" role="presentation" aria-hidden="true"`.
