# Choosing the Right Chart

Translated and adapted from Jérôme Gombert's deck *Dataviz : choisir son graph*. Read alongside `charts-vega.md` (house style for the chart you pick) and `dashboard-ergonomics.md` (how it sits in a tile).

## Two questions first

Before any chart, two answers.

1. **What is the message?** What is the single thing the chart should make obvious in 3 seconds?
2. **Who is the audience?** Their level of data literacy decides how much guidance the chart needs — title length, tooltip detail, annotations.

If you can't answer both, you're not ready to pick a chart yet.

## Four data shapes

Every chart belongs to one of four families. Identify the family before picking the chart.

| Family | Question it answers | Examples |
|---|---|---|
| Comparison | "How does A compare to B?" or "How has A changed over time?" | Bar, column, line, table |
| Composition | "What are the parts of a whole?" | Pie, stacked bar, stacked area, waterfall |
| Relationship | "How does X relate to Y?" | Scatter, bubble, connected scatter |
| Distribution | "How are values spread?" | Histogram, box plot, density plot |

## Decision tree

### Comparison

| Subtype | Best chart |
|---|---|
| Few items, no time | Horizontal **bar** chart |
| Few items, over time, few periods | **Column** chart |
| Few items, over time, many periods | **Line** chart |
| Many items, no time | Sorted horizontal bar chart |
| Two variables per item | Variable-width column chart, or table with embedded sparklines |
| Cyclic time (week, year) | Radar or polar line |

### Composition

| Subtype | Best chart |
|---|---|
| Static, few categories, only relative differences matter | **Pie** chart (only if ≤ 4 slices) |
| Static, only relative differences matter, many categories | **100 % stacked column** (one column) |
| Static, both absolute and relative matter | **Stacked column** chart |
| Over time, only relative differences matter | **100 % stacked area** |
| Over time, both absolute and relative matter | **Stacked area** chart |
| Showing additions / subtractions to a total | **Waterfall** chart |
| Hierarchical composition | **Sunburst** or **treemap** |

### Relationship

| Subtype | Best chart |
|---|---|
| Two variables, small dataset | **Scatter** plot |
| Two variables, large dataset | Scatter with transparency / density |
| Three variables | **Bubble** chart |
| Many variables | **Parallel coordinates** or **scatter matrix** |

### Distribution

| Subtype | Best chart |
|---|---|
| One variable, single distribution | **Histogram** |
| One variable, distributions over a category | **Box plot** or **violin** |
| One variable, distribution over time | **Histogram in line** (small multiples) |
| Two variables | **2D histogram** or **heatmap** |

## Hard-won rules

1. **Pies max 4 slices.** Beyond that the eye can't compare angles. Switch to a sorted horizontal bar chart.
2. **No 3D charts.** They distort proportions and add no information.
3. **Line charts for time, bars for categories.** Reversing this confuses readers.
4. **Sort bar charts by value**, not by name, unless the order is meaningful (months, ratings).
5. **Stacked vs. grouped**: stacked answers "what's the total?", grouped answers "which one is biggest?". Pick the question, then the layout.
6. **Axes start at zero for bars** (truncated bars lie). For lines, truncation is acceptable when the message is the shape of change.
7. **Annotate the message** — a single highlighted point or short label beats forcing the user to find it.
8. **Title = the conclusion.** "Revenue grew 18 % in Q3" beats "Revenue by quarter".

## Variables count and axis design

When picking a chart, also decide:

- **How many variables** are encoded? Each axis, color, size, and shape is a variable.
- **How many data points**? > 200 categories on a bar chart will not read; switch chart shape.
- **Axis scaling**: linear, log, or percentage. Log scales need a clear note in the title or legend.

## Time series

Three sub-shapes:

| Period count | Best chart |
|---|---|
| Few periods (≤ 6) | Column chart |
| Many periods | Line chart |
| Cyclic (hours of day, days of week, months of year) | Polar / radial or column with cyclic axis |

For long time series, consider a **horizon chart** or **small multiples** rather than one cluttered line.

## When in doubt

- Reach for a sorted horizontal bar chart. It works for comparison, supports labels, scales to many categories, and reads in grayscale.
- Reach for a line chart with one or two series. It works for change over time and is unambiguous.

These two shapes solve maybe 70 % of real dataviz needs. The fancier shapes earn their place only when the data really calls for them.

## Checklist

- [ ] Message stated as a single sentence before picking the chart.
- [ ] Audience literacy considered.
- [ ] Data shape identified: comparison / composition / relationship / distribution.
- [ ] Chart shape matches the data shape.
- [ ] Pie has ≤ 4 slices.
- [ ] Bars sorted by value (unless the category has natural order).
- [ ] Bars start at zero.
- [ ] No 3D.
- [ ] Title states the conclusion, not the dimensions.
- [ ] Vega-Lite spec built per `charts-vega.md`.
