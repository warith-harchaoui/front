# Inter — alternate self-hosted family

`front-ui` defaults to **Montserrat** (bundled at
`../montserrat/`) and supports **Inter** as a documented alternate
for dense developer / dashboard / data-table surfaces. Inter is not
bundled because of repo-size discipline; ship it from this folder
when you want to swap.

## What goes in this folder

1. **WOFF2 files** for the four weights `front-ui` uses (400, 500,
   600, 700). The variable-axis file `Inter[opsz,wght].woff2` works
   for all four if your build pipeline supports `font-variation-settings`.
2. **`OFL.txt`** from <https://rsms.me/inter/> — Inter ships under
   SIL Open Font License like Montserrat.
3. **`fonts.css`** with the `@font-face` block(s) pointing at the
   files above.

## Where to get the files

Inter's canonical source is <https://rsms.me/inter/> (CC BY 4.0 site,
OFL fonts). The author hosts both the static-weight WOFF2 files and
the variable build.

```bash
# Variable axis (preferred; one file, every weight)
curl -L -o Inter.var.woff2 \
  https://rsms.me/inter/font-files/Inter.var.woff2
curl -L -o OFL.txt \
  https://rsms.me/inter/inter.css   # adjust to whichever license url
```

If you'd rather pin the static weights individually:

```bash
for w in 400 500 600 700; do
  curl -L -o "Inter-${w}.woff2" \
    "https://rsms.me/inter/font-files/Inter-${w}.woff2"
done
```

## Wiring it into the project

After dropping the files here, follow `references/stack-tailwind.md`
§ *"Typography — default, alternate, and custom swap"*. The three
edits are:

1. `tailwind.config.js` → set
   `fontFamily.sans = ['Inter Variable', 'Inter', 'sans-serif']`
2. `src/styles/app.css` → replace the Montserrat `@import` with
   `@import url('../fonts/inter/fonts.css');`
3. Project README → note that the surface uses Inter and why.

Every other rule (semantic tokens, dark-mode peers, focus rings,
44 × 44 px hit area) stays unchanged.

## Why an empty folder ships in the skill

The folder exists so the `references/stack-tailwind.md` and `SKILL.md`
pointers resolve to a real on-disk path — the release-packaging smoke
test (`tests/test_release_packaging.py`) checks every backticked path
in `SKILL.md` and would otherwise fail. Don't delete the folder; drop
the WOFF2 files in.
