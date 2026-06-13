# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

Auteur : [Warith HARCHAOUI](https://www.linkedin.com/in/warith-harchaoui/)

Un **skill** Claude pour une seule pile frontend : JavaScript pur, Tailwind CSS, Montserrat. Conforme à la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Contenu

- `front/SKILL.md` — point d'entrée du skill, avec frontmatter YAML et instructions.
- `front/references/` — fichiers de référence à divulgation progressive (couleur, stack, checklist, guides UI).
- `front/assets/` — modèles à copier-coller et fichiers Montserrat.

## Ce que le skill garantit

- Le code produit est en JavaScript pur (modules ES, `<dialog>` natif, custom elements quand c'est justifié). Pas de React, Vue, Svelte, Next.js, Nuxt, Angular ni Solid.
- Le code utilise des classes utilitaires Tailwind avec des tokens sémantiques (`bg-brand-blue`, `text-label-primary`). Pas de couleur hexadécimale brute dans le balisage.
- Le code n'utilise que Montserrat comme police d'interface, auto-hébergée depuis `assets/fonts/montserrat/`.
- Le code pose une variante `dark:` sur chaque élément stylé, privilégie `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>`, expose un anneau de focus visible, respecte `prefers-reduced-motion`, et garantit une cible tactile d'au moins 44×44 px.
- Les choix de couleur renvoient aux quatre palettes de `references/color-psychology.md` (source : <https://harchaoui.org/warith/colors/>).

## CLI → IHM

Le skill inclut un workflow qui part d'un outil en ligne de commande existant pour produire une IHM mono-page en JavaScript pur et Tailwind. Le workflow lit le parseur d'arguments du CLI, classe chaque commande (action unique / formulaire / streaming / liste), associe chaque flag à un contrôle de formulaire, puis câble l'exécution sur l'hôte du projet (Tauri, Electron, FastAPI, Express, ou un bouchon navigateur). Voir `front/SKILL.md` → « CLI → GUI workflow ».

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

Claude Code lit la description du frontmatter et active le skill dès qu'un message correspond à ses phrases déclencheuses.

### OpenCode

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Invocation : `/skill front <demande>`.

### LangChain / SDK Anthropic (Python)

Charger `SKILL.md` comme fragment de prompt système, puis ajouter les fichiers de référence au fil des besoins.

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

Pour LangChain proprement dit, encapsuler la même logique dans un `ChatPromptTemplate` avec un `SystemMessage(content=charger_skill())`, et utiliser `langchain_anthropic.ChatAnthropic`.

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
    │       ├── foundations/        ← couleur, typo, mise en page, animation, matériaux, accessibilité, …
    │       ├── components/         ← boutons, alertes, panneaux, navigation, champs, …
    │       ├── patterns/           ← modalité, feedback, chargement, réglages, …
    │       ├── inputs/             ← clavier, pointeur, toucher, focus
    │       └── platforms/          ← mobile, tablette, ordinateur, montre, téléviseur, spatial
    └── assets/
        ├── starter-page.html       ← amorçage en un seul fichier (Tailwind Play CDN)
        ├── components/             ← extraits HTML à copier-coller
        └── fonts/montserrat/       ← variable + 4 statiques WOFF2, OFL.txt, fonts.css
```

## Remerciements

Un grand merci à **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** et **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** pour nos discussions fructueuses.

Palettes de couleurs issues de <https://harchaoui.org/warith/colors/>.

Police Montserrat fournie dans `front/assets/fonts/montserrat/` sous SIL Open Font License — voir le fichier `OFL.txt` joint pour la licence complète et la mention de droits d'auteur associée.

Le skill puise également des connaissances dans les [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) et [Google Material Design](https://material.io/design).

## Licence

**The Unlicense** — code publié dans le domaine public, sans copyright ni restrictions. Vous pouvez l'utiliser, le modifier, le redistribuer ou le vendre, sans permission, attribution ni redevance. Voir `LICENSE.md` pour le texte canonique. La police Montserrat reste sous SIL Open Font License (`front/assets/fonts/montserrat/OFL.txt`) — la dédicace au domaine public ne change pas ce point.
