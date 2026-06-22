# The Unlicense

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any copyright interest in the software to
the public domain. We make this gift to the public at large and to the
detriment of our heirs and successors. We intend this gift to be an
irrevocable relinquishment in perpetuity of all copyright interest in
the software to this software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>.

---

## Bundled third-party assets

The Unlicense above applies to the source of this repository. Bundled
third-party assets retain their own licenses:

- **Roboto / Roboto Serif / Roboto Mono** (typefaces) — bundled in
  `front-ui/assets/fonts/roboto/`, `front-ui/assets/fonts/roboto-serif/`,
  and `front-ui/assets/fonts/roboto-mono/` under the **SIL Open Font
  License (OFL)** (the "three-Roboto rule"). The full license and its
  required copyright notice are in the `OFL.txt` shipped in each of the
  three folders. This is unaffected by the public-domain dedication
  above; OFL is permissive but its terms apply to the font files.

- **Common Voice audio clips** — extracted into
  `tests/fixtures/audio/cv/<lang>/` from Common Voice 26.0, obtained
  via [Mozilla Data Collective][mdc] under the dataset's **CC0 1.0
  Universal** dedication (public domain). The clips themselves are
  redistributable for any purpose, commercial or non-commercial, with
  no attribution requirement. Attribution to Mozilla and the Common
  Voice contributors is provided here as good practice, not as a
  license obligation. Per the Mozilla Data Collective platform terms
  and the spirit of contributor consent, **we do not attempt to
  identify or re-identify speakers**; the per-language `MANIFEST.json`
  records the Common Voice opaque `client_id` hash for reproducibility
  only, never raw identifiers. Contributors withdrawing consent
  upstream should refresh fixtures by re-running
  `tests/fixtures/audio/extract_cv_subset.py` against the latest
  release.

[mdc]: https://mozilladatacollective.com/organization/cmfh0j9o10006ns07jq45h7xk
