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

front accessibility lint public/  # → python front-accessibility/scripts/lint_a11y.py public/
front colors contrast --palette palette.json
front colors cvd screenshot.png
front vision alt photo.jpg --kind informative --lang en
front audio captions video.mp4 --format vtt

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
python front-accessibility/scripts/lint_a11y.py public/
python front-publish/scripts/favicons.py logo.png --out public
```

That works, but it leaks the skill layout and there's no single `--help`
to discover available actions. `front-cli` collapses the surface to a
single `git`-style command, ships `--version`, and (when installed via
`pip install`) wires shell completion automatically through Click.

## Shell completion

Click ships completion scripts for `bash`, `zsh`, and `fish`. Generate
one once, source it from your shell rc, and tab-completion for `front`
sub-commands + options Just Works.

```bash
# Bash
_FRONT_COMPLETE=bash_source front > ~/.front-complete.bash
echo 'source ~/.front-complete.bash' >> ~/.bashrc

# Zsh
_FRONT_COMPLETE=zsh_source front > ~/.front-complete.zsh
echo 'source ~/.front-complete.zsh' >> ~/.zshrc

# Fish
_FRONT_COMPLETE=fish_source front > ~/.config/fish/completions/front.fish
```

The same `_<TOOL>_COMPLETE=<shell>_source` trick works for the per-script
CLIs that were migrated to Click — useful if you invoke them directly
rather than through the `front` driver:

```bash
_ALT_FROM_OLLAMA_COMPLETE=zsh_source alt_from_ollama.py > ~/.alt-complete.zsh
_CAPTIONS_FROM_WHISPER_COMPLETE=zsh_source captions_from_whisper.py > ~/.captions-complete.zsh
_META_FROM_OLLAMA_COMPLETE=zsh_source meta_from_ollama.py > ~/.meta-complete.zsh
_PLAIN_LANGUAGE_COMPLETE=zsh_source plain_language.py > ~/.plain-complete.zsh
```

These commands invoke the script with a special env var so Click prints
the completion shell snippet to stdout — nothing is installed, modified,
or downloaded.

## License

The Unlicense. The same applies as for the rest of the `front` repo.
