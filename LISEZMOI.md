[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

# front — skill frontend en JS pur + Tailwind

Un **skill** Claude ([spécification Anthropic](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)) qui transforme Claude en ingénieur frontend ciblé, avec une seule pile technique et une seule famille typographique :

- **JavaScript pur (vanilla)** — pas de React, Vue, Svelte ni Next.js. Modules ES, `<dialog>` natif, custom elements seulement quand c'est justifié.
- **Tailwind CSS** — tokens sémantiques, mode sombre via `data-color-scheme`, plugins raisonnables.
- **Montserrat** — auto-hébergée depuis `assets/fonts/montserrat/`.
- **Guides UI sélectionnés** — couleur, typographie, mise en page, mouvement, matériaux, accessibilité, écriture, mode sombre, RTL, inclusion, plus un ensemble complet de composants et de patterns.
- **Choix de couleurs fondés sur la psychologie** — depuis <https://harchaoui.org/warith/colors/> (Choix / Émotion / Concept / Psychologie).

## Cas d'usage phare — donner une IHM à votre CLI

Si vous disposez déjà d'un **outil en ligne de commande bien fait**, ce skill suffit à construire l'**interface graphique** correspondante, en une seule session Claude :

> *« Lis le `--help` et les sources de mon CLI, puis génère une UI vanilla-JS + Tailwind d'une seule page qui pilote toutes ses sous-commandes. »*

Le skill lit le parseur d'arguments du CLI, classe chaque commande (action unique / formulaire / streaming / liste), choisit une mise en page (tab bar, sidebar ou palette `⌘K`), mappe les flags vers des contrôles de formulaire, branche l'exécution sur votre hôte (Tauri / Electron / `fastapi` / `express` / stub navigateur), envoie la sortie vers un panneau de log et livre un `index.html` qui fonctionne.

Autres cas couverts :

- Nouveaux composants (bouton, carte, modale, sheet, alerte, nav, tab bar, formulaire, popover, menu, …).
- Nouvelles pages ou landings.
- Refonte ou audit d'UI existante.
- Jeux de tokens et templates de démarrage.
- Migration *depuis* un framework vers du JS pur.

## Démarrage rapide

### 1. Avec Claude Code (CLI)

```bash
# Cloner ou télécharger ce dépôt, puis copier le dossier du skill
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front

# Vérification
ls ~/.claude/skills/front/SKILL.md
```

Ensuite, dans n'importe quelle session Claude Code :

```text
Utilise le skill front pour me construire une page de réglages avec un sélecteur de thème.
```

Claude Code détecte automatiquement le skill grâce à sa description en frontmatter et l'applique quand la demande correspond.

### 2. Avec OpenCode

[OpenCode](https://opencode.ai) supporte le format de skill Anthropic. Déposer le dossier dans le répertoire dédié :

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

Puis depuis un chat :

```text
/skill front Génère un formulaire de connexion email + mot de passe, compatible mode sombre.
```

### 3. Avec LangChain (Python)

Pour un usage programmatique, traiter `SKILL.md` comme un fragment de system prompt. Le pattern ci-dessous charge le skill et tout fichier de référence pertinent, puis appelle Claude via le SDK Anthropic :

```python
# pip install anthropic langchain-anthropic
from pathlib import Path
from anthropic import Anthropic

SKILL_DIR = Path("front")
client = Anthropic()

def charger_skill():
    return (SKILL_DIR / "SKILL.md").read_text()

def reference_eventuelle(message: str) -> str:
    refs = []
    if "couleur" in message.lower() or "color" in message.lower():
        refs.append((SKILL_DIR / "references/color-psychology.md").read_text())
    if "bouton" in message.lower() or "modale" in message.lower():
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

print(demander("Donne-moi un bouton principal libellé « Commencer »."))
```

Pour LangChain à proprement parler, encapsuler la même logique dans un `ChatPromptTemplate` avec `SystemMessage(content=charger_skill())` et utiliser `langchain_anthropic.ChatAnthropic`.

## Ce que produit le skill

- **HTML sémantique** — `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>` d'abord ; ARIA seulement si aucun élément sémantique ne convient.
- **Classes Tailwind** avec tokens sémantiques (`bg-brand-blue`, `text-label-primary`) — jamais de hex brut.
- **Variante `dark:`** sur chaque élément stylé.
- **`Échap` ferme les dialogues**, anneaux de focus visibles, cibles ≥ 44×44 px, `prefers-reduced-motion` respecté.
- **Montserrat** par défaut, avec fallback stack système.
- **Copy bilingue EN/FR** quand le projet ship les deux.

## Structure du dépôt

```
front/                              ← racine du dépôt
├── README.md / LISEZMOI.md         ← README humains (sélecteur bilingue)
└── front/                          ← dossier du skill (à déposer dans ~/.claude/skills/)
    ├── SKILL.md                    ← entrée requise (frontmatter + instructions)
    ├── references/                 ← références « progressive disclosure »
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← couleur, typo, mise en page, mouvement, matériaux, a11y, …
    │       ├── components/         ← boutons, alertes, sheets, nav, champs, …
    │       ├── patterns/           ← modalité, feedback, chargement, réglages, …
    │       ├── inputs/             ← clavier, pointeur, toucher, focus
    │       └── platforms/          ← mobile, tablette, desktop, wearable, tv, spatial
    └── assets/
        ├── starter-page.html       ← amorcer une page complète
        ├── components/             ← snippets HTML à copier-coller
        └── fonts/montserrat/       ← Montserrat WOFF2 + OFL.txt + fonts.css prêt à l'emploi
```

## Statut

Tôt mais fonctionnel. SKILL.md, les docs « stack » de base et un ensemble sélectionné de références UI sont en place. D'autres fichiers de composants et de patterns sont ajoutés au fil des besoins.

## Remerciements

Remerciements particuliers à **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** pour les discussions fructueuses qui ont façonné ce skill.

Palettes de couleurs issues de <https://harchaoui.org/warith/colors/> — Choix, Émotion, Concept et Psychologie.

Famille typographique **Montserrat** par Julieta Ulanovsky et contributeurs — <https://github.com/JulietaUla/Montserrat> — sous SIL Open Font License. Les fichiers sont inclus dans `front/assets/fonts/montserrat/` pour l'auto-hébergement hors ligne.

## Licence

MIT pour le code du skill. La police Montserrat est sous OFL — voir `front/assets/fonts/montserrat/OFL.txt`.
