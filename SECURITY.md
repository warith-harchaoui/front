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
- Bundled fonts ship under their own license (Roboto, Roboto Serif,
  Roboto Mono: all SIL OFL). See `LICENSE.md` for the carve-out.
- **Distribution channels.** Two supported install paths:
  1. **Tagged GitHub release** (recommended). Each release ships
     per-skill tarballs, a four-skill bundle tarball, and a single
     `SHA256SUMS` file built by `scripts/release.sh` and published by
     the `release.yml` workflow on every `v*.*.*` tag push. Users
     verify with `shasum -a 256 -c SHA256SUMS` (or `sha256sum -c`)
     before extracting — README's *Install* section walks the full
     flow.
  2. **`git clone` + `cp -r`** (developer / contributor path). No
     verification step beyond `git fsck`. Documented in
     `CONTRIBUTING.md`.
- **What we don't sign yet.** Release artifacts carry SHA-256 checksums
  but are **not GPG-signed** and are **not Sigstore-attested**.
  Treat the checksum as integrity proof against transport corruption,
  not as authenticity proof of the maintainer. If you need
  authenticity, build from a tagged commit you've reviewed yourself
  (the `release.yml` workflow is in-tree and reproducible).
- **What lives in the supply chain.** Direct upstream registries:
  PyPI (`pip install -r requirements-dev.txt`), the Ollama registry
  (model pulls), Hugging Face mirrors (whisper.cpp model files), the
  jsDelivr `gh` proxy (Tailwind Play CDN in prototype mode). No
  vendored binaries, no auto-updaters.
- **Trust model — short version.** This repo ships text and Python
  scripts you can read top-to-bottom in under an hour. Read what you
  install. The validators (`scripts/validate_all.py`,
  `front-ui/scripts/validate.py`) and the deterministic test suite
  (`pytest`) run with stdlib + PyYAML only and never touch the
  network; running them locally is a cheap way to confirm an install
  is what it claims to be.
