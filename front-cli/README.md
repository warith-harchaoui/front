# front-cli

A thin top-level driver for the four [`front`](https://github.com/warith-harchaoui/front) skills.

```bash
pip install ./front-cli         # from the repo root, or
pip install front-cli           # from PyPI when published
```

Then:

```bash
front --help                    # discoverable sub-commands across all 4 skills
front --version

front ui validate               # → python front-ui/scripts/validate.py

front a11y lint public/         # → python front-a11y/scripts/lint_a11y.py public/
front a11y contrast --palette palette.json
front a11y cvd screenshot.png
front a11y alt photo.jpg --kind informative --lang en
front a11y captions video.mp4 --format vtt

front publish favicons logo.png --out public --name "Project"
front publish meta page.html
front publish indexes --root . --base-url https://example.com
front publish plain --input copy.md
```

The driver **shells out** to each existing script — it does not duplicate any
logic. The validators (`validate`, `lint`, `contrast`, `cvd`, `indexes`) stay
stdlib-only when invoked directly, even if `front-cli` itself depends on Click.

## How it finds the skills

`front-cli` looks for each skill folder in this order:

1. `$FRONT_SKILLS_PATH` (colon-separated list of parent directories).
2. The current working directory (useful when running inside the repo).
3. `~/.claude/skills/`.
4. `~/.opencode/skills/`.

If a skill is missing, the relevant sub-command says so and points at the
install instructions.

## Why this exists

Before `front-cli`, users ran each script directly:

```bash
python front-a11y/scripts/lint_a11y.py public/
python front-publish/scripts/favicons.py logo.png --out public
```

That works, but it leaks the skill layout and there's no single `--help`
to discover available actions. `front-cli` collapses the surface to a
single `git`-style command, ships `--version`, and (when installed via
`pip install`) wires shell completion automatically through Click.

## License

The Unlicense. The same applies as for the rest of the `front` repo.
