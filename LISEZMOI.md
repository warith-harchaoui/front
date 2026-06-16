


# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

<p align="center">
  <img src="assets/logo.png" alt="Front — quatre skills Claude / OpenCode pour des frontends en JavaScript pur + Tailwind" width="240">
</p>

## De quoi s'agit-il ?

`front`, c'est **quatre petits skills Claude / OpenCode** qui cadrent
l'agent sur une seule pile frontend — JavaScript pur, Tailwind CSS,
Montserrat ou Inter — et lui fournissent un système de design soigné.
Demander à l'agent de « construire une UI », « habiller ce CLI d'une
IHM », « transformer ce dossier de markdown en site » ou « auditer
l'accessibilité » oriente vers le bon skill et produit du code dans
la même pile : HTML sémantique, variante `dark:` sur chaque élément
stylé, anneau de focus visible, garde-fous pour `prefers-reduced-motion`,
graphiques en Vega-Lite, texte alternatif rédigé selon les recommandations
W3C / WAI.

Les quatre skills :

| Skill | Quand l'installer | Phrases déclencheuses |
|---|---|---|
| **front-ui** | Toujours — il porte les règles de pile et les tokens. | « construis une UI », « crée un composant », « conçois une page », « fais un formulaire / modal / bouton / nav », « tableau de bord », « audite cette UI ». |
| **front-cli-gui** | Vous habillez des outils CLI d'une IHM web. | « habille ce CLI d'une IHM », « construis une UI pour mon script Python », « argparse vers IHM web ». |
| **front-publish** | Vous livrez des sites de doc, des landings, des meta-tags, des favicons. | « transforme ce dossier markdown en site », « meta tags », « favicons », « robots.txt », « sitemap », « llms.txt », « flux Atom », « langage clair », « réécris au niveau 6e ». |
| **front-a11y** | Vous avez besoin d'audits d'accessibilité et de contenu (texte alternatif, sous-titres). | « lint a11y », « vérif WCAG », « audit de contraste », « texte alternatif », « décris cette image », « sous-titres », « transcription », « aperçu daltonien ». |

Les skills compagnons héritent des règles de pile de `front-ui`.
N'installez que ceux dont vous avez besoin.

## À qui ça s'adresse

Aux développeurs en solo et aux petites équipes (≤ 5 personnes) qui
livrent des **outils internes** : tableaux de bord internes, panneaux
d'administration, démos ML / data, scripts CLI emballés, sites de
recherche, sites de doc pour petits projets. Vous n'avez pas de
designer dédié, vous ne voulez pas vous battre avec un framework, et
vous voulez du code qui a l'air pensé et qui tient un an sans courir
après les versions de React.

Ce **n'est pas** le bon choix pour :

- Le travail de marque pour une app grand public qui demande une
  identité visuelle propre.
- Les landings marketing où Webflow ou Framer sont plus rapides.
- Les apps où l'équipe a déjà choisi React / Vue / Svelte — préférez
  shadcn / Headless UI / Mantine.
- Les sites de doc versionnés à plusieurs centaines de pages —
  préférez MkDocs Material, Hugo ou Astro.

Pour les alternatives par catégorie et l'aide à la décision « est-ce
que `front` est le bon outil ? », voir [LANDSCAPE.md](LANDSCAPE.md).

## Ce que les skills garantissent

