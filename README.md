[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

# front — vanilla JS + Tailwind frontend skill

A Claude **skill** ([Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)) that turns Claude into a focused frontend engineer with one stack and one type family:

- **Vanilla JavaScript** — no React, Vue, Svelte, Next.js. ES modules, native `<dialog>`, custom elements only when justified.
- **Tailwind CSS** — semantic tokens, dark mode via `data-color-scheme`, sensible plugins.
- **Montserrat** — self-hosted from the bundled `assets/fonts/montserrat/`.
- **Curated UI guidelines** — color, typography, layout, motion, materials, accessibility, writing, dark mode, RTL, inclusion, and a full set of component / pattern references.
- **Color choices grounded in psychology** — using the palettes at <https://harchaoui.org/warith/colors/> (Choice / Emotion / Concept / Psychology).

## Flagship use case — give your CLI a GUI

If you already have a **nicely-built command-line tool**, this skill is enough to build the matching **graphical interface** on top of it, in a single Claude session:

> *"Read my CLI's `--help` and source, then generate a single-page vanilla-JS + Tailwind UI that drives every sub-command."*

The skill reads the CLI's argument parser, categorizes each command (one-shot / form-driven / streaming / list), picks a layout (tab bar, sidebar, or `⌘K` palette), maps flags to form controls, wires execution to your host (Tauri / Electron / `fastapi` / `express` / browser stub), streams output to a log panel, and ships a working `index.html`.

Other use cases the skill handles:

- New components (button, card, modal, sheet, alert, nav, tab bar, form, popover, menu, …).
- New pages or landing surfaces.
- Redesigns or audits of existing UI.
- Token sets and starter templates.
- Migration *away* from a framework toward vanilla JS.

## Quick start

### 1. With Claude Code (CLI)

```bash
# Clone or download this repo, then place the skill folder in your skills dir
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front

# Verify
ls ~/.claude/skills/front/SKILL.md
```

Then in any Claude Code session:

```text
Use the front skill to build me a settings page with a theme switcher.
```

Claude Code auto-discovers the skill from its frontmatter description and applies it when the request matches.

### 2. With OpenCode

[OpenCode](https://opencode.ai) supports the Anthropic skill format. Drop the skill folder in OpenCode's skills directory:

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Then trigger from a chat:

```text
/skill front Generate a login form with email + password, dark mode aware.
```

### 3. With LangChain (Python)

For programmatic use, treat `SKILL.md` as a system-prompt fragment. The pattern below loads the skill and any reference file the user's task triggers, then calls Claude via the Anthropic SDK:

```python
# pip install anthropic langchain-anthropic
from pathlib import Path
from anthropic import Anthropic

SKILL_DIR = Path("front")
client = Anthropic()

def load_skill():
    skill_md = (SKILL_DIR / "SKILL.md").read_text()
    return skill_md

def maybe_load_reference(user_msg: str) -> str:
    refs = []
    if "color" in user_msg.lower():
        refs.append((SKILL_DIR / "references/color-psychology.md").read_text())
    if "button" in user_msg.lower() or "modal" in user_msg.lower():
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

print(ask("Build me a primary CTA button labeled 'Get started'."))
```

For LangChain proper, wrap the same logic in a `ChatPromptTemplate` with `SystemMessage(content=load_skill())` and use `langchain_anthropic.ChatAnthropic`.

## What the skill produces

- **Semantic HTML** — `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>` first; ARIA only when no semantic element fits.
- **Tailwind classes** with semantic tokens (`bg-brand-blue`, `text-label-primary`) — never raw hex.
- **Dark-mode peer** on every styled element.
- **`Escape` closes dialogs**, visible focus rings, ≥ 44×44 hit areas, `prefers-reduced-motion` honored.
- **Montserrat** preferred, with a system-font fallback stack.
- **Bilingual EN/FR copy** when the project ships both.

## Repository structure

```
front/                              ← repo root
├── README.md / LISEZMOI.md         ← human-facing READMEs (bilingual switcher)
└── front/                          ← the skill folder (drop into ~/.claude/skills/)
    ├── SKILL.md                    ← required entry point (frontmatter + instructions)
    ├── references/                 ← progressive-disclosure reference docs
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← color, typography, layout, motion, materials, a11y, …
    │       ├── components/         ← buttons, alerts, sheets, nav, fields, …
    │       ├── patterns/           ← modality, feedback, loading, settings, …
    │       ├── inputs/             ← keyboard, pointer, touch, focus
    │       └── platforms/          ← mobile, tablet, desktop, wearable, tv, spatial
    └── assets/
        ├── starter-page.html       ← bootstrap a full page
        ├── components/             ← copy-paste HTML snippets
        └── fonts/montserrat/       ← Montserrat WOFF2 + OFL.txt + paste-ready fonts.css
```

## Status

Early but functional. SKILL.md, the core stack docs, and a curated set of UI-guideline references are in place. More component / pattern files are added iteratively as needs surface.

## Acknowledgements

Special thanks to **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** for fruitful discussions that shaped this skill.

Color palettes from <https://harchaoui.org/warith/colors/> — Choice, Emotion, Concept, and Psychology.

Type family **Montserrat** by Julieta Ulanovsky and contributors — <https://github.com/JulietaUla/Montserrat> — under the SIL Open Font License. The font files are bundled in `front/assets/fonts/montserrat/` for offline self-hosting.

## License

MIT for the skill source. The bundled Montserrat font is OFL — see `front/assets/fonts/montserrat/OFL.txt`.
