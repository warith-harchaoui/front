


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
| **front-accessibility** | Vous avez besoin de lint a11y statique. | « lint a11y », « vérif accessibilité HTML », « contrôle a11y statique », « lint WCAG-friendly », « a11y pre-commit ». |
| **front-colors** | Vous auditez le contraste, simulez le daltonisme, ou voulez une palette curatée avec éclaircissement / assombrissement perceptuels. | « vérif WCAG », « audit de contraste », « ma palette est-elle accessible », « aperçu daltonien », « deutéranope », « CVD », « OKLCH », « éclaircis cette couleur ». |
| **front-vision** | Vous draftez du texte alternatif conforme W3C depuis des images, en local (pas de SaaS). | « texte alternatif », « décris cette image », « draft alt », « description d'image », « img sans alt ». |
| **front-audio** | Vous draftez des sous-titres WebVTT / SRT pour `<video>` / `<audio>` en local (pas de SaaS). | « sous-titres », « transcris cette vidéo », « transcris cet audio », « WebVTT », « SRT », « fichier de sous-titres », « VTT », « piste sous-titres ». |
| **front-ux-laws** | Vous voulez un vocabulaire partagé pour vos décisions d'UI ET un auditeur pre-commit qui échoue sur les violations détectables des Laws of UX (Hick, Fitts, Miller, Jakob, Tesler, Aesthetic-Usability, Selective Attention, Doherty, Choice Overload). | « Laws of UX », « Hick / Fitts / Miller / Jakob / Tesler / Peak-End / Postel / Paradox of the Active User », « audite ma nav / mon formulaire / ma page de prix », « cet onboarding combat-il l'utilisateur actif ». |
| **front-figures** | Vous produisez des figures pour la data-science (Vega-Lite / matplotlib), des plots d'explicabilité de modèle (SHAP / Shapash / TimeSHAP / LIME), ou des estimations d'effet causal (DoWhy / EconML) — et voulez un auditeur pre-commit qui échoue sur les fautes de data-viz. | « chart this », « make a figure », « SHAP plot », « explain this model », « feature importance », « shapash », « timeshap », « LIME », « causal inference », « DoWhy », « EconML », « treatment effect », « DAG », « audit this figure », « dual y-axis ». |

Les skills compagnons héritent des règles de pile de `front-ui`.
N'installez que ceux dont vous avez besoin.

> **Quelle phrase déclenche quel skill ?** Voir
> [`TRIGGERS.md`](TRIGGERS.md) — généré depuis chaque `SKILL.md`,
> liste toutes les phrases garanties par leur description avec le
> skill qu'elles activent.

## Deux modes — make et audit

Chaque skill front-* appartient à l'une (ou aux deux) moitiés d'une
seule boucle : **make** (produire l'artefact) et **audit** (le
vérifier). Le tableau indique quand charger chaque skill et ce qui
reste en feuille de route.

