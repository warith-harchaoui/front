# Vega-first gallery — the spec to replace matplotlib / seaborn / pyplot

**Prefer Vega-Lite.** For any chart it can express, reach for a Vega-Lite
v5 spec before matplotlib, seaborn, or pyplot — because the spec carries
its own data (figure + data + encoding in one auditable, diffable,
re-traceable file), it themes to the house style via `_style.vega_config`,
it drops straight into a front-ui page, and the [Ralph Eyeball
Loop](ralph-eyeball-loop.md) rasterises the *actual* spec that ships.

Every skeleton below is `mark` + `encoding` (+ `transform` where it does
real work), with `"data": {"name": "table"}` as a placeholder. In
production, add `"$schema": "https://vega.github.io/schema/vega-lite/v5.json"`
and merge `_style.vega_config(dark=…)` into `config`; render with
`scripts/render_diagram.py fig.vl.json --out fig.png`.

Type fields: `nominal` (categorical), `ordinal` (ordered), `quantitative`
(numeric), `temporal` (dates).

Sources: [Vega-Lite gallery](https://vega.github.io/vega-lite/examples/),
[Vega gallery](https://vega.github.io/vega/examples/),
[vl-convert](https://github.com/vega/vl-convert).

## 1. Bar

| Chart | seaborn / matplotlib | Key |
|---|---|---|
| Vertical bar | `sns.barplot` / `plt.bar` | `x` N, `y` Q |
| Horizontal bar | `sns.barplot(orient="h")` | swap x/y — prefer for ranked categories |
| Grouped bar | `sns.barplot(hue=…)` | `xOffset` (v5 idiom) |
| Stacked bar | `sns.histplot(multiple="stack")` | `color` adds the series |
| 100 % stacked | `multiple="fill"` | `"stack": "normalize"` |

```json
{"data":{"name":"table"},"mark":"bar","encoding":{"y":{"field":"cat","type":"nominal","sort":"-x"},"x":{"field":"val","type":"quantitative"}}}
```
```json
{"data":{"name":"table"},"mark":"bar","encoding":{"x":{"field":"cat","type":"nominal"},"y":{"field":"val","type":"quantitative"},"xOffset":{"field":"grp","type":"nominal"},"color":{"field":"grp","type":"nominal"}}}
```

## 2. Line

| Chart | seaborn / matplotlib | Key |
|---|---|---|
| Line | `sns.lineplot` | `x` T, `y` Q |
| Multi-series | `sns.lineplot(hue=…)` | `color` N |
| Line + point | `marker="o"` | `{"type":"line","point":true}` |
| Step | `drawstyle="steps"` | `"interpolate":"step-after"` |

```json
{"data":{"name":"table"},"mark":{"type":"line","point":true},"encoding":{"x":{"field":"t","type":"temporal"},"y":{"field":"val","type":"quantitative"},"color":{"field":"series","type":"nominal"}}}
```

## 3. Area

| Chart | matplotlib | Key |
|---|---|---|
| Area | `fill_between` | `mark:"area"` |
| Stacked area | `stackplot` | + `color` |
| Streamgraph | `stackplot(baseline="wiggle")` | `"stack":"center"` |

```json
{"data":{"name":"table"},"mark":"area","encoding":{"x":{"field":"t","type":"temporal"},"y":{"field":"val","type":"quantitative","stack":"center"},"color":{"field":"series","type":"nominal"}}}
```

## 4. Scatter

| Chart | seaborn | Key |
|---|---|---|
| Scatter | `sns.scatterplot` | `x` Q, `y` Q |
| Bubble | `size=…` | + `size` Q |
| By category | `hue=…` | + `color` N |

```json
{"data":{"name":"table"},"mark":"point","encoding":{"x":{"field":"x","type":"quantitative"},"y":{"field":"y","type":"quantitative"},"size":{"field":"mag","type":"quantitative"},"color":{"field":"cat","type":"nominal"}}}
```

## 5. Histogram / density

| Chart | seaborn | Key |
|---|---|---|
| Histogram | `sns.histplot` | `"bin":true` + `"aggregate":"count"` |
| Density (KDE) | `sns.kdeplot` | `density` transform (Gaussian — a real KDE) |

```json
{"data":{"name":"table"},"mark":"bar","encoding":{"x":{"field":"val","type":"quantitative","bin":true},"y":{"aggregate":"count"}}}
```
```json
{"data":{"name":"table"},"transform":[{"density":"val","bandwidth":0.3}],"mark":"area","encoding":{"x":{"field":"value","type":"quantitative"},"y":{"field":"density","type":"quantitative"}}}
```

## 6. Box / strip

```json
{"data":{"name":"table"},"mark":{"type":"boxplot","extent":"min-max"},"encoding":{"x":{"field":"grp","type":"nominal"},"y":{"field":"val","type":"quantitative"}}}
```
Strip / jitter (`sns.stripplot`) via a random `xOffset`:
```json
{"data":{"name":"table"},"transform":[{"calculate":"random()","as":"jitter"}],"mark":{"type":"point","size":8},"encoding":{"x":{"field":"grp","type":"nominal"},"y":{"field":"val","type":"quantitative"},"xOffset":{"field":"jitter","type":"quantitative","axis":null}}}
```

## 7. Heatmap

```json
{"data":{"name":"table"},"mark":"rect","encoding":{"x":{"field":"col","type":"nominal"},"y":{"field":"row","type":"nominal"},"color":{"field":"val","type":"quantitative"}}}
```
2D binned density (`plt.hist2d`): bin both axes, `"aggregate":"count"` on color.

## 8. Small multiples

```json
{"data":{"name":"table"},"mark":"line","encoding":{"x":{"field":"t","type":"temporal"},"y":{"field":"val","type":"quantitative"},"facet":{"field":"grp","type":"nominal","columns":3}}}
```
Use `column` × `row` for a full grid (`sns.FacetGrid`).

## 9. Layered composite

Bar + mean rule (replaces a manual `axhline`):
```json
{"data":{"name":"table"},"layer":[
  {"mark":"bar","encoding":{"x":{"field":"cat","type":"nominal"},"y":{"field":"val","type":"quantitative"}}},
  {"mark":"rule","encoding":{"y":{"aggregate":"mean","field":"val","type":"quantitative"}}}
]}
```

## 10. Error bars / CI

The composite marks compute the interval from raw rows (`extent` = `ci` /
`stderr` / `stdev` / `iqr`) — the seaborn `errorbar=` default, done in-spec:
```json
{"data":{"name":"table"},"mark":{"type":"errorband","extent":"ci"},"encoding":{"x":{"field":"t","type":"temporal"},"y":{"field":"val","type":"quantitative","title":"mean ± CI"}}}
```
Hold precomputed `lo`/`hi` instead? Use a `rule` with `y`/`y2`.

## 11. Ranged dot / lollipop / dumbbell

```json
{"data":{"name":"table"},"encoding":{"y":{"field":"cat","type":"nominal"},"x":{"field":"val","type":"quantitative"}},"layer":[
  {"mark":"rule"},
  {"mark":{"type":"point","filled":true,"size":100}}
]}
```

## Explainability & causality — from extracted model data

These replace `shap.plots.*` and DoWhy's graphviz output. You extract the
numbers from the model and drive Vega yourself; the plot is just data.

- **SHAP beeswarm** — melt `shap_values.values` to long rows
  `{feature, shap, feat_val_norm}`; `circle` mark, `x`=shap, `y`=feature,
  `color`=normalised feature value, random `yOffset` as jitter. (Vega-Lite
  has no true swarm packing — jitter is the honest approximation.)
- **SHAP / permutation importance** — `mean(|shap|)` per feature → sorted
  horizontal bar (`"sort":"-x"`). Clean.
- **SHAP waterfall** — one row's contributions; running sum via a `window`
  transform, floating bars with `x`/`x2`. Workable, the most awkward.
- **LIME weights** — `explanation.as_list()` → diverging horizontal bar,
  color by sign. Clean.
- **Partial dependence / ICE** — faint per-sample `line` layer (`detail`
  = line id) under a bold PD average line. Clean.
- **Causal DAG** — precompute the layout in Python (`networkx`
  `graphviz_layout`/`spring_layout`), emit nodes `{id,x,y}` and edges
  `{x,y,x2,y2}`; layer `rule` (edges) + `circle` (nodes) + `text`
  (labels). Reproducible. (Auto-layout needs full Vega's `force`
  transform — non-deterministic; prefer precomputed coordinates.)

```json
{"data":{"name":"table"},"transform":[{"calculate":"random()","as":"jit"}],"mark":{"type":"circle","size":14,"opacity":0.6},"encoding":{"x":{"field":"shap","type":"quantitative","title":"SHAP value"},"y":{"field":"feature","type":"nominal","sort":{"field":"imp","order":"descending"}},"yOffset":{"field":"jit","type":"quantitative","axis":null},"color":{"field":"feat_val_norm","type":"quantitative","title":"feature value"}}}
```

## Print & vector output

`vl-convert` emits **PNG, SVG, and vector PDF** — journal-ready. Hit exact
physical dimensions by setting `width`/`height` in the spec to
inches × dpi (e.g. Nature single column = 89 mm ≈ 3.5 in → 1050 px at
300 dpi) and rendering `--format pdf` / `--format svg`. Contour / 2D
density fields need **full Vega** (`isocontour` / `kde2d` transforms),
not Vega-Lite.

## The honest residue — where matplotlib still wins

Vega genuinely cannot (or cannot cleanly) do these; keep them in
matplotlib / plotly / graphviz:

- **True 3D** surfaces / volumes (`plot_surface`, voxels).
- **Filled contour fields** in Vega-Lite (2D contours live in full Vega).
- **True beeswarm** collision packing (jitter only).
- **Dendrograms / cluster trees**, **Sankey / alluvial**, **chord**,
  **treemap / sunburst** — bespoke full-Vega recipes at best.
- **Quiver / stream / vector fields.**
- **`imshow` of raw arrays** with colormap interpolation (use `rect` for
  gridded data).
- **Broken axes, twin independent secondary axes** (deliberately
  discouraged).
- **>~50k marks** — in-browser rendering gets heavy; rasterise with
  matplotlib / datashader.

Everything else — families 1–11 and the extractable explainability plots —
is idiomatic Vega and fully replaces seaborn / pyplot.
