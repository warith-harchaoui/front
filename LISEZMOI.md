<p align="center">
  <img src="assets/logo.png" alt="Front — un skill Claude pour des frontends JavaScript pur + Tailwind + Montserrat" width="240">
</p>

# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

## De quoi s'agit-il ?

`front` est un skill Claude qui cadre Claude sur une seule pile frontend — JavaScript pur, Tailwind CSS et Montserrat comme unique police d'interface — et lui fournit un système de design soigné. Demander à Claude de « construire une UI », « créer un composant », « concevoir un tableau de bord » ou « habiller ce CLI d'une IHM » produit du code dans cette pile exacte, avec un parti pris reproductible : HTML sémantique, variante `dark:` sur chaque élément stylé, anneau de focus visible, garde-fous pour `prefers-reduced-motion`, choix de couleurs traçables à une psychologie documentée, graphiques en Vega-Lite, texte alternatif rédigé selon les recommandations W3C / WAI.

## À quoi ça sert ?

La plupart des frontends produits par des LLM partagent une esthétique générique — dégradés violets, cartes glassmorphiques, formules marketing, grilles à trois cartes — parce que le modèle se rabat sur les motifs les plus courants de son entraînement. Ce skill remplace ces réflexes par un parti pris ferme : une seule pile, une seule police, une seule philosophie de couleur, un seul jeu de critères ergonomiques. Le résultat : du code frontend cohérent d'une session à l'autre, débarrassé des « tics » d'IA, prêt à être livré dans tout projet adoptant cette pile.

Le cas d'usage phare, c'est **CLI → IHM** : pointez Claude vers le `--help` d'un outil en ligne de commande existant, et le skill produit l'IHM JavaScript pur + Tailwind correspondante en une seule session. Autres cas d'usage : nouveaux composants, pages entières, audits ergonomiques, tableaux de bord et dataviz, migration depuis un framework vers le JavaScript pur, et outillage d'accessibilité (texte alternatif W3C, meta-tags, jeu de favicons, validateur).

## Contenu

- `front/SKILL.md` — point d'entrée du skill, avec frontmatter YAML et instructions.
- `front/references/` — fichiers de référence à divulgation progressive (couleur, stack, checklist, guides UI, dataviz, meta-tags, i18n, anti-patterns, psychologie UX, Material Design, texte alternatif, sous-titres, audits contraste / daltonisme, réécriture en langage clair, lint a11y, index de site).
- `front/assets/` — modèles à copier-coller, fichiers Montserrat, et un exemple CLI → IHM exécutable (`assets/examples/cli-gui-demo/`).
- `front/scripts/` — utilitaires Python, chacun avec son fichier de dépendances dédié :
  - **Garde-fou pré-livraison** — `validate.py`, `lint_a11y.py`, `audit_contrast.py`, `site_indexes.py` (stdlib uniquement).
  - **Assets & meta** — `favicons.py`, `meta_from_ollama.py`.
  - **Outillage accessibilité** — `alt_from_ollama.py`, `install_alt_ai.py`, `simulate_cvd.py`, `plain_language.py`.
  - **Sous-titres / transcription** — `install_captions.py`, `captions_from_whisper.py`.
- `llms.txt` — index du projet conforme à <https://llmstxt.org/> pour les consommateurs LLM.
- `assets/logo.png` — logo du projet (utilisé en tête de ce LISEZMOI).

## Ce que le skill garantit