| Skill | Make (générer) | Audit (porte) |
|---|---|---|
| **front-ui** | `references/` + `assets/components/` — playbook de génération HTML / Tailwind / dataviz | `scripts/validate.py`, `references/checklist.md`, `anti-patterns.md`, `ergonomics-criteria.md` |
| **front-cli-gui** | `scripts/cli_to_gui.py` (émetteur CLI → HTML — adaptateurs argparse + Click + `--from-help`) + `assets/examples/cli-gui-demo/` (scaffold exécutable) | Accouplez `front-accessibility` + `front-ux-laws` sur le HTML produit (l'émetteur est son propre client — sa sortie passe les deux audits avec zéro finding). |
| **front-publish** | `favicons.py`, `meta_from_ollama.py`, `site_indexes.py`, `plain_language.py`, `md_to_html.py`, `narrate.py` | `lint_markdown.py` |
| **front-accessibility** | _(rien — voir `front-ui` pour les templates, `front-vision` pour les alt, `front-audio` pour les sous-titres)_ | `lint_a11y.py` (14 règles, stdlib seul) |
| **front-colors** | `palette_to_tailwind.py` (CSV → tailwind.config.js) | `audit_contrast.py`, `simulate_cvd.py` |
| **front-vision** | `alt_from_ollama.py` (alt W3C via Ollama local) | _(présence de `alt=` vérifiée par `front-accessibility`)_ |
| **front-audio** | `captions_from_whisper.py` (WebVTT / SRT via whisper.cpp local) | _(présence de `<track>` vérifiée par `front-accessibility`)_ |
| **front-ux-laws** | `references/laws-of-ux.md` (playbook des 30 lois) | `audit_laws_of_ux.py` (Hick / Miller / Fitts / Jakob / Tesler / …) |
| **front-figures** | `make_figure.py` (CSV → Vega / matplotlib), `explain_model.py` (dispatcher SHAP / Shapash / TimeSHAP / LIME), `causal_estimate.py` (boucle DoWhy + backends EconML + rendu DAG), `install_figures.py` (installeur par tier) | `audit_figure.py` (missing-axis-title, dual-y-axis, truncated-baseline, pie-3d, rainbow-palette, cvd-unsafe, missing-polarity, chartjunk, role-img-missing) |

Le tableau est honnête sur les manques. Les cellules vides marquent
de vraies entrées de roadmap, pas des oublis.

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
   interne, sans chaîne de build. Les portes a11y (`front-accessibility`)
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

Photographie de l'état de chaque surface à `v0.9.0`. Les huit dossiers
de skills sont stables ; la seule zone en travaux est l'**audio /
sous-titres** (front-audio, vidéo → texte). La **narration audio**
(front-publish, texte → audio) est stable et explicitement encadrée
comme amélioration éditoriale optionnelle, pas exigence WCAG.

| Domaine | État | Notes |
|---|---|---|
| `front-ui` (règles de pile, tokens, composants, dataviz, checklist) | Stable | Les 9 règles dures documentées ; `validate.py` stdlib uniquement ; couvert par `tests/test_validate.py`. |
| `front-cli` (pilote `front` unifié, complétion shell) | Stable | Basé sur Click ; transmission du `--help` corrigée en 0.3.0 (test de non-régression en 0.3.1). |
| `front-cli-gui` (CLI → IHM, phare) | Stable (skill + démo exécutable) | `assets/examples/cli-gui-demo/` tourne de bout en bout. Durcissement production (auth, rate-limit, sandbox) délibérément laissé à l'hôte. |
| `front-publish` (site Markdown, meta, favicons, indexes, langage clair, narration audio) | Stable | 11 scripts publics couvrant les quatre artefacts cœur (favicons, meta, indexes, langage clair) + Markdown → HTML + lint Markdown + pipeline narration audio (orchestrateur, wrappers OpenVoice et Chatterbox, sélecteur de voix, installeur). Couverture déterministe large (favicons, site-indexes, meta, langage clair, lint, narration) ; suite d'éval pour meta + langage clair. Surcharge `FRONT_LANG_PAIR` câblée. |
| `front-accessibility` — lint | Stable (renommé depuis `front-a11y` en 0.9.0) | Lint a11y statique 14 règles, stdlib uniquement. Désormais resserré au lint après les sorties color / vision / audio. |
| `front-colors` — audit contraste, simulation CVD, palette curatée, éclaircissement / assombrissement perceptuels | Stable (nouveau en 0.7.0) | Correcteur de contraste par voisin OKLCH, matrices CVD de Machado, CSV palette unifiée (base Apple + projections émotion / concept / psychologie), module `_colors` stdlib uniquement, classe `Color`. Sorti de `front-accessibility` pour un périmètre plus clair. |
| `front-vision` — texte alternatif W3C via vision Ollama locale | Stable (nouveau en 0.8.0) | Modèle par défaut `gemma4:e4b` (variante `-mlx` auto-sélectionnée sur Apple silicon). Arbre de décision par objectif, biais par texte environnant + vocabulaire projet, cache disque. Sorti de `front-accessibility` pour un périmètre plus clair. Éval texte alternatif sur fixtures Wikipedia. |
| `front-audio` — **sous-titres WebVTT / SRT via whisper.cpp local** | **WiP / TODO** (sorti en 0.9.0) | `captions_from_whisper.py` est fonctionnel ; ce qui manque, ce sont les baselines WER par langue (`en` / `fr` / `es` câblés via l'extracteur, baselines pas encore publiées), le clip utilisateur `vocab-biasing-clip.wav`, et une révision prévue de l'intégration whisper.cpp via `pdbms`. Voir [Roadmap](CHANGELOG.md#roadmap). |
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
| Une page HTML existante ou une capture d'écran | « Audite » / « Vérif WCAG » / « Rends ça moins IA » | `front-ui` (anti-patterns, ergonomie) + `front-accessibility` (lint) + `front-colors` (contraste, daltonisme) | Constats au regard des 8 critères ergonomiques + catalogue d'anti-patterns ; diffs concrets ; checklist pré-livraison ; sorties `lint_a11y` + `audit_contrast` + `simulate_cvd`. |
| Une image (`*.png`, `*.jpg`, …) | « Texte alternatif pour cette image » | `front-vision` | Texte alternatif conforme W3C dans la bonne catégorie (informatif / décoratif / fonctionnel / texte / complexe / groupe), rédigé dans la langue de la page, marqué `data-alt-source="ai"`. |
| Un fichier audio ou vidéo (`.mp4`, `.wav`, `.mp3`, …) — **WiP** | « Sous-titres / transcription » | `front-audio` *(en travaux)* | Sous-titres WebVTT / SRT / texte brut depuis whisper.cpp local, avec biais de vocabulaire issu du projet. Extrait `<video>` + `<track kind="captions">` à coller. Le script et les tests sont là aujourd'hui ; les baselines WER par langue et le clip de référence pour le biais de vocabulaire sont encore à collecter — voir [État d'avancement](#état-davancement). |
| Un logo (`logo.png` / `.svg`) | « Jeu de favicons » / « Icônes PWA » | `front-publish` | `favicon.svg` + `.ico` + lot de PNG + `apple-touch-icon.png` + icône PWA masquable + `site.webmanifest` + extrait `head.html`. |
| Une description d'objectif ou une page HTML | « Meta tags » / « SEO » / « OG card » / « GEO » / « llms.txt » / « AI Overview » | `front-publish` | **Pour le SEO :** titre + description + Open Graph + Twitter Card + JSON-LD Schema.org (JSON sur stdout) — voir [les trois piliers de Google Search Essentials](https://developers.google.com/search/docs/essentials) appliqués dans `front-publish/references/seo-essentials.md`. **Pour le GEO** (Generative Engine Optimization — surfaces de réponses AI Overview / Gemini / ChatGPT) : `llms.txt` est émis par `scripts/site_indexes.py` aux côtés de `robots.txt` + `sitemap.xml` + Atom/RSS, donc le site embarque un résumé Markdown lisible par les LLM dès qu'une commande « transforme ce dossier en site » se termine. Mêmes robots, mêmes permissions dans `robots.txt` — aucune balise meta « AI » n'existe ; toute affirmation contraire est fausse. |
| Du copy d'IHM brut | « Langage clair » / « Réécris au niveau 6e » | `front-publish` | Même sens, voix marketing retirée, longueur de sortie ≤ 1,1× l'original. |
| Une palette JSON | « Audit de contraste » / « Ma palette est-elle accessible ? » | `front-colors` | Chaque paire `(label, surface)` parcourue, échecs listés avec la correction OKLCH voisine la plus proche. Sortie 1 sur échec. |
| Une page finalisée / capture d'écran | « Vérif pré-livraison » | `front-ui` + `front-accessibility` + `front-colors` | La porte `checklist.md` exécutée ; lint + contraste + daltonisme passent ; copy / animation / performance vérifiés. |

> Pas sûr quelle ligne correspond ? Décrivez l'entrée en français courant. L'arbre de décision de chaque `SKILL.md` mappe les formulations vers les workflows.

## Installation

Les skills suivent la [spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
et sont lus nativement par **Claude Code** et **OpenCode**. N'installez
que ceux qui vous servent.

Les flux Claude Code et OpenCode sont **identiques sauf pour le
dossier d'install** — les deux runtimes lisent les `SKILL.md` dans
un dossier par skill, et les mêmes tarballs servent les deux. La
procédure ci-dessous montre une voie ; le second runtime est une
substitution d'une ligne.

> **Variables partagées.** Remplacez `<RUNTIME>` par `claude` ou
> `opencode`. Épinglez `VERSION` sur la dernière tag — voir
> [releases](https://github.com/warith-harchaoui/front/releases).

### 1. Téléchargez une release taguée (somme de contrôle vérifiée)

```bash
VERSION=0.15.1
curl -L -o front-skills.tar.gz \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/front-skills-${VERSION}.tar.gz
curl -L -o SHA256SUMS \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/SHA256SUMS

# macOS : shasum -a 256 -c SHA256SUMS
# Linux : sha256sum -c SHA256SUMS
shasum -a 256 -c SHA256SUMS

tar xzf front-skills.tar.gz
```

Si vous n'avez besoin que d'un seul skill, remplacez le bundle par
une tarball unitaire (par exemple `front-accessibility-${VERSION}.tar.gz`).
Le même `SHA256SUMS` couvre tous les artefacts.

### 2. Copiez dans le dossier skills du runtime

Choisissez **un** runtime :

```bash
# Claude Code :
RUNTIME=claude   # → ~/.claude/skills/
# OpenCode :
RUNTIME=opencode # → ~/.opencode/skills/

mkdir -p ~/.${RUNTIME}/skills
cp -r front-ui            ~/.${RUNTIME}/skills/   # toujours
cp -r front-cli-gui       ~/.${RUNTIME}/skills/   # uniquement si vous habillez des CLI
cp -r front-publish       ~/.${RUNTIME}/skills/   # uniquement pour les sites de doc
cp -r front-accessibility ~/.${RUNTIME}/skills/   # uniquement pour lint a11y statique
cp -r front-colors        ~/.${RUNTIME}/skills/   # uniquement pour contraste WCAG / CVD / palette
cp -r front-vision        ~/.${RUNTIME}/skills/   # uniquement pour alt text (Ollama local)
cp -r front-audio         ~/.${RUNTIME}/skills/   # uniquement pour sous-titres (whisper.cpp local)
cp -r front-ux-laws       ~/.${RUNTIME}/skills/   # uniquement pour l'audit Laws-of-UX
cp -r front-figures       ~/.${RUNTIME}/skills/   # uniquement si vous produisez des figures dataviz / SHAP / DoWhy
```

Installez dans **les deux** runtimes si vous alternez entre eux —
même dossier copié dans deux chemins.

### 3. Vérifiez

```bash
# Un skill est installé et son SKILL.md est sur disque :
ls ~/.${RUNTIME}/skills/front-ui/SKILL.md

# Optionnel — si vous avez aussi cloné le dépôt, vérifiez chaque
# skill installé contre la spécification Anthropic (stdlib + PyYAML,
# pas de réseau) :
python3 scripts/validate_all.py
```

Le runtime lit la description du `SKILL.md` de chaque skill au
démarrage de la conversation ; les phrases correspondantes activent
automatiquement le skill. Voir [`TRIGGERS.md`](TRIGGERS.md) pour
l'index par phrase.

### Nettoyage — retirer les skills obsolètes ou renommés

Si vous aviez installé une ancienne version, votre dossier
`~/.${RUNTIME}/skills/` peut contenir des dossiers orphelins issus
de renommages passés (par exemple `front-a11y/` d'avant le rename
v0.9.0 vers `front-accessibility`). Lancez l'aide pour les détecter
et les retirer :

```bash
# Audit seul (liste les dossiers orphelins ; ne supprime jamais) :
python3 scripts/cleanup_local_skills.py

# Appliquer : demande confirmation par dossier avant suppression.
python3 scripts/cleanup_local_skills.py --apply
```

L'outil vérifie `~/.claude/skills/` et `~/.opencode/skills/` contre
le manifeste canonique [`SKILLS.txt`](SKILLS.txt) et signale tout
dossier `front-*` qui n'est plus livré par ce dépôt.

### Mise à jour

Recommencez les étapes 1–3 avec la nouvelle `VERSION`. Le nom du
dossier installé est stable, donc chaque `cp -r` écrase l'install
précédente sur place — pas de suppression manuelle entre versions,
sauf quand un skill est **renommé** (utilisez l'aide de nettoyage
ci-dessus dans ce cas). Les renommages sont listés dans
[`CHANGELOG.md`](CHANGELOG.md).

### Installation depuis les sources (contributeur / développeur)

Pour itérer sur les skills, ou pour épingler un commit qui n'est
pas encore tagué, clonez et copiez depuis l'arbre de travail. Pas
de vérification de somme de contrôle — c'est à vous de garantir
le bon commit cloné.

```bash
git clone https://github.com/warith-harchaoui/front.git
cd front
python3 -m pip install -r requirements-dev.txt   # PyYAML + pytest
python3 -m pytest                                # suite complète déterministe
python3 scripts/validate_all.py                  # tous les 8 skills, YAML + contenu

# Reflète l'étape 2 ci-dessus :
RUNTIME=claude   # ou opencode
mkdir -p ~/.${RUNTIME}/skills
for skill in $(grep -v '^[[:space:]]*#' SKILLS.txt | grep -v '^[[:space:]]*$'); do
    cp -r "$skill" ~/.${RUNTIME}/skills/
done
```

`CONTRIBUTING.md` reprend le même flux côté contributeur.

### OpenCode + Ollama local — l'approche zéro token

[OpenCode](https://opencode.ai) est le second runtime supporté —
et le compagnon naturel d'un workflow **entièrement local, sans
token**. OpenCode est agnostique au modèle : pointez-le sur un
daemon [Ollama](https://ollama.com) local et vous obtenez le même
comportement de skills que Claude Code, avec deux différences
concrètes :

- **Pas de tokens d'API.** Rien ne quitte la machine ; rien ne
  facture.
- **Pas de quota d'usage.** Lancez la boucle toute la nuit sur un
  long batch sans surveiller un compteur.

Le compromis est la qualité du modèle. Un modèle local de 7-13 B
est en-dessous de Claude / GPT-4 sur le raisonnement difficile ;
les skills front-* compensent parce qu'ils chargent l'*opinion* en
amont (règles de pile, audits, phrases déclencheuses) — le modèle
n'a plus qu'à suivre un script, pas à l'inventer. Pour le travail
UI, l'alt text, les sous-titres, les audits de contraste, les
checks Laws of UX, la voie locale est aujourd'hui réellement
utilisable.

L'ajustement avec ce dépôt est direct : **trois skills front-*
parlent déjà à un daemon Ollama local** pour leurs surfaces IA —
`front-vision` (alt text, `gemma4:e4b`),
`front-publish/meta_from_ollama.py` (meta de page),
`front-publish/plain_language.py` (réécriture de copie). Quand vous
lancez OpenCode contre le même daemon Ollama, toute la boucle —
agent + scripts pilotés par les skills — utilise un seul modèle
local. Zéro appel externe.

```bash
# Démarrage rapide. Suppose Ollama + un binaire OpenCode dans le PATH.
ollama serve &                                # démarrer le daemon
ollama pull gemma4:e4b-mlx                    # Apple Silicon
# Linux / Windows : ollama pull gemma4:e4b
```

Un seul modèle pour toute la pile : il pilote la boucle d'agent
OpenCode ET sert tous les scripts front-* basés Ollama
(`alt_from_ollama`, `meta_from_ollama`, `plain_language`,
`narrate_post`). Même daemon, même tag, même réponse à « quel
modèle tourne ? » — `gemma4:e4b`.

#### Câbler OpenCode sur le daemon Ollama local (config unique)

Le provider `ollama` livré avec OpenCode pointe par défaut sur
Ollama Cloud. Pour viser votre daemon **local**, ajoutez un
provider `local-ollama` à `~/.config/opencode/opencode.jsonc`
(le fichier existe déjà ; seule la clé `provider` est nouvelle) :

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local-ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b-mlx":       { "name": "gemma4:e4b-mlx (local)" },
        "gemma4:e4b":           { "name": "gemma4:e4b (local)" }
      }
    }
  }
}
```

Ollama expose un endpoint compatible OpenAI sur
`http://localhost:11434/v1`, que le provider
`@ai-sdk/openai-compatible` parle nativement — pas de plugin à
installer en plus de la config. Listez exactement les tags que
vous avez pull-és (faites `ollama list` pour les voir) ;
OpenCode ne les découvre pas automatiquement.

Puis lancez OpenCode sur le provider local :

```bash
# Apple Silicon — la variante -mlx tourne plus vite :
opencode run "construis-moi un bouton CTA principal" \
    -m local-ollama/gemma4:e4b-mlx

# Linux / Windows ou matériel non-MLX :
opencode run "construis-moi un bouton CTA principal" \
    -m local-ollama/gemma4:e4b

# → ~/.opencode/skills/front-* se chargent automatiquement.
# → Les scripts front-vision / front-publish basés Ollama
#   tapent dans le même daemon pour leurs traitements.
# → Coût : 0 token ; rien ne quitte la machine.
```

Si vous préférez un modèle entraîné pour le code côté agent et
réservez `gemma4:e4b` aux traitements des scripts, le motif via
variables d'environnement (documenté plus haut —
`OLLAMA_MODEL_BASE=gemma4:e4b` pour les scripts,
`-m local-ollama/qwen2.5-coder:latest` pour l'agent) sépare les
rôles proprement. Le tableau « Configurer les scripts des skills »
ci-dessus est la référence.

#### Configurer les scripts des skills (même daemon, variables séparées)

OpenCode pilote l'agent ; les scripts des skills qui parlent
*aussi* à Ollama (alt text, meta tags, langage clair, narration
audio) lisent leurs propres variables d'environnement. **Aucun
chevauchement avec `OPENCODE_MODEL`** — réglez les deux ; les deux
doivent pointer sur le même daemon, mais le modèle peut différer :

| Variable | Lue par | Effet | Défaut |
|---|---|---|---|
| `OLLAMA_URL` | tout script basé Ollama | URL du daemon. Doit correspondre à celui d'OpenCode. | `http://localhost:11434` |
| `OLLAMA_MODEL` | tout script basé Ollama | Tag exact à utiliser (prioritaire sur l'auto-MLX). | _(non défini)_ |
| `OLLAMA_MODEL_BASE` | `alt_from_ollama.py`, `meta_from_ollama.py`, `narrate_post.py` | Tag de base ; `-mlx` auto-ajouté sur Apple Silicon. | `gemma4:e4b` |
| `FRONT_LANG_PAIR` | tout script gérant la langue | Première entrée = `--lang` par défaut si pas de flag. | `en,fr` |
| `OPENCODE_MODEL` | OpenCode lui-même | Tag du modèle côté agent. Indépendant des scripts. | _(défini par OpenCode)_ |

Le motif honnête : gardez `OLLAMA_URL` identique des deux côtés ;
laissez chaque côté choisir son modèle. L'agent bénéficie d'un
modèle entraîné pour le code (Qwen 2.5 Coder, DeepSeek-Coder) ; le
script de vision a besoin d'un multimodal (Gemma 4) ; le
réécriveur en langage clair fonctionne avec l'un comme l'autre.

```bash
# Même daemon des deux côtés ; modèle différent par préoccupation.
export OLLAMA_URL=http://localhost:11434
export OPENCODE_MODEL=qwen2.5-coder:7b
export OLLAMA_MODEL_BASE=gemma4:e4b   # ↰ vision / meta / narration
```

Choisissez OpenCode quand les coûts de tokens comptent, quand le
travail est en masse / répétitif (alt-texter une bibliothèque de
500 images, regénérer les meta tags à chaque commit, auditer un
site de 50 pages), ou quand la donnée ne doit pas quitter la
machine. Choisissez Claude Code quand le travail demande le
jugement d'un modèle frontière (synthèse design originale,
refactos ambigus, revue de code d'une bibliothèque inconnue).

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

## Hooks pre-commit

Le dépôt fournit un manifeste `.pre-commit-hooks.yaml` à la racine,
donc n'importe quel projet peut câbler les portes d'audit front-*
dans [pre-commit](https://pre-commit.com/) avec un seul bloc `repo:`
— sans chemins de scripts en dur, sans installation au-delà de
`pre-commit install`.

```yaml
# .pre-commit-config.yaml — ajouter le dépôt en une entrée
repos:
  - repo: https://github.com/warith-harchaoui/front
    rev: v0.12.0          # fixer une tag — bumper via renovate / dependabot
    hooks:
      - id: front-accessibility-lint
      - id: front-ux-laws-audit
      - id: front-publish-lint-markdown
      - id: front-ui-validate-skill   # uniquement si vous livrez des skills
      # Ajoutez --fix en hook arg pour activer les auto-correctifs sûrs
      # ex. - id: front-ux-laws-audit
      #        args: [--fix]
```

Les hooks sont stdlib-only côté Python (pre-commit installe chacun
dans son propre venv isolé). Les deux hooks couleur déclarent Pillow
via `additional_dependencies`. Chaque hook respecte le filtre de type
de fichier transmis par pre-commit (HTML pour les hooks a11y + Laws
of UX ; Markdown pour le hook publish).

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
├── LICENSE.md                          ← BSD-3-Clause (OFL pour Roboto / Roboto Serif / Roboto Mono)
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
├── front-accessibility/                ← lint a11y HTML statique
│   ├── SKILL.md
│   ├── references/                     ← lint-a11y
│   └── scripts/                        ← lint_a11y.py
│
├── front-colors/                       ← audit contraste + simulation CVD + palette curatée
│   ├── SKILL.md
│   ├── references/                     ← contrast-audit, cvd-simulation, palette.csv
│   └── scripts/                        ← audit_contrast.py, simulate_cvd.py, _colors.py
│
├── front-vision/                       ← texte alternatif W3C via vision Ollama locale
│   ├── SKILL.md
│   ├── references/                     ← alt-text-ai
│   └── scripts/                        ← alt_from_ollama.py, install_alt_ai.py, prompts/
│
└── front-audio/                        ← sous-titres WebVTT / SRT via whisper.cpp local
    ├── SKILL.md
    ├── references/                     ← captions-ai
    └── scripts/                        ← captions_from_whisper.py, install_captions.py
```

## Auteur

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

Quatre petits **skills** Claude / OpenCode pour une seule pile
frontend : JavaScript pur, Tailwind CSS, et la règle des trois Roboto
(Roboto / Roboto Serif / Roboto Mono). Conformes à la
[spécification Anthropic des skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Un grand merci à
**[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**,
**[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)**,
**[Auguste Baum](https://www.linkedin.com/in/auguste-baum/)** et
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

**BSD-3-Clause** — la même licence que **scikit-learn**. Permissive :
utilisation, modification, redistribution, vente, intégration dans des
produits commerciaux. Les trois conditions sont (1) conserver la notice
de copyright dans les redistributions de code source, (2) la reproduire
dans la documentation des distributions binaires, (3) ne pas utiliser
le nom du détenteur du copyright pour endosser des produits dérivés
sans autorisation. Voir `LICENSE.md` pour le texte canonique. Les
trois familles Roboto (Roboto, Roboto Serif, Roboto Mono) restent sous
SIL Open Font License (voir le `OFL.txt` joint dans chaque dossier
`front-ui/assets/fonts/roboto*/`) — la licence BSD-3-Clause ci-dessus
s'applique au code source, pas aux polices.

**Licence vs. attribution.** Les crédits d'auteur dans la documentation
sont une reconnaissance volontaire (pas la condition #3 de la licence).
Vous êtes libre de les retirer ou de les remplacer dans votre fork ;
les obligations BSD-3-Clause ci-dessus sont ce qui voyage avec le code.
