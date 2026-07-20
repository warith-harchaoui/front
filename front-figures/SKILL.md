---
name: front-figures
description: >-
  Data-science figures for vanilla-JS + Tailwind, both make and audit —
  publication-quality matplotlib / seaborn plots, Vega-Lite JSON in the
  front-ui house style, model-explainability plots via SHAP / Shapash /
  TimeSHAP / LIME, causal-effect estimation and DAG rendering via DoWhy /
  EconML, and a static auditor that flags data-viz sins (missing axis labels,
  dual y-axes, truncated baselines, 3D pies, rainbow palettes, CVD-unsafe
  hues, chartjunk, undeclared polarity). Deterministic auditor, local-first
  make side. Trigger phrases: "chart this", "make a figure", "SHAP plot",
  "explain this model", "feature importance", "shapash", "timeshap", "LIME",
  "causal inference", "DoWhy", "EconML", "treatment effect", "refute",
  "refutation", "DAG", "audit this figure", "colorblind safe palette", "dual
  y-axis", "bar / line / scatter chart", "Vega-Lite", "visualize data", "audit
  this chart", "install figures". Output: Vega JSON / PNG / SVG on disk +
  an HTML figure snippet; auditor emits JSON + exit codes for CI.
license: BSD-3-Clause
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. The auditor (static) needs
  Python 3.10+ stdlib + PyYAML only. The generators need Python 3.10+
  plus the tiered dependencies pinned in ``scripts/requirements-*.txt``
  — one per concern (dataviz, explainability, causality). The
  ``install_figures.py`` script installs each tier on demand. No
  network required at figure-generation time once installed.
metadata:
  author: Warith Harchaoui
  version: 0.26.0
---

# front-figures — data-viz, explainability, and causality figures

## Audience and positioning

Solo developers, data scientists, and small teams who:

- Ship **figures** — charts in a docs site, feature-importance plots in
  a model report, DAGs in a causal analysis — and want them to look
  consistent with the rest of the `front-*` stack (Roboto, curated
  palette, dark-mode peer, `role="img"`, alt text stub).
- Want **model explainability** without picking a library the hard way.
  SHAP for tree models, **Shapash** for a full HTML report a business
  stakeholder can read, **TimeSHAP** when the model is a recurrent /
  transformer time-series predictor, LIME when the model is a black-box
  classifier.
- Want **causal-effect estimation** using an opinionated pipeline
  (DoWhy → EconML → refuters), not a hand-rolled Rubin causal model,
  and want the resulting DAG rendered in the same house style.
