


# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

<p align="center">
  <img src="assets/logo.png" alt="Front — quatre skills Claude / OpenCode pour des frontends en JavaScript pur + Tailwind" width="240">
</p>

## De quoi s'agit-il ?

`front`, c'est **quatre petits skills Claude / OpenCode** qui cadrent
l'agent sur une seule pile frontend — JavaScript pur, Tailwind CSS,
et la règle des trois Roboto (Roboto pour les sans-serif, Roboto Serif
pour les serif, Roboto Mono pour le code) — et lui fournissent un
système de design soigné.
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

`front` vise quatre publics concrets. Chaque ligne est un argumentaire
autonome : si l'un d'eux correspond à votre situation, le skill
associé se justifie déjà à lui seul.

1. **Développeurs en solo sans designer.** Des choix par défaut
   assumés pour arrêter de tergiverser sur les tokens — installez
   `front-ui` et livrez une UI utilisable dès le premier commit.
   Tokens Tailwind, variantes `dark:`, anneaux de focus, zones
   tactiles : tout est cadré.
2. **Pentesters qui écrivent des tableaux de bord internes.** Sortie
   HTML mono-fichier qui se dépose telle quelle sur une machine
   interne, sans chaîne de build. Les portes a11y (`front-a11y`)
   tournent en CI sans navigateur, donc même un outil de recon jetable
   reste lisible pour les coéquipiers sous techno d'assistance.
3. **Data scientists qui habillent des CLI.** Pointez `front-cli-gui`
   sur votre `--help` — argparse, Click, Typer, clap, commander, cobra
   se laissent introspecter — et vous obtenez une maquette d'IHM
   fonctionnelle. Pas de runtime Gradio, pas de prison React.
4. **Sites de documentation bilingues (EN/FR par défaut ; la paire
   est configurable).** `front-publish` garde la typographie et la
   tonalité alignées sur deux langues, et produit en une passe meta
   tags + favicons + sitemap. Changez la paire (EN/DE, EN/JA, EN/ES,
   …) en éditant un seul token de configuration — voir, dans chaque
   `SKILL.md`, la section « Changing the language pair ».

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
Pour des sites réels déjà livrés sur cette pile, voir
[GALLERY.md](GALLERY.md).

## Ce que les skills garantissent

- Le code produit est en JavaScript pur (modules ES, `<dialog>` natif,
  custom elements quand c'est justifié). Pas de React, Vue, Svelte,
  Next.js, Nuxt, Angular ni Solid.
- Le code utilise des classes utilitaires Tailwind avec des tokens
  sémantiques (`bg-brand-blue`, `text-label-primary`). Pas de couleur
  hexadécimale brute dans le balisage.
- Le code applique la **règle des trois Roboto** : exactement trois
  polices téléchargées, toutes issues de la super-famille Roboto —
  **Roboto** (sans-serif / UI / texte courant), **Roboto Serif**
  (longform éditorial / pages très textuelles), **Roboto Mono**
  (`<code>`, `<pre>`, panneaux terminal, logs). Aucune autre famille
  téléchargée n'est admise (ni Inter, ni Montserrat, ni IBM Plex, ni
  JetBrains Mono). Les trois familles partagent par construction les
  mêmes métriques et la même hauteur d'x — les surfaces mêlant prose
  et code restent cohérentes typographiquement. Toutes sont
  auto-hébergées (pas de CDN Google Fonts en production) ; les WOFF2
  + OFL vivent sous `front-ui/assets/fonts/roboto/`, `…/roboto-serif/`
  et `…/roboto-mono/`.
- Le code pose une variante `dark:` sur chaque élément stylé,
  privilégie `<button>` / `<a>` / `<label>` / `<dialog>` / `<form>`,
  expose un anneau de focus visible, respecte `prefers-reduced-motion`,
  et garantit une cible tactile d'au moins 44 × 44 px.
- Le code expose un **toggle 🌞 Light / 🌚 Dark / 🌗 Auto**
  (placement canonique : haut-droite du header sticky → coin
  bas-droite du footer → ancrage fixed bottom-right quand il n'y a
  pas de header). **Auto est le défaut**, pour qu'un visiteur frais
  hérite du choix de son OS et ne soit jamais surpris par un thème
  forcé. Composant :
  `front-ui/assets/components/theme-toggle.html`. Câblage :
  `front-ui/references/stack-vanilla-js.md` § « Theme switching ».
