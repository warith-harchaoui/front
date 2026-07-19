---
name: front-ux-laws
description: >-
  Apply the canonical Laws of UX (Jon Yablonski, lawsofux.com) to vanilla-JS +
  Tailwind work — both when making new UI ("design this screen using Hick /
  Fitts / Miller", "what does Peak-End say here", "is this onboarding fighting
  the Paradox of the Active User") AND when auditing existing HTML ("audit for
  Laws of UX", "is my nav too Hick-heavy", "check my form for Postel /
  Tesler", "too many choices / options", "cognitive load", "Doherty
  threshold", "reduce clutter"). Reference covers 30 laws with trigger /
  action / Tailwind hook. Static auditor scripts/audit_laws_of_ux.py flags the
  mechanically-detectable subset (Hick, Miller, Fitts, Jakob, Tesler,
  Aesthetic-Usability, Selective Attention, Doherty, Choice Overload) with
  severity and JSON output. Pairs with companion skills front-ui (generation),
  front-accessibility (a11y lint), front-publish (docs site), front-colors
  (contrast). Output is HTML-aware findings via JSON or stdout, exit codes for
  pre-commit / CI.
license: BSD-3-Clause
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. The auditor needs
  Python 3.9+ stdlib only (html.parser, argparse, json). No network
  access required. Reference is plain Markdown with no exec deps.
metadata:
  author: Warith Harchaoui
  version: 0.25.0
  source: https://lawsofux.com/
---

# front-ux-laws — make and audit by the Laws of UX

## Audience and positioning

Solo developers and small teams who:

- Want a **shared vocabulary** for UI decisions ("we're trading Hick
  for Doherty here") without re-deriving cognitive science from
  scratch each time.
- Want a **pre-commit auditor** that fails fast when emitted HTML
  violates a mechanically-detectable law (an 11-link `<nav>`, an
  unchunked IBAN, a clickable `<div>` masquerading as a button).
- Need the rules without buying the book — the skill restates each
  law's trigger and action and points at the primary sources
  (Yablonski's lawsofux.com plus Nielsen Norman Group and the
  Wikipedia critique of Postel's Law).

This skill is **not** a substitute for usability testing. The
Aesthetic-Usability Effect itself warns that beauty can mask real
bugs ([NN/g, 2024](https://www.nngroup.com/articles/aesthetic-usability-effect/));
pair this skill with axe-core / Pa11y / Lighthouse and behavioural
observation in real user sessions.

## Two modes — make and audit

The `front-*` repo is a toolkit for **making** UI and **auditing**
the result. This skill ships both halves of that loop for the Laws
of UX specifically:

| Mode | Tool | When to load |
|---|---|---|
| **Make** — pick the right law for a screen | `references/laws-of-ux.md` | At generation time. The reference is structured for in-conversation lookup: trigger → action → Tailwind hook. Load it once per design surface; pick ONE law to apply, not five. |
| **Make** — auto-fix mechanically-fixable violations | `scripts/audit_laws_of_ux.py --fix` | Closes the audit↔make loop: every violation that can be repaired by a one-line text edit is fixed in place (Fitts adds `min-h-11`; Aesthetic-Usability adds `focus-visible:ring-2`; Miller chunks long digit runs with NBSP; Jakob rewrites `<div>` / `<span>` to `<button>`). Iterates until convergence; idempotent. |
| **Audit** — fail the build on detectable violations | `scripts/audit_laws_of_ux.py` | Pre-commit, pre-merge, CI. Static parser, no browser, no network. Findings come as `error` or `warning`; exit non-zero only when an `error` is found unless `--strict` is set. |

## Decision tree

| Trigger phrase | Mode | Run |
|---|---|---|
| "design / build / make this screen using Hick / Fitts / Miller / Jakob / Tesler / Peak-End" | make | Load `references/laws-of-ux.md`, jump to the relevant bucket, apply the **smallest concrete change** the law asks for. |
| "what does the Laws of UX say about this onboarding flow" | make | Load reference, walk the **Time** + **Memory** buckets. |
| "is this a dark pattern" | make | Stop here, hand to `front-ui/references/anti-patterns.md`. |
| "audit this page / component / dir for Laws of UX" | audit | `python scripts/audit_laws_of_ux.py <file-or-dir>` |
| "auto-fix the easy ones" / "make my UI pass the Laws of UX" | make | `python scripts/audit_laws_of_ux.py --fix <file-or-dir>` — applies the four mechanical fixers (Fitts / Aesthetic-Usability / Miller / Jakob) in place. Add `--dry-run` to preview. |
| "fail the build on Hick / Jakob violations" | audit | `python scripts/audit_laws_of_ux.py --only hick,jakob --strict <dir>` |
| "JSON for CI" | audit | `python scripts/audit_laws_of_ux.py --json <dir>` |
| "false positive on Tesler / Miller" | audit | `python scripts/audit_laws_of_ux.py --ignore tesler,miller <dir>` |

## Implemented audit checks

Each check maps to one law in the canonical set. The trigger column
states the heuristic the static parser uses (not the law's full
definition — that lives in the reference). False-positive rate is
the auditor's best-effort qualitative estimate against the
front-ui starter components.

| Law | Severity | What the static parser flags | False positives to expect |
|---|---|---|---|
| Hick's Law | error | `<nav>` exposing > 7 top-level *logical* choices (radiogroups / tablists collapse to one) | Rich app shells with a documented "More" menu and a deliberate top-level surface area. |
| Choice Overload | warning | A `<div>`/`<section>` with `pricing`/`plans` + `grid`/`flex` in its class list and > 4 direct column children | A genuine four-tier B2B price table where each tier is concrete; mark with `--ignore choice-overload`. |
| Miller's Law | warning | A visible alphanumeric run ≥ 8 chars in body text | English words 8–12 chars are excluded; CSS class hashes in `class=""` attributes are stripped before scanning. |
| Jakob's Law | error | `<div>` / `<span>` with `onclick=` / `role="button"` / `cursor-pointer` and no real interactive child | Wrappers that contain a real `<button>` / `<a>` are exempt. |
| Fitts's Law | warning | Interactive element with no `min-h-11+` / `h-11+` / `size-11+` Tailwind class | Plain text links inside paragraphs (heuristically exempted). |
| Aesthetic-Usability | warning | Interactive element without `focus-visible:ring-*` or `focus:ring-*` | Type=hidden inputs are exempted. |
| Selective Attention | warning | `<span>` whose only signal is `text-red-*` / `text-green-*` and whose visible text is not a status word, with no icon child | Spans that contain a status word ("Failed", "OK", …) or an `<svg>`/`<img>` child are exempted. |
| Tesler's Law | warning | `HH:MM` time string with no timezone token (`UTC`, `+02:00`, `Europe/Paris`, `Z`, named TZ) within 40 chars | Durations like "Took 14:30" — silence with `--ignore tesler`. |
| Doherty Threshold | — | Out of scope for static analysis. Use Lighthouse + a real device. | — |

## Examples

### Make — apply Hick + Fitts to a primary CTA

User: "Design a hero CTA for a settings page that respects Hick + Fitts."

1. Load `references/laws-of-ux.md`, *Decision* and *Aesthetics*
   buckets.
2. Hick says one obvious choice; Fitts says 44 px min hit area.
3. Emit:

```html
<button class="inline-flex min-h-11 items-center justify-center gap-2
               rounded-full bg-brand-blue px-5 py-3 text-[17px]
               font-semibold text-white hover:opacity-90
               active:scale-[0.97]
               focus:outline-none focus-visible:ring-2
               focus-visible:ring-brand-blue
               focus-visible:ring-offset-2
               focus-visible:ring-offset-surface-primary
               motion-reduce:active:scale-100">
  Save changes
</button>
```

### Audit — pre-commit on the components dir

```bash
python front-ux-laws/scripts/audit_laws_of_ux.py \
  --strict --json \
  front-ui/assets/components/ > .audit.json
test -s .audit.json && jq length .audit.json
```

CI fails on any finding when `--strict`. Drop `--strict` to let
warnings pass and only fail on real errors (Hick, Jakob).

## Tool composition

- When generating new HTML: invoke this skill's reference at design
  time; rerun the auditor on the emitted file as a self-check before
  returning code.
- When auditing existing HTML emitted by `front-ui`: run the
  auditor first, then load the reference for any flagged law to
  draft a fix.
- When the audit reports Selective-Attention warnings, also run the
  `front-accessibility` lint — the a11y skill catches the same family of
  bugs from a different angle (color-only state, missing alt,
  unlabelled inputs).

## References

- `references/laws-of-ux.md` — canonical Yablonski set (30 laws),
  trigger → action → Tailwind hook. Reads as both a make-time
  playbook and an audit-time refusal list. Load it on demand; not
  preloaded.

## Scripts

- `scripts/audit_laws_of_ux.py` — Python 3.9+ stdlib-only static
  auditor. Run `--help` for the full flag list (`--json`, `--strict`,
  `--only LAW1,LAW2`, `--ignore LAW1,LAW2`).

## Attribution

Concept names and the curated set are © Jon Yablonski under
CC-BY-NC-SA 4.0 (lawsofux.com). Restatements in
`references/laws-of-ux.md` are fair commentary; cite the source when
surfacing a law to a user.
