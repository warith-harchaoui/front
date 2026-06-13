# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)


Un **skill** Claude qui restreint Claude à une seule pile frontend : JavaScript pur, Tailwind CSS, Montserrat. Conforme à la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Contenu

- `front/SKILL.md` — entrée du skill avec frontmatter YAML et instructions.
- `front/references/` — fichiers de référence « progressive disclosure » (couleur, stack, checklist, guides UI).
- `front/assets/` — templates à copier-coller et fichiers Montserrat.

## Ce que le skill impose

- Le code produit utilise du JS pur (modules ES, `<dialog>` natif, custom elements quand c'est justifié). Pas de React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Le code utilise des classes utilitaires Tailwind avec tokens sémantiques (`bg-brand-blue`, `text-label-primary`). Pas de hex brut dans le markup.
- Le code utilise Montserrat comme unique police d'interface, auto-hébergée depuis `assets/fonts/montserrat/`.
- Le code pose une variante `dark:` sur chaque élément stylé, utilise `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` en priorité, expose un anneau de focus visible, respecte `prefers-reduced-motion`, et tient une cible de 44×44 px minimum.
- Les choix de couleur renvoient aux quatre palettes de `references/color-psychology.md` (source : <https://harchaoui.org/warith/colors/>).

## CLI → IHM

Le skill inclut un workflow qui prend un outil en ligne de commande existant et produit une IHM mono-page en vanilla JS + Tailwind. Le workflow lit le parseur d'arguments du CLI, classe chaque commande (action unique / formulaire / streaming / liste), mappe les flags vers des contrôles de formulaire, et branche l'exécution sur l'hôte du projet (Tauri, Electron, FastAPI, Express, ou un stub navigateur). Voir `front/SKILL.md` → « CLI → GUI workflow ».

## Installation

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front
```

Vérification :

```bash
ls ~/.claude/skills/front/SKILL.md
```

Claude Code lit la description du frontmatter et applique le skill quand un message utilisateur correspond à ses phrases déclencheuses.

### OpenCode

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Invocation : `/skill front <demande>`.

### LangChain / SDK Anthropic (Python)

Charger `SKILL.md` comme fragment de system prompt. Ajouter les fichiers référencés à la demande.

```python
# pip install anthropic
from pathlib import Path
from anthropic import Anthropic

SKILL_DIR = Path("front")
client = Anthropic()

def charger_skill() -> str:
    return (SKILL_DIR / "SKILL.md").read_text()

def reference_eventuelle(message: str) -> str:
    refs = []
    m = message.lower()
    if "couleur" in m or "color" in m:
        refs.append((SKILL_DIR / "references/color-psychology.md").read_text())
    if "bouton" in m or "modale" in m or "formulaire" in m:
        refs.append((SKILL_DIR / "references/ui-guidelines/INDEX.md").read_text())
    return "\n\n---\n\n".join(refs)

def demander(message: str) -> str:
    systeme = charger_skill() + "\n\n" + reference_eventuelle(message)
    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=systeme,
        messages=[{"role": "user", "content": message}],
    )
    return resp.content[0].text

print(demander("Génère un bouton principal libellé « Commencer »."))
```

Pour LangChain à proprement parler, encapsuler la même logique dans un `ChatPromptTemplate` avec un `SystemMessage(content=charger_skill())` et utiliser `langchain_anthropic.ChatAnthropic`.

## Structure du dépôt

```
front/                              ← racine du dépôt
├── README.md / LISEZMOI.md         ← EN / FR
├── .gitignore
└── front/                          ← dossier du skill ; à déposer dans ~/.claude/skills/
    ├── SKILL.md
    ├── references/
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← couleur, typo, mise en page, mouvement, matériaux, a11y, …
    │       ├── components/         ← boutons, alertes, sheets, navigation, champs, …
    │       ├── patterns/           ← modalité, feedback, chargement, réglages, …
    │       ├── inputs/             ← clavier, pointeur, toucher, focus
    │       └── platforms/          ← mobile, tablette, desktop, wearable, tv, spatial
    └── assets/
        ├── starter-page.html       ← amorçage mono-fichier (Tailwind Play CDN)
        ├── components/             ← snippets HTML à copier-coller
        └── fonts/montserrat/       ← variable + 4 statiques WOFF2, OFL.txt, fonts.css
```

## Remerciements

Remerciements particuliers à **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** pour les discussions fructueuses.

Palettes de couleurs depuis <https://harchaoui.org/warith/colors/>.

Montserrat par Julieta Ulanovsky et contributeurs — <https://github.com/JulietaUla/Montserrat> — SIL Open Font License. Les fichiers sont inclus dans `front/assets/fonts/montserrat/`.

## Licence

MIT pour le code du skill. Montserrat est sous OFL — voir `front/assets/fonts/montserrat/OFL.txt`.
