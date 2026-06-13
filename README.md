# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

Author: [Warith HARCHAOUI](https://www.linkedin.com/in/warith-harchaoui/)

A Claude **skill** for a single frontend stack: vanilla JavaScript, Tailwind CSS, Montserrat. Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Special thanks to **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)**, and **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

Montserrat font is bundled in `front/assets/fonts/montserrat/` under the SIL Open Font License — see the bundled `OFL.txt` for the full license and the attached copyright notice.

We also got some knowledge from [Apple  Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and [Google Material Design](https://material.io/design).

## Contents

- `front/SKILL.md` — entry point with YAML frontmatter and instructions.
- `front/references/` — progressive-disclosure reference files (color, stack, checklist, UI guidelines, dataviz, meta tags, i18n, anti-patterns, UX psychology, Material Design, alt text).
- `front/assets/` — copy-paste templates and Montserrat font files.
- `front/scripts/` — Python helpers (`validate.py`, `install_alt_ai.py`, `alt_from_ollama.py`, `meta_from_ollama.py`, `favicons.py`) with `requirements.txt`.
- `llms.txt` — index of the project per <https://llmstxt.org/> for LLM consumers.

## What the skill enforces

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex in markup.
- Output uses Montserrat as the sole UI typeface, self-hosted from `assets/fonts/montserrat/`.
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion`, and meets a 44×44 px hit area.
- Color choices map to the four palettes in `references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).

## CLI → GUI

The skill includes a workflow that takes an existing command-line tool and produces a single-page vanilla-JS + Tailwind GUI for it. The workflow reads the CLI's argument parser, categorizes each command (one-shot / form / streaming / list), maps flags to form controls, and wires execution to the project's host (Tauri, Electron, FastAPI, Express, or a browser stub). See `front/SKILL.md` → "CLI → GUI workflow".

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front
```

Verify:

```bash
ls ~/.claude/skills/front/SKILL.md
```

Claude Code reads the skill's frontmatter description and applies the skill when a user message matches its trigger phrases.

### OpenCode

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Invoke with `/skill front <request>`.

### LangChain / Anthropic SDK (Python)

Load `SKILL.md` as a system-prompt fragment. Append referenced files on demand.

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


## License

**The Unlicense** — released into the public domain, no copyright, no restrictions. Use, modify, redistribute, sell — without permission, attribution, or fee. See `LICENSE.md` for the canonical text. The bundled Montserrat font remains under the SIL Open Font License (`front/assets/fonts/montserrat/OFL.txt`); the public-domain dedication doesn't change that.