- Les choix de couleur renvoient aux palettes de
  `front-ui/references/color-psychology.md` (source :
  <https://harchaoui.org/warith/colors/>).
- La sortie du skill est **du HTML mono-fichier de niveau prototype**
  par défaut — adaptée aux démos, maquettes, outils internes et
  petites landings. La page d'amorçage utilise le CDN Play de
  Tailwind, que Tailwind lui-même réserve au prototypage. Pour un site
  de production à l'échelle, faites passer **Tailwind CLI** ou
  **Vite + Tailwind** sur le HTML émis avant déploiement ; les noms de
  classes sont stables, donc les mêmes fichiers survivent à la
  bascule. Voir `front-ui/references/stack-tailwind.md`.
- Copy bilingue (EN/FR par défaut — configurable via `lang_pair`).
  Anglais en sortie, bascule sur la langue de l'utilisateur. La paire
  par projet se règle dans le token `metadata.lang_pair` du frontmatter
  de n'importe quel skill (EN/FR, EN/DE, EN/ES, EN/JA, …) — voir
  chaque `SKILL.md` → « Changing the language pair » et
  `front-publish/references/i18n.md`. Pour une surcharge ponctuelle
  depuis le shell, utilisez la variable d'environnement
  `FRONT_LANG_PAIR` (par exemple `export FRONT_LANG_PAIR="en,fr"`) ;
  la première entrée devient le `--lang` par défaut des scripts
  Ollama quand aucun drapeau n'est passé.

## État d'avancement

Photographie de l'état de chaque surface à `v0.6.4`. Les quatre dossiers
de skills sont stables ; la seule zone en travaux est l'**audio /
sous-titres** (front-a11y, vidéo → texte). La nouvelle **narration
audio** (front-publish, texte → audio) est stable et explicitement
encadrée comme amélioration éditoriale optionnelle, pas exigence
WCAG.

| Domaine | État | Notes |
|---|---|---|
| `front-ui` (règles de pile, tokens, composants, dataviz, checklist) | Stable | Les 9 règles dures documentées ; `validate.py` stdlib uniquement ; couvert par `tests/test_validate.py`. |
| `front-cli` (pilote `front` unifié, complétion shell) | Stable | Basé sur Click ; transmission du `--help` corrigée en 0.3.0 (test de non-régression en 0.3.1). |
| `front-cli-gui` (CLI → IHM, phare) | Stable (skill + démo exécutable) | `assets/examples/cli-gui-demo/` tourne de bout en bout. Durcissement production (auth, rate-limit, sandbox) délibérément laissé à l'hôte. |
| `front-publish` (site Markdown, meta, favicons, indexes, langage clair) | Stable | 4 scripts, 18 tests déterministes, suite d'éval pour meta + langage clair. Surcharge `FRONT_LANG_PAIR` câblée. |
| `front-a11y` — lint, contraste, daltonisme, texte alternatif | Stable | Lint 14 règles, correcteur OKLCH, daltonisme Machado, éval texte alternatif sur fixtures Wikipedia. Auto-détection de la capacité vision MLX en 0.3.1. |
| `front-a11y` — **sous-titres / transcriptions** | **WiP / TODO** | `captions_from_whisper.py` est fonctionnel ; ce qui manque, ce sont les baselines WER par langue (`en` / `fr` / `es` câblés via l'extracteur, baselines pas encore publiées) et le clip utilisateur `vocab-biasing-clip.wav`. Voir [Roadmap](CHANGELOG.md#roadmap). |
| `LISEZMOI.md` (README français) | Stable | À parité structurelle avec le README EN — même ordre des sections, contenu maintenu en synchronisation à chaque release. |

Pour le détail par release (et la suite prévue), voir [`CHANGELOG.md`](CHANGELOG.md).

## Entrées → sorties

Ce que vous donnez à l'agent et ce qu'il vous renvoie. Chaque ligne
est un flux autonome — prenez celle qui vous concerne, ignorez le
reste.

| Vous fournissez | Phrase | Skill | Sortie |
|---|---|---|---|
| Un CLI fonctionnel (`tool --help`, source avec `argparse` / `click` / `clap` / `commander` / `cobra`) | « Habille ce CLI d'une IHM » + chemin du projet | `front-cli-gui` | Page unique `index.html` + `app.js` + Tailwind CSS, sous-commandes mappées en formulaires / flux / tables, exécution câblée sur votre hôte (Tauri / Electron / FastAPI / Express / bouchon navigateur). Roboto + Roboto Mono auto-hébergées. |
| Un dossier de fichiers Markdown (README, `docs/**`, articles) | « Transforme ces fichiers markdown en site » | `front-publish` | Site statique : une page HTML par `.md`, barre supérieure collante, sommaire latéral pour `docs/`, mode sombre, favicons, balises `<meta>`, `robots.txt` + `sitemap.xml` + `llms.txt` + flux Atom. |
| Une demande libre (« bouton primaire », « dialogue de confirmation », « page réglages ») | « Construis un `<composant>` » | `front-ui` | HTML sémantique + Tailwind + JS minimal, anneau de focus, variante `dark:`, zone tactile 44 × 44 px, fermeture par `Échap`, garde-fou `prefers-reduced-motion`. |
| Un jeu de données (CSV, JSON, quelques lignes collées) | « Trace ça » / « Tableau de bord pour X » | `front-ui` | Spec Vega-Lite v5 JSON + wrapper `<figure>`. Style maison, palette de `color-psychology.md`, axes avec polarité, `role="img"`. |
| Une page HTML existante ou une capture d'écran | « Audite » / « Vérif WCAG » / « Rends ça moins IA » | `front-ui` (anti-patterns, ergonomie) + `front-a11y` (lint, contraste, daltonisme) | Constats au regard des 8 critères ergonomiques + catalogue d'anti-patterns ; diffs concrets ; checklist pré-livraison ; sorties `lint_a11y` + `audit_contrast` + `simulate_cvd`. |
| Une image (`*.png`, `*.jpg`, …) | « Texte alternatif pour cette image » | `front-a11y` | Texte alternatif conforme W3C dans la bonne catégorie (informatif / décoratif / fonctionnel / texte / complexe / groupe), rédigé dans la langue de la page, marqué `data-alt-source="ai"`. |
| Un fichier audio ou vidéo (`.mp4`, `.wav`, `.mp3`, …) — **WiP** | « Sous-titres / transcription » | `front-a11y` *(en travaux)* | Sous-titres WebVTT / SRT / texte brut depuis whisper.cpp local, avec biais de vocabulaire issu du projet. Extrait `<video>` + `<track kind="captions">` à coller. Le script et les tests sont là aujourd'hui ; les baselines WER par langue et le clip de référence pour le biais de vocabulaire sont encore à collecter — voir [État d'avancement](#état-davancement). |
| Un logo (`logo.png` / `.svg`) | « Jeu de favicons » / « Icônes PWA » | `front-publish` | `favicon.svg` + `.ico` + lot de PNG + `apple-touch-icon.png` + icône PWA masquable + `site.webmanifest` + extrait `head.html`. |
| Une description d'objectif ou une page HTML | « Meta tags » / « SEO » / « OG card » / « GEO » / « llms.txt » / « AI Overview » | `front-publish` | **Pour le SEO :** titre + description + Open Graph + Twitter Card + JSON-LD Schema.org (JSON sur stdout) — voir [les trois piliers de Google Search Essentials](https://developers.google.com/search/docs/essentials) appliqués dans `front-publish/references/seo-essentials.md`. **Pour le GEO** (Generative Engine Optimization — surfaces de réponses AI Overview / Gemini / ChatGPT) : `llms.txt` est émis par `scripts/site_indexes.py` aux côtés de `robots.txt` + `sitemap.xml` + Atom/RSS, donc le site embarque un résumé Markdown lisible par les LLM dès qu'une commande « transforme ce dossier en site » se termine. Mêmes robots, mêmes permissions dans `robots.txt` — aucune balise meta « AI » n'existe ; toute affirmation contraire est fausse. |
| Du copy d'IHM brut | « Langage clair » / « Réécris au niveau 6e » | `front-publish` | Même sens, voix marketing retirée, longueur de sortie ≤ 1,1× l'original. |
| Une palette JSON | « Audit de contraste » / « Ma palette est-elle accessible ? » | `front-a11y` | Chaque paire `(label, surface)` parcourue, échecs listés avec la correction OKLCH voisine la plus proche. Sortie 1 sur échec. |
| Une page finalisée / capture d'écran | « Vérif pré-livraison » | `front-ui` + `front-a11y` | La porte `checklist.md` exécutée ; lint + contraste + daltonisme passent ; copy / animation / performance vérifiés. |

> Pas sûr quelle ligne correspond ? Décrivez l'entrée en français courant. L'arbre de décision de chaque `SKILL.md` mappe les formulations vers les workflows.

## Installation

Les skills suivent la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
et sont lus nativement par **Claude Code** et **OpenCode**. N'installez
que ceux qui vous servent.

### Claude Code

Installation depuis une release GitHub taguée. Cela épingle une
version, vérifie la somme de contrôle et garantit un jeu de règles
stable qui ne dérive pas entre deux mises à jour.

```bash
# 1. Téléchargez une release taguée
VERSION=0.6.4
curl -L -o front-skills.tar.gz \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/front-skills-${VERSION}.tar.gz
curl -L -o SHA256SUMS \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/SHA256SUMS

# 2. Vérifiez la somme de contrôle (macOS : shasum ; Linux : sha256sum)
shasum -a 256 -c SHA256SUMS    # ou : sha256sum -c SHA256SUMS

# 3. Extrayez et installez ceux dont vous avez besoin
tar xzf front-skills.tar.gz
mkdir -p ~/.claude/skills
cp -r front-ui      ~/.claude/skills/   # toujours
cp -r front-cli-gui ~/.claude/skills/   # uniquement si vous habillez des CLI
cp -r front-publish ~/.claude/skills/   # uniquement pour les sites de doc
cp -r front-a11y    ~/.claude/skills/   # uniquement pour les portes a11y
```

Vérifier l'installation sur disque :

```bash
ls ~/.claude/skills/front-ui/SKILL.md
```

Vérifier que les SKILL.md sont valides (vrai YAML, `name` aligné sur
le dossier, description dans la plage Anthropic 50–1024 caractères) :

```bash
# À lancer une fois depuis un clone du dépôt (stdlib + PyYAML)
python3 scripts/validate_all.py
```

Si vous n'avez besoin que d'un seul skill, téléchargez sa tarball
unitaire (par exemple `front-a11y-${VERSION}.tar.gz`) plutôt que le
bundle. Chaque release publie les tarballs unitaires en plus du
bundle, et le même `SHA256SUMS` couvre l'ensemble.

Claude Code lit la description du frontmatter de chaque skill et active
le bon dès qu'un message correspond à ses phrases déclencheuses.

### OpenCode

[OpenCode](https://opencode.ai) est un agent de code en terminal, open
source, qui sait piloter Claude, GPT et des modèles locaux derrière la
même expérience. Le flux ci-dessus s'applique tel quel — extrayez le
bundle, puis :

```bash
mkdir -p ~/.opencode/skills
cp -r front-* ~/.opencode/skills/
```

À privilégier si vous voulez l'expérience des skills sans dépendance à
un fournisseur unique, ou si OpenCode est déjà votre outil quotidien.

### Installation depuis les sources (contributeur / développeur)

Pour itérer sur les skills eux-mêmes, ou pour épingler un commit qui
n'est pas encore tagué, clonez et copiez directement. Pas de
vérification de somme de contrôle ici — c'est à vous de garantir que
vous avez bien cloné le commit voulu.

```bash
git clone https://github.com/warith-harchaoui/front.git
cd front
python3 -m pip install -r requirements-dev.txt   # PyYAML + pytest
python3 -m pytest                                # 420+ tests déterministes
python3 scripts/validate_all.py                  # 4 skills × YAML + contenu
mkdir -p ~/.claude/skills
cp -r front-ui      ~/.claude/skills/            # toujours
cp -r front-a11y    ~/.claude/skills/            # compagnons optionnels
```

`CONTRIBUTING.md` reprend le même flux côté contributeur.

### Mise à jour

Pour mettre à jour, recommencez la procédure release avec une
`VERSION` plus récente. Le nom du dossier installé est stable, donc
`cp -r front-ui ~/.claude/skills/` écrase l'install précédente sur
place. Le `SHA256SUMS` de chaque release fait foi : si la vérification
échoue, n'installez pas l'artefact.

### Modèle de confiance

En bref : le dépôt livre du texte et des scripts Python qui se lisent
de haut en bas en moins d'une heure. **Les releases taguées portent
des sommes de contrôle SHA-256** (intégrité contre la corruption en
transit) ; elles ne sont **pas signées GPG** ni attestées Sigstore
aujourd'hui. Si vous avez besoin d'authenticité au-delà d'une preuve
d'intégrité, construisez à partir d'un commit tagué que vous avez
relu vous-même — `scripts/release.sh` est dans l'arbre et reproductible,
et le workflow `release.yml` ne fait rien que le script ne fasse en
local. Voir [`SECURITY.md`](SECURITY.md) pour la note complète
chaîne d'approvisionnement.

### Complétion shell

Le pilote `front` (et les quatre CLI par-script migrés à Click —
`alt_from_ollama.py`, `captions_from_whisper.py`,
`meta_from_ollama.py`, `plain_language.py`) embarquent la complétion
`bash` / `zsh` / `fish` gratuitement via l'astuce
`_<OUTIL>_COMPLETE=<shell>_source` de Click. Voir
[`front-cli/README.md`](front-cli/README.md#shell-completion) pour la
mise en place en une ligne par shell. Le même motif marche pour les
CLI par-script lancés directement (par exemple
`_ALT_FROM_OLLAMA_COMPLETE=zsh_source alt_from_ollama.py`).

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
├── LICENSE.md                          ← The Unlicense (OFL pour Roboto / Roboto Serif / Roboto Mono)
├── llms.txt                            ← index https://llmstxt.org/ pour les LLM
├── pytest.ini, requirements-dev.txt    ← outillage dev partagé
├── tests/                              ← suite pytest partagée pour les quatre skills
├── assets/logo.png                     ← logo du projet
│
├── front-ui/                           ← skill de génération d'UI
│   ├── SKILL.md
│   ├── references/                     ← couleur, pile, composants, dataviz, design system, checklist
│   ├── scripts/                        ← validate.py (stdlib uniquement)
│   └── assets/                         ← starter-page, composants, les trois polices Roboto (sans / serif / mono)
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
frontend : JavaScript pur, Tailwind CSS, et la règle des trois Roboto
(Roboto / Roboto Serif / Roboto Mono). Conformes à la
[spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Un grand merci à
**[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**,
**[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** et
**[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)**
pour nos discussions fructueuses.

Palettes de couleurs issues de <https://harchaoui.org/warith/colors/>.

Les trois familles Roboto sont livrées dans
`front-ui/assets/fonts/roboto/`, `front-ui/assets/fonts/roboto-serif/`
et `front-ui/assets/fonts/roboto-mono/`, chacune sous SIL Open Font
License — voir le fichier `OFL.txt` joint dans chaque dossier.

Le skill puise également des connaissances dans les
[Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
et [Google Material Design](https://material.io/design).

## Licence

**The Unlicense** — code publié dans le domaine public, sans
copyright ni restrictions. Vous pouvez l'utiliser, le modifier, le
redistribuer ou le vendre, sans permission, attribution ni redevance.
Voir `LICENSE.md` pour le texte canonique. Les trois familles Roboto
(Roboto, Roboto Serif, Roboto Mono) restent sous SIL Open Font License
(voir le `OFL.txt` joint dans chaque dossier
`front-ui/assets/fonts/roboto*/`) — la dédicace au domaine public ne
change pas ce point.

**Licence vs. attribution.** Le code est publié sous l'Unlicense
(domaine public — aucune autorisation requise pour l'utiliser, le
forker, le modifier ou le re-marquer). Les crédits d'auteur dans la
documentation sont une reconnaissance volontaire, pas une exigence de
licence. Vous êtes libre de les retirer ou de les remplacer dans votre
fork.