- Want a **pre-commit gate** that fails fast on the small set of
  data-viz mistakes that survive review: dual y-axes, truncated
  baselines on non-ratio scales, 3D pies, rainbow palettes, missing
  axis labels, undeclared polarity ("higher is better" / "lower is
  better"), and colorblind-unsafe hues.

This skill is **not** a substitute for a real analyst's judgement.
The auditor catches mechanical mistakes; it does not know whether the
chart answers the right question. `explain_model.py` drafts SHAP
plots; you still have to read them. `causal_estimate.py` runs DoWhy's
identify → estimate → refute loop and prints an effect number, but
the effect is only as good as the DAG you supplied.

## Two modes — make and audit

The `front-*` repo is a toolkit for **making** artifacts and
**auditing** them. This skill ships both halves of that loop for
data-science figures:

| Mode | Tool | Purpose |
|---|---|---|
| **Make** — plot a dataset in the house style | `scripts/make_figure.py` | CSV / JSON / Parquet + a spec → Vega-Lite JSON (default) or a matplotlib PNG/SVG in the same palette and typography as `front-ui`. Emits a `<figure role="img">` snippet with alt-text stub and polarity tag. |
| **Make** — explain a fitted model | `scripts/explain_model.py` | Dispatches to SHAP / Shapash / TimeSHAP / LIME by model type (tree / linear / sequence / black-box). Writes summary + dependence + waterfall plots; drops a Shapash HTML report when `--report shapash`. |
| **Make** — estimate a causal effect + draw the DAG | `scripts/causal_estimate.py` | End-to-end DoWhy loop: model → identify → estimate (EconML backend when treatment is continuous) → refute. Renders the DAG with graphviz + writes the effect table to JSON. |
| **Audit** — gate before ship | `scripts/audit_figure.py` | Static parser flags data-viz anti-patterns in a Vega-Lite JSON spec, a matplotlib-emitted SVG, or a rendered `<figure>` block in HTML. Findings as `error` or `warning`; exit non-zero when an `error` is present unless `--strict`. |
| **Install** — one-shot setup of the tiered stack | `scripts/install_figures.py` | pip-installs the dataviz / explainability / causality tiers as requested. Idempotent; safe to re-run. Detects the active env manager (pip / uv / poetry / conda) and defers to it. |

## Honest framing of what each tool covers

| Tool | Catches | Misses |
|---|---|---|
| `scripts/make_figure.py` | Vega-Lite v5 JSON specs in the `front-ui` house style (rounded corners, no top/right spine, no rainbows, palette from `front-colors/references/palette.csv`); matplotlib PNG/SVG fallback with the same palette + Roboto stack; automatic polarity tag on the y-axis when the metric name matches a known "higher/lower is better" pattern; alt-text stub written next to the image. | Does not invent the right chart — you pass the encoding. For chart-type selection see `front-ui/references/dataviz-chart-selection.md`. Does not do map projections beyond Vega-Lite's built-ins; for choropleths see `front-ui/references/dataviz-maps.md`. |
| `scripts/explain_model.py` | Model-agnostic SHAP for tree / linear / kernel models (via `shap.Explainer`), Shapash HTML report for a full business-facing writeup, TimeSHAP for recurrent / attention-based time-series models, LIME as fallback for opaque classifiers. Writes summary plot + top-N dependence plots + one waterfall for the row with the largest absolute prediction. | Does not train models. Does not evaluate them — use `probabl-ai/skills/evaluate-ml-pipeline` or `scikit-learn`'s report utilities. Does not do counterfactual reasoning — see `alibi` or `DiCE`. |
| `scripts/causal_estimate.py` | DoWhy's four-step loop end-to-end (model → identify → estimate → refute); EconML `DML`, `DR-learner`, and `CausalForest` estimators when treatment is continuous; a rendered DAG via graphviz; a JSON effect table for CI. | Does not discover the DAG — you supply it as a gml / networkx / DoWhy string. For discovery, use `causal-learn` or `causallearn`. Does not do interrupted-time-series or synthetic controls — for those see `CausalImpact` or `SparseSC` (out of scope). |
| `scripts/audit_figure.py` | Vega-Lite specs and standalone matplotlib SVGs. Rules: missing / empty axis title; dual y-axis; y-axis truncated on a non-ratio scale; 3D pie / donut with rotation; rainbow palette (viridis is fine; jet / hsv / rainbow are not); colorblind-unsafe pair (red + green + no other channel); undeclared polarity on a metric the auditor recognises; chartjunk (background gradient, drop shadow, custom mark shadows); missing `role="img"` / alt-text stub on the surrounding `<figure>`. | Does not verify whether the *right chart* was chosen for the data (that's a design decision, not a mechanical one). Does not evaluate statistical soundness (baseline choice, confidence-interval computation). Loop a data-viz reviewer in for the final call. |

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "chart this" / "plot the data" / "make a figure" / "dashboard tile" | `make_figure.py` | `python scripts/make_figure.py <data.csv> --x <col> --y <col> --kind <bar\|line\|scatter\|hist\|box\|heatmap> [--emit vega\|png\|svg] [--polarity higher-better\|lower-better\|target=N] [--out fig.json]` |
| "publication-quality figure" / "Nature/Science style" | `make_figure.py` | `python scripts/make_figure.py <data.csv> --preset publication --emit svg --out fig.svg` — 300 dpi, Roboto Serif for labels, no chartjunk, single-column width by default. |
| "explain this model" / "SHAP plot" / "feature importance" | `explain_model.py` | `python scripts/explain_model.py --model model.pkl --data X.csv [--engine auto\|shap\|shapash\|timeshap\|lime] [--out ./explain/]` |
| "shapash report" / "give a stakeholder-facing explanation" | `explain_model.py` | `python scripts/explain_model.py --model model.pkl --data X.csv --engine shapash --report shapash --out ./explain/` — writes a full HTML report. |
| "timeshap" / "explain my LSTM / transformer sequence model" | `explain_model.py` | `python scripts/explain_model.py --model seq_model.pkl --data X.npy --engine timeshap --sequence-cols "t_0,t_1,...,t_N" --out ./explain/` |
| "causal effect" / "average treatment effect" / "DAG" / "DoWhy" | `causal_estimate.py` | `python scripts/causal_estimate.py --data d.csv --treatment T --outcome Y --confounders "X1,X2,X3" --dag dag.gml [--estimator dml\|dr\|causal-forest\|linear] [--refute all\|placebo\|subset\|random-cause]` |
| "audit this figure" / "is this chart misleading" | `audit_figure.py` | `python scripts/audit_figure.py <path>` — accepts a Vega-Lite JSON, a matplotlib SVG, or an HTML file with `<figure>` blocks. |
| "colorblind-safe palette on the figure" | `audit_figure.py` + `front-colors` | `python scripts/audit_figure.py <path>` catches the pattern; run `front-colors/scripts/simulate_cvd.py` on the rendered PNG for a preview. |
| "first-time setup" / "install the data-viz stack" | `install_figures.py` | `python scripts/install_figures.py --tier dataviz+explain+causal` — installs pinned versions of each tier. |

## The four figure tiers

| Tier | Libraries | When to install | Key scripts |
|---|---|---|---|
| **dataviz** | `matplotlib`, `seaborn`, `altair`, `vega_datasets`, `pandas` | Always — the base tier. | `make_figure.py`, `audit_figure.py` |
| **explain** | `shap`, `shapash`, `timeshap`, `lime`, `scikit-learn` | You have a fitted model and want to explain it. | `explain_model.py` |
| **causal** | `dowhy`, `econml`, `networkx`, `graphviz` (system pkg) | You are estimating a causal effect from observational data. | `causal_estimate.py` |
| **install-only** | `pip` / `uv` / `poetry` / `conda` (whichever the project uses) | First-time setup on a fresh machine. | `install_figures.py` |

The tiers are **additive**. `install_figures.py --tier dataviz` installs
only the base plotting stack; `--tier dataviz+explain` adds SHAP /
Shapash / TimeSHAP / LIME; `--tier dataviz+explain+causal` adds DoWhy /
EconML / networkx / graphviz. The auditor itself is stdlib + PyYAML;
you can run `audit_figure.py` on a Vega-Lite JSON without installing
any of the tiers.

## House style — figures that match `front-ui`

Every figure `make_figure.py` emits inherits the front-* design tokens:

1. **Colors** from `front-colors/references/palette.csv` — no rainbows,
   no library defaults. Sequential → `viridis`; diverging → `RdBu_r`;
   qualitative → the curated Apple-inspired palette.
2. **Roboto** everywhere (Serif for publication presets; Mono for
   tabular value labels and tick numbers); **tabular numerals**.
3. **No top/right spine, no tick marks, no gridlines** (heatmaps
   excepted), **no 3D / shadows / gradients** (bar one area fill) —
   matching `front-ui/references/charts-vega.md`.
4. **Dark-mode aware** — Vega toggles on `data-color-scheme="dark"`;
   matplotlib uses `dark_background` under `--dark`.
5. **Polarity stated** on every quantitative axis with a well-defined
   good direction — `(higher is better)` / `(lower is better)` /
   `(target = N)`, reinforced (never carried) by a semantic palette
   colour. Full mapping: `references/polarity-and-color.md`.
6. **`role="img"` + `<figcaption>`** on every `<figure>`; alt text from
   the chart title + polarity when `--alt-from-title` is set.

## Explainability, causality, and auditor rules — see references

The detailed catalogues live in `references/` (progressive disclosure —
load the one you need):

- **Explainability.** `explain_model.py` dispatches to SHAP (default,
  tree/linear/kernel) / Shapash (stakeholder HTML report) / TimeSHAP
  (recurrent / attention time-series) / LIME (black-box fallback);
  `--engine auto` inspects the model, `--engine` overrides, `--report
  shapash` always adds the HTML report. Full engine-selection matrix and
  per-engine output contract: `references/explainability.md`.
- **Causality.** `causal_estimate.py` runs DoWhy's model → identify →
  estimate → refute loop (EconML backends for continuous treatment;
  placebo / random-common-cause / data-subset refuters unless `--refute
  none`), writing `effect.json` + a house-styled `dag.svg`. Backends,
  DAG encodings, and the refutation battery: `references/causality.md`.
- **Auditor rules.** `audit_figure.py` flags `missing-axis-title`,
  `dual-y-axis`, `truncated-baseline`, `pie-3d`, `rainbow-palette`,
  `cvd-unsafe`, `missing-polarity`, `chartjunk`, and `role-img-missing`,
  each with a severity and an `--ignore` escape. Full rule catalogue with
  false-positive notes: `references/audit-figure.md`.

## Curated defaults — user data wins

The canonical palette lives in `front-colors` (see
`front-colors/references/palette.csv`); `front-figures` reads it at
runtime when co-installed. When the user has not specified a
palette, `make_figure.py` reaches for the curated set. Mirror of the
three-Roboto rule in `front-ui/SKILL.md`:

- **Generation, no user palette specified:** use the curated CSV.
- **User names colors or supplies a palette** ("our brand is `#8B5CF6`",
  "we already have a tailwind.config.js with our tokens"): use theirs.
- **Audit mode:** respect the existing colors; do not refactor to the
  CSV unless the user asks. `audit_figure.py` should flag CVD-unsafe
  hues against the user's palette, not against ours.

## Tool composition

For a data-science deliverable end-to-end:

```bash
# 1. Explore + plot in the house style.
python front-figures/scripts/make_figure.py data.csv \
    --x date --y conversion_rate --kind line \
    --polarity higher-better --emit vega --out fig.json

# 2. Explain the model.
python front-figures/scripts/explain_model.py \
    --model model.pkl --data X.csv --engine auto \
    --report shapash --out ./explain/

# 3. Estimate the causal effect + draw the DAG.
python front-figures/scripts/causal_estimate.py \
    --data d.csv --treatment T --outcome Y \
    --confounders "X1,X2,X3" --dag dag.gml \
    --estimator dml --refute all --out ./causal/

# 4. Audit the emitted figures.
python front-figures/scripts/audit_figure.py fig.json
python front-figures/scripts/audit_figure.py ./explain/
python front-figures/scripts/audit_figure.py ./causal/dag.svg

# 5. Preview colorblind rendering.
python front-colors/scripts/simulate_cvd.py fig.png --grid

# 6. Draft alt text for the surrounding page.
python front-vision/scripts/alt_from_ollama.py --kind complex \
    --context "Weekly conversion rate — higher is better" fig.png

# 7. Static a11y lint on the page that hosts the figure.
python front-accessibility/scripts/lint_a11y.py public/report.html
```

## When NOT to use this skill

- You need a **live dashboard** (streaming metrics, WebSocket
  refresh) — `front-figures` emits static specs / files. Use
  Grafana, Superset, or Streamlit.
- You need **notebook-first** exploration — the make scripts are
  pipe-ready CLIs, not Jupyter widgets. Use `jupyter-notebook`
  (Anthropic) or `working-in-notebooks` (legout) skills.
- You need **counterfactual explanations** — see `alibi`, `DiCE`, or
  the WhatIf tool. SHAP / Shapash / LIME answer *"why did the model
  predict this"*; counterfactuals answer *"what would flip the
  prediction"*.
- You need **causal discovery** (learning the DAG from data) — see
  `causal-learn` or `causal-discovery-toolbox`. This skill assumes
  the DAG is supplied.
- You need **interrupted-time-series** or **synthetic-control**
  analyses — see `CausalImpact` (Bayesian ITS) or `SparseSC`
  (synthetic controls). Out of scope here.
- Your team already uses Style Dictionary / Theo / Tokens Studio and
  a designed dashboard framework — those are more powerful; this
  skill is a deterministic pre-commit gate + a house-styled emitter.

## References

- `references/dataviz-decision-tree.md` — Which chart type for which
  question (frequency, comparison, part-of-whole, time series,
  distribution, correlation, geospatial).
- `references/polarity-and-color.md` — Why every quantitative axis
  gets a `(higher is better)` / `(lower is better)` / `(target = N)`
  tag; how the polarity color is picked from the palette's
  Psychology-Positive / Negative projections; Emotion / Concept
  accessors. Source of the semantic mapping:
  <https://harchaoui.org/warith/colors/>.
- `references/explainability.md` — SHAP / Shapash / TimeSHAP / LIME
  engine choice; per-engine output contract; when to prefer each.
- `references/causality.md` — DoWhy's four-step loop; EconML backends;
  refutation battery; how to encode a DAG in gml / DoWhy string form.
- `references/audit-figure.md` — Full rule catalogue for
  `audit_figure.py` with false-positive notes.
- `references/publication-presets.md` — Journal-ready presets
  (Nature single-column, Science two-column, PLOS full-width, IEEE
  transactions).

## Scripts

| Script | Install | Purpose |
|---|---|---|
| `scripts/make_figure.py` | `pip install -r scripts/requirements-dataviz.txt` | CSV / JSON / Parquet + spec → Vega-Lite JSON (default), matplotlib PNG/SVG, or seaborn PNG. House style enforced; polarity tag auto-attached; alt-text stub written. |
| `scripts/explain_model.py` | `pip install -r scripts/requirements-explain.txt` | Model-agnostic explainability dispatcher — SHAP / Shapash / TimeSHAP / LIME. Auto-picks by model type; `--engine` overrides. |
| `scripts/causal_estimate.py` | `pip install -r scripts/requirements-causal.txt` | DoWhy loop (model → identify → estimate → refute) with EconML backends. Renders DAG in front-* house style; writes `effect.json`. |
| `scripts/audit_figure.py` | stdlib + PyYAML | Static auditor for Vega-Lite JSON / matplotlib SVG / HTML `<figure>` blocks. Deterministic; no model, no network. |
| `scripts/install_figures.py` | subprocess to project env manager | Idempotent installer for the three tiers (dataviz / explain / causal). Detects pip / uv / poetry / conda. |
| `scripts/_argparse.py`, `scripts/_click.py`, `scripts/_lang.py`, `scripts/_vocab.py` | (internal helpers) | Argparse / Click factory, language detection, project-vocab biasing. Duplicated per-skill so each skill stays self-contained. |
| `scripts/_style.py` | stdlib only | Shared style tokens (palette lookup, matplotlib rcParams, Vega-Lite `config` block, Roboto stack). Reads `front-colors/references/palette.csv` when co-installed. |

## Companion skills

| You also need… | Install |
|---|---|
| Vanilla-JS + Tailwind UI generation (house style, tokens, components) | `front-ui` |
| Wrap the CLIs in a GUI (argparse → web form) | `front-cli-gui` |
| Markdown → website + meta + favicons + indexes | `front-publish` |
| Static HTML a11y lint on the page hosting the figure | `front-accessibility` |
| WCAG contrast audit + CVD simulation on the rendered PNG | `front-colors` |
| W3C alt text for the rendered figure (local Ollama vision) | `front-vision` |
| Local WebVTT / SRT captions for an accompanying video | `front-audio` |
| Laws-of-UX audit on the surrounding page | `front-ux-laws` |
