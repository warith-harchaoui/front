# Charts — Vega-Lite

Source for colors: <https://harchaoui.org/warith/colors/> (see also `references/color-psychology.md`).
Source for the rendering engine: <https://vega.github.io/vega-lite/>.

## When to consult this file

- Any chart, graph, dashboard tile, or data visualization
- Sparklines, distributions, time series, categorical comparisons

## Library choice

The skill emits **Vega-Lite v5 JSON specs**, rendered with the Vega-Embed runtime. No D3 written by hand, no Chart.js, no Recharts.

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
```

For production, install via npm (`vega`, `vega-lite`, `vega-embed`) and bundle.

## House style — non-negotiable defaults

1. **Rounded corners at 10 px** on every chart mark and on the chart container.
2. **Colors from `color-psychology.md`** — no rainbow palettes, no Vega defaults.
3. **No 3D**, no drop shadows, no gradients (except a single linear fill for area charts).
4. **No gridlines on the value axis** unless explicitly needed; light gridlines on the category axis only.
5. **Tabular numerals** for value labels.
6. **Dark-mode aware** — provide two specs (light/dark) or override `config` based on `data-color-scheme`.
7. **Title above** in body weight; subtitle below in label-secondary.

## Skill color palette in Vega-Lite

```json
{
  "config": {
    "background": "transparent",
    "view": { "stroke": "transparent" },
    "axis": {
      "labelFont": "Montserrat",
      "titleFont": "Montserrat",
      "labelColor": "#3C3C43",
      "titleColor": "#000000",
      "grid": false,
      "domain": true,
      "domainColor": "rgba(60,60,67,0.36)",
      "tickColor": "rgba(60,60,67,0.36)"
    },
    "title":  { "font": "Montserrat", "fontWeight": 600, "color": "#000000" },
    "header": { "labelFont": "Montserrat", "titleFont": "Montserrat" },
    "legend": { "labelFont": "Montserrat", "titleFont": "Montserrat", "labelColor": "#3C3C43", "titleColor": "#000000" },
    "range": {
      "category": ["#007AFF","#28CD41","#FF9500","#AF52DE","#FF2D55","#FFCC00","#79DBDC","#FF3B30"],
      "diverging": ["#FF3B30","#FFCC00","#28CD41"],
      "heatmap":   ["#CCE4FF","#007AFF"],
      "ramp":      ["#CCE4FF","#007AFF"]
    },
    "bar":  { "cornerRadiusEnd": 10, "color": "#007AFF" },
    "rect": { "cornerRadius": 10 },
    "line": { "color": "#007AFF", "strokeWidth": 2.5, "interpolate": "monotone" },
    "area": { "color": "#007AFF", "opacity": 0.2, "line": { "strokeWidth": 2.5 } },
    "point":{ "color": "#007AFF", "filled": true, "size": 60 },
    "tick": { "color": "#007AFF" }
  }
}
```

Apply this `config` block to every spec. The skill ships a ready-to-include example at `assets/components/chart-bar.json`.

## Dark-mode override

When `<html data-color-scheme="dark">`, swap the config to:

```json
{
  "config": {
    "background": "transparent",
    "axis": { "labelColor": "rgba(235,235,245,0.6)", "titleColor": "#FFFFFF", "domainColor": "rgba(84,84,88,0.65)", "tickColor": "rgba(84,84,88,0.65)" },
    "title":  { "color": "#FFFFFF" },
    "legend": { "labelColor": "rgba(235,235,245,0.6)", "titleColor": "#FFFFFF" },
    "bar":  { "color": "#0A84FF" },
    "line": { "color": "#0A84FF" },
    "area": { "color": "#0A84FF", "opacity": 0.2 },
    "point":{ "color": "#0A84FF" }
  }
}
```

## Container

```html
<figure class="rounded-[10px] bg-surface-secondary p-4 dark:bg-surface-secondary-dark">
  <figcaption class="sr-only">Weekly active users</figcaption>
  <div id="chart" role="img" aria-label="Weekly active users line chart"></div>
</figure>
<script type="module">
  import 'vega'; import 'vega-lite'; import embed from 'vega-embed';
  const spec = await (await fetch('./chart-line.json')).json();
  embed('#chart', spec, { actions: false, renderer: 'svg' });
</script>
```

Use SVG renderer (sharper, smaller for typical chart sizes, themable via CSS).

## Concrete rules

1. **Container radius 10 px** (`rounded-[10px]`) — matches the mark radius.
2. **One color per series** drawn from the skill palette in `color-psychology.md`.
3. **Legends only when 2+ series**; otherwise label inline.
4. **Tooltip enabled** (Vega-Embed default) for any chart richer than a single sparkline.
5. **Accessible**: wrap in `role="img"` + `aria-label` describing the takeaway, not the chart shape.

## Checklist

- [ ] Vega-Lite JSON, not hand-written SVG.
- [ ] House `config` applied.
- [ ] Rounded corners 10 px on marks and on the container.
- [ ] Colors from the skill palette.
- [ ] Dark-mode override wired.
- [ ] `role="img"` + `aria-label`.
- [ ] SVG renderer.
