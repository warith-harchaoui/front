[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

# front

A Claude **skill** that constrains Claude to a single frontend stack: vanilla JavaScript, Tailwind CSS, Montserrat. Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Contents

- `front/SKILL.md` — entry point with YAML frontmatter and instructions.
- `front/references/` — progressive-disclosure reference files (color, stack, checklist, UI guidelines).
- `front/assets/` — copy-paste templates and Montserrat font files.

## What the skill enforces

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex in markup.
- Output uses Montserrat as the sole UI typeface, self-hosted from `assets/fonts/montserrat/`.
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion`, and meets a 44×44 px hit area.
- Color choices map to the four palettes in `references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).

## CLI → GUI

The skill includes a workflow that takes an existing command-line tool and produces a single-page vanilla-JS + Tailwind GUI for it. The workflow reads the CLI's argument parser, categorizes each command (one-shot / form / streaming / list), maps flags to form controls, and wires execution to the project's host (Tauri, Electron, FastAPI, Express, or a browser stub). See `front/SKILL.md` → "CLI → GUI workflow".

## Install

Clone the repo, then choose the runtime you use.

```bash
git clone https://github.com/<user>/front.git
cd front
```

### Option A — Claude Code (CLI)

```bash
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front
ls ~/.claude/skills/front/SKILL.md   # sanity check
```

Claude Code reads the skill's frontmatter description and applies the skill when a user message matches its trigger phrases.

### Option B — Claude.ai (web)

1. Zip the skill folder:
   ```bash
   (cd front && zip -r ../front.zip .)
   ```
2. In Claude.ai → **Settings → Capabilities → Skills → Upload skill**, upload `front.zip`.

### Option C — OpenCode

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Invoke with `/skill front <request>`.

### Option D — LangChain / Anthropic SDK (Python)

Load `front/SKILL.md` as a system-prompt fragment. Append referenced files on demand.

```python
# pip install anthropic
from pathlib import Path
from anthropic import Anthropic

SKILL_DIR = Path("front")
client = Anthropic()

def load_skill() -> str:
    return (SKILL_DIR / "SKILL.md").read_text()

def maybe_load_reference(user_msg: str) -> str:
    refs = []
    m = user_msg.lower()
    if "color" in m:
        refs.append((SKILL_DIR / "references/color-psychology.md").read_text())
    if "button" in m or "modal" in m or "form" in m:
        refs.append((SKILL_DIR / "references/ui-guidelines/INDEX.md").read_text())
    if "chart" in m or "graph" in m:
        refs.append((SKILL_DIR / "references/charts-vega.md").read_text())
    return "\n\n---\n\n".join(refs)

def ask(user_msg: str) -> str:
    system = load_skill() + "\n\n" + maybe_load_reference(user_msg)
    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text

print(ask("Generate a primary button labeled 'Get started'."))
```

For LangChain proper, wrap the same logic in `ChatPromptTemplate` with a `SystemMessage(content=load_skill())` and use `langchain_anthropic.ChatAnthropic`.

### Other runtimes

The Anthropic Skill spec is loaded natively by **Claude Code**, **Claude.ai**, and **OpenCode**. Everywhere else, the skill still works — but as a **custom system prompt**, not a parsed skill. Paste `front/SKILL.md` into the host's system-prompt slot, and load reference files (`front/references/**`) yourself when the task calls for them. Shape verified with Cursor (`.cursor/rules`), Continue (`config.json` custom context), Cline, Aider (`.aider.conf.yml`), and direct Messages API calls.

### Optional — local alt-text helper

The skill can auto-draft `alt` for `<img>` tags via a local Ollama vision model (`gemma4:e2b`, `gemma4:e2b-mlx` on Apple Silicon). Local-only, no data leaves the machine.

| Platform | One-shot install |
|---|---|
| macOS, Ubuntu / Linux | `bash front/scripts/install-alt-ai.sh` |
| Windows | `powershell -ExecutionPolicy Bypass -File front\scripts\install-alt-ai.ps1` |

Then: `node front/scripts/alt-from-ollama.mjs ./path/to/image.jpg`. Full guidance in `front/references/alt-text-ai.md`.

## Repository structure

```
front/                              ← repo root
├── README.md / LISEZMOI.md         ← EN / FR
├── .gitignore
└── front/                          ← skill folder; drop into ~/.claude/skills/
    ├── SKILL.md
    ├── references/
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← color, typography, layout, motion, materials, a11y, …
    │       ├── components/         ← buttons, alerts, sheets, navigation, fields, …
    │       ├── patterns/           ← modality, feedback, loading, settings, …
    │       ├── inputs/             ← keyboard, pointer, touch, focus
    │       └── platforms/          ← mobile, tablet, desktop, wearable, tv, spatial
    └── assets/
        ├── starter-page.html       ← single-file bootstrap (Tailwind Play CDN)
        ├── components/             ← copy-paste HTML snippets
        └── fonts/montserrat/       ← variable + 4 static WOFF2, OFL.txt, fonts.css
```

## Acknowledgements

Special thanks to **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

Montserrat by Julieta Ulanovsky and contributors — <https://github.com/JulietaUla/Montserrat> — SIL Open Font License. The font files are bundled in `front/assets/fonts/montserrat/`.

## License

MIT for the skill source. Montserrat is OFL — see `front/assets/fonts/montserrat/OFL.txt`.