- Le code produit est en JavaScript pur (modules ES, `<dialog>` natif, custom elements quand c'est justifié). Pas de React, Vue, Svelte, Next.js, Nuxt, Angular ni Solid.
- Le code utilise des classes utilitaires Tailwind avec des tokens sémantiques (`bg-brand-blue`, `text-label-primary`). Pas de couleur hexadécimale brute dans le balisage.
- Le code n'utilise que Montserrat comme police d'interface, auto-hébergée depuis `assets/fonts/montserrat/`.
- Le code pose une variante `dark:` sur chaque élément stylé, privilégie `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>`, expose un anneau de focus visible, respecte `prefers-reduced-motion`, et garantit une cible tactile d'au moins 44×44 px.
- Les choix de couleur renvoient aux quatre palettes de `references/color-psychology.md` (source : <https://harchaoui.org/warith/colors/>).

## CLI → IHM

Le skill inclut un workflow qui part d'un outil en ligne de commande existant pour produire une IHM mono-page en JavaScript pur et Tailwind. Le workflow lit le parseur d'arguments du CLI, classe chaque commande (action unique / formulaire / streaming / liste), associe chaque flag à un contrôle de formulaire, puis câble l'exécution sur l'hôte du projet (Tauri, Electron, FastAPI, Express, ou un bouchon navigateur). Voir `front/SKILL.md` → « CLI → GUI workflow ».

## Installation

Ce skill suit la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) : il est lu nativement — activation depuis le frontmatter, divulgation progressive des fichiers `references/`, appel direct des `scripts/` — par deux agents de code : **Claude Code** et **OpenCode**. Choisissez celui qui correspond à votre éditeur et à votre modèle préféré.

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

[OpenCode](https://opencode.ai) est un agent de code en terminal, open source, qui sait piloter Claude, GPT et des modèles locaux derrière la même expérience.

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

OpenCode reconnaît le skill via la même description de frontmatter que Claude Code et orchestre les scripts de `front/scripts/` exactement de la même manière. À privilégier si vous voulez l'expérience du skill sans dépendance à un fournisseur unique, ou si OpenCode est déjà votre outil quotidien.

## Structure du dépôt

```
front/                              ← racine du dépôt
├── README.md / LISEZMOI.md         ← EN / FR
├── LICENSE.md                      ← The Unlicense (Montserrat reste sous OFL)
├── llms.txt                        ← index https://llmstxt.org/ pour les LLM
├── assets/logo.png                 ← logo du projet (utilisé dans ce LISEZMOI)
├── .gitignore
└── front/                          ← dossier du skill ; à déposer dans ~/.claude/skills/
    ├── SKILL.md
    ├── references/
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   ├── charts-vega.md / dataviz-*.md / dashboard-ergonomics.md
    │   ├── meta-tags.md / site-indexes.md / i18n.md
    │   ├── alt-text-ai.md / captions-ai.md / plain-language.md
    │   ├── contrast-audit.md / cvd-simulation.md / lint-a11y.md
    │   ├── anti-patterns.md / ergonomics-criteria.md / ux-psychology.md / material-design.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← couleur, typo, mise en page, animation, matériaux, accessibilité, …
    │       ├── components/         ← boutons, alertes, panneaux, navigation, champs, …
    │       ├── patterns/           ← modalité, feedback, chargement, réglages, …
    │       ├── inputs/             ← clavier, pointeur, toucher, focus
    │       └── platforms/          ← mobile, tablette, ordinateur, montre, téléviseur, spatial
    ├── scripts/                    ← utilitaires Python (3.9+, multi-plateformes)
    │   ├── validate.py / lint_a11y.py / audit_contrast.py / site_indexes.py   (stdlib uniquement)
    │   ├── favicons.py / meta_from_ollama.py
    │   ├── alt_from_ollama.py / install_alt_ai.py / simulate_cvd.py / plain_language.py
    │   ├── install_captions.py / captions_from_whisper.py
    │   └── requirements*.txt        ← un fichier par fonctionnalité (alt-text, sous-titres, daltonisme, favicons, …)
    └── assets/
        ├── starter-page.html       ← amorçage en un seul fichier (Tailwind Play CDN)
        ├── components/             ← extraits HTML à copier-coller + specs Vega-Lite
        ├── examples/cli-gui-demo/  ← exemple CLI → IHM exécutable
        └── fonts/montserrat/       ← variable + 4 statiques WOFF2, OFL.txt, fonts.css
```

## Auteur

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

Un **skill** Claude pour une seule pile frontend : JavaScript pur, Tailwind CSS, Montserrat. Conforme à la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Un grand merci à **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** et **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** pour nos discussions fructueuses.

Palettes de couleurs issues de <https://harchaoui.org/warith/colors/>.

Police Montserrat fournie dans `front/assets/fonts/montserrat/` sous SIL Open Font License — voir le fichier `OFL.txt` joint pour la licence complète et la mention de droits d'auteur associée.

Le skill puise également des connaissances dans les [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) et [Google Material Design](https://material.io/design).

## Licence

**The Unlicense** — code publié dans le domaine public, sans copyright ni restrictions. Vous pouvez l'utiliser, le modifier, le redistribuer ou le vendre, sans permission, attribution ni redevance. Voir `LICENSE.md` pour le texte canonique. La police Montserrat reste sous SIL Open Font License (`front/assets/fonts/montserrat/OFL.txt`) — la dédicace au domaine public ne change pas ce point.
