# AI-assisted Alt Text

The skill emits `<img>` tags with meaningful `alt`. When the author has not supplied one, the skill drafts alt text with a **local vision model running on Ollama**. Local-only — nothing leaves the machine.

- Model (default): `gemma4:e2b`
- Apple Silicon variant: `gemma4:e2b-mlx` (MLX-optimized; selected automatically)
- Override anytime with `OLLAMA_MODEL=<tag>` (e.g. `gemma3n:e2b` if the above tag is not yet in the Ollama registry).

## Install

```bash
bash front/scripts/install-alt-ai.sh
```

The installer:

1. Installs Ollama if missing (`brew install ollama` on macOS, official script on Linux).
2. Starts the Ollama daemon if not already running.
3. Pulls the right model tag — `-mlx` suffix on Apple Silicon, plain otherwise.
4. Suggests `gemma3n:e2b` as a fallback if the primary tag is not yet published.

No Python dependencies required — `front/scripts/alt_from_ollama.py` uses only the standard library. The optional extras in `front/scripts/requirements.txt` (Pillow for pre-resize) are commented out.

## Use

```bash
# from a path
python3 front/scripts/alt_from_ollama.py ./public/hero.jpg

# from a URL
python3 front/scripts/alt_from_ollama.py https://example.com/photo.jpg

# with a context hint (helps the model disambiguate)
python3 front/scripts/alt_from_ollama.py ./team.jpg "Photo on a careers page"
```

Output: one line of alt text on stdout, ≤ 125 characters. The literal token `EMPTY` (no quotes) means the model judged the image **purely decorative**; the caller emits:

```html
<img src="…" alt="" role="presentation" aria-hidden="true">
```

## Use from the skill (vanilla JS, server-side proxy)

Calling Ollama from the browser is blocked by CORS in most setups. Run a tiny proxy that re-uses the Python script:

```bash
# minimal proxy — adapt to your runtime
python3 -m http.server 8000     # serves static files
# alt-text endpoint: invoke alt_from_ollama.py from your server framework
```

A FastAPI sketch:

```python
# pip install fastapi uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "front/scripts"))
from alt_from_ollama import describe

app = FastAPI()

class Req(BaseModel):
    src: str
    context: str = ""

@app.post("/alt")
def alt(req: Req) -> dict:
    text = describe(req.src, req.context)
    return {"alt": "" if text == "EMPTY" else text, "decorative": text == "EMPTY"}
```

Browser call:

```js
async function altFor(src, context = '') {
  const r = await fetch('/alt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ src, context }),
  });
  return r.json();   // { alt: "…", decorative: false }
}
```

## Rules the prompt enforces

1. ≤ 125 characters — short alt is kinder to screen readers.
2. **Describe meaning, not pixels.** "Person walking a dog at sunset" beats "An image of a person, a dog, and orange sky".
3. **No "image of …", "picture of …", "photo of …"** prefixes — screen readers already announce "image".
4. **Don't guess race, gender, age, mood** unless contextually essential.
5. **Decorative recognition.** If the image is texture / ornament / divider, model returns `EMPTY`.
6. **Text-in-image** is preserved verbatim.

The hard 125-char cap is enforced again in Python after generation, in case the model overshoots.

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
| `Could not reach Ollama at http://localhost:11434` | Daemon not running | `ollama serve` in another terminal, or re-run `install-alt-ai.sh`. |
| `Error: model not found` | Tag absent from registry | Re-run with `OLLAMA_MODEL=gemma3n:e2b` (or `gemma3n:e2b-mlx`). |
| Garbled or hallucinated text | Image very small or low quality | Pre-resize to ≥ 512 px on the long edge. |
| Very slow first call | First inference loads weights | Subsequent calls are fast; keep the daemon running between calls. |

## Checklist

- [ ] `install-alt-ai.sh` ran successfully and the model is in `ollama list`.
- [ ] `alt_from_ollama.py` returns a non-empty string on a known photo.
- [ ] Server proxy in place if calling from the browser.
- [ ] Every AI-drafted `alt` carries `data-alt-source="ai"` until a human reviews it.
- [ ] Decorative responses (`EMPTY`) translate to `alt="" role="presentation" aria-hidden="true"`.
