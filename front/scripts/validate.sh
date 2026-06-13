#!/usr/bin/env bash
# validate.sh — quality gate for the front skill.
#
# Run from anywhere; the script resolves the skill root from its own location.
# Exits non-zero on any failure. Prints a one-line summary per check.
#
# Checks performed:
#   1. SKILL.md exists and has a valid frontmatter block.
#   2. SKILL.md description is between 50 and 1024 characters.
#   3. No forbidden framework imports anywhere in the skill source.
#   4. No trademarked UI-platform terms in user-facing docs.
#      (Install-context references to "Apple Silicon" are allowed inside scripts/
#       and references/alt-text-ai.md, where they're technically necessary.)
#   5. No LLM-marketing phrases (production-grade, non-negotiable, ...).
#   6. No README.md inside the skill folder (Anthropic spec).
#   7. Every reference path declared by ui-guidelines/INDEX.md exists on disk.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fail=0

note()  { printf "✓ %s\n"   "$1"; }
warn()  { printf "✗ %s\n"   "$1" >&2; fail=$((fail+1)); }
trace() { printf "  → %s\n" "$1" >&2; }

cd "$SKILL_ROOT" || exit 2

# ── 1. SKILL.md exists and has valid frontmatter ────────────────────────────
if [ ! -f SKILL.md ]; then
  warn "SKILL.md missing at $SKILL_ROOT/SKILL.md"
else
  if ! head -n1 SKILL.md | grep -qx -- '---'; then
    warn "SKILL.md does not start with '---' frontmatter delimiter"
  elif ! awk 'NR>1 && /^---$/ {print NR; exit}' SKILL.md | grep -q .; then
    warn "SKILL.md frontmatter is not closed with '---'"
  else
    note "SKILL.md frontmatter is well-formed"
  fi
fi

# ── 2. Description length ───────────────────────────────────────────────────
desc_len=$(awk '
  /^---$/ { fm = !fm; next }
  fm && /^description:/ { sub(/^description:[[:space:]]*/, ""); buf=$0; getline ln;
    while (ln !~ /^[a-z][a-z_]*:/ && ln != "---" && ln != "") { buf=buf" "ln; getline ln }
    print length(buf); exit }
' SKILL.md)
if [ -z "$desc_len" ]; then
  warn "SKILL.md frontmatter missing 'description:' field"
elif [ "$desc_len" -lt 50 ]; then
  warn "SKILL.md description is too short ($desc_len chars; need ≥ 50)"
elif [ "$desc_len" -gt 1024 ]; then
  warn "SKILL.md description exceeds 1024 chars ($desc_len)"
else
  note "SKILL.md description length OK ($desc_len / 1024 chars)"
fi

# ── 3. Forbidden framework imports ─────────────────────────────────────────
hits=$(grep -rEn --include='*.md' --include='*.html' --include='*.mjs' --include='*.js' \
  -e 'from[[:space:]]+["'"'"']react' \
  -e 'from[[:space:]]+["'"'"']vue' \
  -e 'from[[:space:]]+["'"'"']svelte' \
  -e 'from[[:space:]]+["'"'"']solid-js' \
  -e 'from[[:space:]]+["'"'"']next' \
  -e 'from[[:space:]]+["'"'"']nuxt' \
  -e 'from[[:space:]]+["'"'"']@angular' \
  -e 'require\(["'"'"']react' \
  -e 'require\(["'"'"']vue' \
  . 2>/dev/null)
if [ -n "$hits" ]; then
  warn "Framework import detected:"
  echo "$hits" | head -10 | while read -r line; do trace "$line"; done
else
  note "No framework imports"
fi

# ── 4. Trademarked UI-platform terms in user-facing docs ───────────────────
hits=$(grep -rEn --include='*.md' --include='*.html' \
  --exclude-dir=scripts \
  -e '\bApple\b' -e '\bApple Silicon\b' -e '\biOS\b' -e '\biPadOS\b' \
  -e '\bmacOS\b' -e '\bwatchOS\b' -e '\btvOS\b' -e '\bvisionOS\b' \
  -e 'SF[[:space:]]*Pro' -e 'SF[[:space:]]*Mono' -e 'SF[[:space:]]*Symbol' \
  -e 'San[[:space:]]*Francisco' -e '\bHIG\b' \
  . 2>/dev/null \
  | grep -v 'references/alt-text-ai.md' \
  | grep -v 'foundations/images.md.*Apple Silicon' \
  | grep -v 'foundations/images.md.*ollama' )
if [ -n "$hits" ]; then
  warn "Trademarked UI-platform term in user-facing docs:"
  echo "$hits" | head -10 | while read -r line; do trace "$line"; done
else
  note "No trademarked UI-platform terms in user-facing docs"
fi

# ── 5. LLM-marketing phrases ───────────────────────────────────────────────
hits=$(grep -rEn --include='*.md' \
  -e '\bproduction-grade\b' -e '\bnon-negotiable\b' \
  -e '\bworld-class\b' -e '\bcutting-edge\b' -e '\bstate-of-the-art\b' \
  -e '\bseamlessly\b' -e '\beffortlessly\b' -e '\bgracefully\b' \
  -e '\bleverages?\b' -e '\bempowers?\b' \
  -e '\brobust\b' -e '\bcomprehensive\b' -e '\bturnkey\b' \
  . 2>/dev/null)
if [ -n "$hits" ]; then
  warn "LLM-marketing phrase detected:"
  echo "$hits" | head -10 | while read -r line; do trace "$line"; done
else
  note "No LLM-marketing phrases"
fi

# ── 6. No README.md inside the skill folder ────────────────────────────────
if [ -f README.md ]; then
  warn "README.md exists inside the skill folder (Anthropic spec forbids it)"
else
  note "No README.md inside the skill folder"
fi

# ── 7. Every reference path declared by INDEX.md exists ────────────────────
idx="references/ui-guidelines/INDEX.md"
if [ -f "$idx" ]; then
  missing=0
  while IFS= read -r rel; do
    [ -e "references/ui-guidelines/$rel" ] || { warn "INDEX.md references missing file: $rel"; missing=$((missing+1)); }
  done < <(grep -oE '`[a-z][a-z0-9_/-]*\.md`' "$idx" | tr -d '`' | sort -u)
  [ "$missing" = 0 ] && note "All ui-guidelines/INDEX.md paths exist"
fi

# ── Summary ────────────────────────────────────────────────────────────────
echo
if [ "$fail" -eq 0 ]; then
  echo "PASS — skill is shippable."
  exit 0
else
  echo "FAIL — $fail check(s) failed."
  exit 1
fi
