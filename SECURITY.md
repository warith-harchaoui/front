# Security policy

The project is released into the public domain under
[The Unlicense](LICENSE.md). The same terms apply to the disclosure
process: report what you find, on your own schedule, with no
obligation either way.

## What "security" means here

`front` is a collection of Claude skills plus stdlib-and-Pillow
Python scripts. There is no service, no daemon, no network listener
shipped by the repo itself. The realistic attack surface is:

- Scripts that execute as the user who invokes them. They read and
  write files in the project directory and `~/.cache/front-skill/`.
- Scripts that download model weights or call a local Ollama daemon
  (`install_alt_ai.py`, `install_captions.py`,
  `alt_from_ollama.py`, `meta_from_ollama.py`,
  `plain_language.py`, `captions_from_whisper.py`). HTTPS to the
  upstream registries (Hugging Face mirror, Ollama registry) and
  loopback to `127.0.0.1:11434`.
- Emitted HTML / JS that ships into the user's site. The skill bans
  inline `<script>` and inline `<style>` for production output and
  the `validate.py` gate refuses to pass with them present.

Out of scope: model output. The skill calls a local model; the model
can hallucinate. That is a quality issue, not a security issue.

## Reporting a vulnerability

Open a GitHub issue at
<https://github.com/warith-harchaoui/front/issues> with the label
`security`. If the report is sensitive, email
<warith@deraison.ai> instead and the issue can be opened publicly
once a fix or workaround lands.

There is no bounty program and no SLA. The repo is maintained by one
person on best-effort time. Realistic turnaround:

- Acknowledgement: within one week.
- Fix or written rationale: within four weeks for issues that affect
  a script that touches the network or executes a subprocess; longer
  for everything else.

## Disclosure

Coordinated disclosure is preferred but not required. The Unlicense
does not give the maintainer any standing to demand otherwise. If you
publish first, please link the issue or commit that addresses the
problem so users can act on the same information.

## Supply-chain notes

- The skill pins no minor versions for the Python dependencies it
  declares (`requests`, `click`, `Pillow`, `numpy`). Pin yourself if
  you need reproducibility.
- Bundled fonts ship under their own license
  (Montserrat: SIL OFL). See `LICENSE.md` for the carve-out.
- Distribution today is `git clone` + `cp -r`. There is no signed
  release, no checksum file. Treat the repo like any other
  public-domain source: read what you copy.