- Le code produit est en JavaScript pur (modules ES, `<dialog>` natif,
  custom elements quand c'est justifié). Pas de React, Vue, Svelte,
  Next.js, Nuxt, Angular ni Solid.
- Le code utilise des classes utilitaires Tailwind avec des tokens
  sémantiques (`bg-brand-blue`, `text-label-primary`). Pas de couleur
  hexadécimale brute dans le balisage.
- Le code utilise **Montserrat** par défaut pour les surfaces
  marketing / texte long, ou **Inter** pour les UI denses
  développeur / tableau de bord / data. Montserrat n'est pas toujours
  le bon choix : si vous déposez une famille auto-hébergée sous
  `front-ui/assets/fonts/<famille>/` (TTF ou WOFF2 + licence),
  `front-ui` bascule vers cette famille. Toutes les polices sont
  auto-hébergées (pas de CDN Google Fonts en production).
- Le code pose une variante `dark:` sur chaque élément stylé,
  privilégie `<button>` / `<a>` / `<label>` / `<dialog>` / `<form>`,
  expose un anneau de focus visible, respecte `prefers-reduced-motion`,
  et garantit une cible tactile d'au moins 44 × 44 px.
- Les choix de couleur renvoient aux palettes de
  `front-ui/references/color-psychology.md` (source :
  <https://harchaoui.org/warith/colors/>).
- Tailwind a une étape de build. La page d'amorçage utilise le Play
  CDN, à réserver au prototypage — voir
  `front-ui/references/stack-tailwind.md` pour le bascule production
  (Tailwind CLI ou Vite).
- Copy bilingue par défaut : anglais en sortie, bascule sur la langue
  de l'utilisateur. La paire de langues est configurable par projet
  (EN/FR, EN/DE, EN/ES, EN/JA, …) — voir
  `front-publish/references/i18n.md`.

## Entrées → sorties

Ce que vous donnez à l'agent et ce qu'il vous renvoie. Chaque ligne
est un flux autonome — prenez celle qui vous concerne, ignorez le
reste.

| Vous fournissez | Phrase | Skill | Sortie |
|---|---|---|---|
| Un CLI fonctionnel (`tool --help`, source avec `argparse` / `click` / `clap` / `commander` / `cobra`) | « Habille ce CLI d'une IHM » + chemin du projet | `front-cli-gui` | Page unique `index.html` + `app.js` + Tailwind CSS, sous-commandes mappées en formulaires / flux / tables, exécution câblée sur votre hôte (Tauri / Electron / FastAPI / Express / bouchon navigateur). Inter auto-hébergée. |
| Un dossier de fichiers Markdown (README, `docs/**`, articles) | « Transforme ces fichiers markdown en site » | `front-publish` | Site statique : une page HTML par `.md`, barre supérieure collante, sommaire latéral pour `docs/`, mode sombre, favicons, balises `<meta>`, `robots.txt` + `sitemap.xml` + `llms.txt` + flux Atom. |
| Une demande libre (« bouton primaire », « dialogue de confirmation », « page réglages ») | « Construis un `<composant>` » | `front-ui` | HTML sémantique + Tailwind + JS minimal, anneau de focus, variante `dark:`, zone tactile 44 × 44 px, fermeture par `Échap`, garde-fou `prefers-reduced-motion`. |
| Un jeu de données (CSV, JSON, quelques lignes collées) | « Trace ça » / « Tableau de bord pour X » | `front-ui` | Spec Vega-Lite v5 JSON + wrapper `<figure>`. Style maison, palette de `color-psychology.md`, axes avec polarité, `role="img"`. |
| Une page HTML existante ou une capture d'écran | « Audite » / « Vérif WCAG » / « Rends ça moins IA » | `front-ui` (anti-patterns, ergonomie) + `front-a11y` (lint, contraste, daltonisme) | Constats au regard des 8 critères ergonomiques + catalogue d'anti-patterns ; diffs concrets ; checklist pré-livraison ; sorties `lint_a11y` + `audit_contrast` + `simulate_cvd`. |
| Une image (`*.png`, `*.jpg`, …) | « Texte alternatif pour cette image » | `front-a11y` | Texte alternatif conforme W3C dans la bonne catégorie (informatif / décoratif / fonctionnel / texte / complexe / groupe), rédigé dans la langue de la page, marqué `data-alt-source="ai"`. |
| Un fichier audio ou vidéo (`.mp4`, `.wav`, `.mp3`, …) | « Sous-titres / transcription » | `front-a11y` | Sous-titres WebVTT / SRT / texte brut depuis Whisper local, avec biais de vocabulaire issu du projet. Extrait `<video>` + `<track kind="captions">` à coller. |
| Un logo (`logo.png` / `.svg`) | « Jeu de favicons » / « Icônes PWA » | `front-publish` | `favicon.svg` + `.ico` + lot de PNG + `apple-touch-icon.png` + icône PWA masquable + `site.webmanifest` + extrait `head.html`. |
| Une description d'objectif ou une page HTML | « Meta tags » / « SEO » / « OG card » | `front-publish` | Titre + description + Open Graph + Twitter Card + JSON-LD Schema.org. JSON sur stdout. |
| Du copy d'IHM brut | « Langage clair » / « Réécris au niveau 6e » | `front-publish` | Même sens, voix marketing retirée, longueur de sortie ≤ 1,1× l'original. |
| Une palette JSON | « Audit de contraste » / « Ma palette est-elle accessible ? » | `front-a11y` | Chaque paire `(label, surface)` parcourue, échecs listés avec la correction OKLCH voisine la plus proche. Sortie 1 sur échec. |
| Une page finalisée / capture d'écran | « Vérif pré-livraison » | `front-ui` + `front-a11y` | La porte `checklist.md` exécutée ; lint + contraste + daltonisme passent ; copy / animation / performance vérifiés. |

> Pas sûr quelle ligne correspond ? Décrivez l'entrée en français courant. L'arbre de décision de chaque `SKILL.md` mappe les formulations vers les workflows.

## Installation

Les skills suivent la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
et sont lus nativement par **Claude Code** et **OpenCode**. N'installez
que ceux qui vous servent.

### Claude Code

```bash
git clone https://github.com/warith-harchaoui/front.git
mkdir -p ~/.claude/skills

# Toujours :
cp -r front/front-ui      ~/.claude/skills/front-ui

# Selon vos besoins :
cp -r front/front-cli-gui ~/.claude/skills/front-cli-gui
cp -r front/front-publish ~/.claude/skills/front-publish
cp -r front/front-a11y    ~/.claude/skills/front-a11y
```

Vérification :

```bash
ls ~/.claude/skills/front-ui/SKILL.md
```

Claude Code lit la description du frontmatter de chaque skill et active
le bon dès qu'un message correspond à ses phrases déclencheuses.

### OpenCode

[OpenCode](https://opencode.ai) est un agent de code en terminal, open
source, qui sait piloter Claude, GPT et des modèles locaux derrière la
même expérience.

```bash
mkdir -p ~/.opencode/skills
cp -r front/front-* ~/.opencode/skills/
```

À privilégier si vous voulez l'expérience des skills sans dépendance à
un fournisseur unique, ou si OpenCode est déjà votre outil quotidien.

## CLI → IHM, le cas d'usage phare

Le skill `front-cli-gui` part d'un outil en ligne de commande existant
et produit une IHM mono-page en JavaScript pur + Tailwind. Le workflow
lit le parseur d'arguments du CLI, classe chaque commande (action
unique / formulaire / streaming / liste), associe chaque flag à un
contrôle de formulaire, puis câble l'exécution sur l'hôte du projet
(Tauri, Electron, FastAPI, Express, ou un proxy HTTP + SSE en stdlib).

Un exemple exécutable d'environ 700 lignes est livré dans
`front-cli-gui/assets/examples/cli-gui-demo/`. Pour le lancer :

```bash
cd front-cli-gui/assets/examples/cli-gui-demo
python server.py  # stdlib uniquement, ouvre http://localhost:8787
```

Pour une comparaison honnête face à Gradio / Streamlit / Tauri / Taipy,
voir `front-cli-gui/SKILL.md` → « Why this skill, not Gradio / Streamlit
/ Tauri / Taipy » et [LANDSCAPE.md](LANDSCAPE.md) § 7.

## Structure du dépôt

```text
front/                                  ← racine du dépôt
├── README.md / LISEZMOI.md             ← EN / FR
├── LANDSCAPE.md                        ← matrices comparatives vs alternatives
├── CHANGELOG.md                        ← notes de version
├── CONTRIBUTING.md                     ← comment proposer des changements
├── LICENSE.md                          ← The Unlicense (OFL pour Montserrat + Inter)
├── llms.txt                            ← index https://llmstxt.org/ pour les LLM
├── pytest.ini, requirements-dev.txt    ← outillage dev partagé
├── tests/                              ← suite pytest partagée pour les quatre skills
├── assets/logo.png                     ← logo du projet
│
├── front-ui/                           ← skill de génération d'UI
│   ├── SKILL.md
│   ├── references/                     ← couleur, pile, composants, dataviz, design system, checklist
│   ├── scripts/                        ← validate.py (stdlib uniquement)
│   └── assets/                         ← starter-page, composants, polices Montserrat + Inter
│
├── front-cli-gui/                      ← skill CLI → IHM (phare)
│   ├── SKILL.md
│   ├── references/cli-gui-workflow.md
│   └── assets/examples/cli-gui-demo/   ← exemple exécutable
│
├── front-publish/                      ← Markdown → site + meta + favicons + index + langage clair
│   ├── SKILL.md
│   ├── references/                     ← meta-tags, site-indexes, plain-language, i18n
│   └── scripts/                        ← favicons.py, meta_from_ollama.py, site_indexes.py, plain_language.py
│
└── front-a11y/                         ← audits d'accessibilité + outillage de contenu
    ├── SKILL.md
    ├── references/                     ← lint-a11y, contrast-audit, cvd-simulation, alt-text-ai, captions-ai
    └── scripts/                        ← lint_a11y.py, audit_contrast.py, simulate_cvd.py, alt_from_ollama.py, install_alt_ai.py, captions_from_whisper.py, install_captions.py
```

## Auteur

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

Quatre petits **skills** Claude / OpenCode pour une seule pile
frontend : JavaScript pur, Tailwind CSS, Montserrat ou Inter. Conformes
à la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Un grand merci à
**[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**,
**[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** et
**[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)**
pour nos discussions fructueuses.

Palettes de couleurs issues de <https://harchaoui.org/warith/colors/>.

La police Montserrat est livrée dans
`front-ui/assets/fonts/montserrat/` sous SIL Open Font License — voir
le fichier `OFL.txt` joint. Inter est référencée depuis
[rsms.me/inter](https://rsms.me/inter/) (OFL) ; téléchargez le fichier
WOFF2 séparément pour l'auto-hébergement.

Le skill puise également des connaissances dans les
[Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
et [Google Material Design](https://material.io/design).

## Licence

**The Unlicense** — code publié dans le domaine public, sans
copyright ni restrictions. Vous pouvez l'utiliser, le modifier, le
redistribuer ou le vendre, sans permission, attribution ni redevance.
Voir `LICENSE.md` pour le texte canonique. La police Montserrat reste
sous SIL Open Font License
(`front-ui/assets/fonts/montserrat/OFL.txt`) — la dédicace au domaine
public ne change pas ce point.
