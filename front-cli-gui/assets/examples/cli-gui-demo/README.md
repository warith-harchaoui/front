# cli-gui-demo

Worked example of the **front** skill's flagship CLI → GUI workflow. A mock CLI (`imgconvert`) is wrapped in a single-page GUI built with vanilla JavaScript, Tailwind CSS, Montserrat, and a tiny Python proxy.

## What it shows

The CLI is small but exercises every flag-to-control mapping in the skill's CLI → GUI recipe:

| CLI flag shape | GUI control |
|---|---|
| Positional path | `<input type="text">` |
| `int` | `<input type="number">` |
| Bounded `int` (e.g. `--quality 1-100`) | `<input type="range">` + live `<output>` |
| 3-option `enum` (`--to {png,jpg,webp}`) | `<fieldset role="radiogroup">` styled as segmented control |
| `boolean` (`--keep-aspect`) | `<input type="checkbox" role="switch">` styled as a pill |
| Streaming stdout | `<pre>` log panel with auto-scroll, fed by Server-Sent Events |

See `manifest.json` for a per-file map of which skill principle each piece demonstrates.

## Launch

```bash
cd front-cli-gui/assets/examples/cli-gui-demo
python server.py
```

Open <http://localhost:8787>. No `pip install` is needed — the server uses only the Python standard library, and the GUI uses the Tailwind Play CDN (no build step). Montserrat is bundled under `public/fonts/montserrat/` and served by the same proxy.

## How it maps to the skill's CLI → GUI workflow

The eight steps from `SKILL.md` → "CLI → GUI workflow":

1. **Inventory the CLI** — read `cli/imgconvert.py` (or `python cli/imgconvert.py --help`). Three subcommands: `resize`, `convert`, `optimize`.
2. **Categorize each command** — all three are form-driven with a streamed log. None are list-producing.
3. **Pick a layout** — 3 commands → sidebar on the start (desktop) and a horizontal tab strip (mobile). See `public/index.html` `<nav id="sidebar">`.
4. **Map flags to form controls** — see the table above.
5. **Wire execution** — `public/app.js` posts JSON to `/run` on the Python proxy; `server.py` spawns the CLI and streams stdout back via Server-Sent Events.
6. **Stream output** — `app.js` consumes the SSE stream and appends each line to the `<pre>` log panel.
7. **Emit a single page** — one HTML, one JS module, one CSS (Tailwind directives via the Play CDN), Montserrat self-hosted.
8. **Document launch** — this file.

## File structure

```text
cli-gui-demo/
├── README.md                       this file
├── manifest.json                   principles each file demonstrates
├── server.py                       HTTP + SSE proxy (Python stdlib only)
├── cli/
│   └── imgconvert.py               mock CLI (3 subcommands)
└── public/
    ├── index.html                  GUI markup
    ├── app.js                      vanilla ES module
    ├── favicon.svg                 single-shape SVG icon
    └── fonts/montserrat/           variable + italic-variable WOFF2 + OFL.txt
```

Total emitted lines (excluding fonts): ~700.

## What's not here

- **Real image conversion** — the CLI writes a stub file. Adding Pillow would distract from the GUI-mapping demo.
- **Authentication, persistence, multi-step wizards** — not relevant to this demo.
- **A bundled Tailwind build** — the Play CDN keeps the demo zero-build. For production, the skill's `stack-tailwind.md` documents the Tailwind CLI / Vite swap.
- **WCAG audit** — `python front-a11y/scripts/lint_a11y.py front-cli-gui/assets/examples/cli-gui-demo/public/` should pass; this demo is meant to be a clean baseline.

## License

The demo is released under The Unlicense (see the repository root's `LICENSE.md`). Montserrat retains its SIL Open Font License — see `public/fonts/montserrat/OFL.txt`.
