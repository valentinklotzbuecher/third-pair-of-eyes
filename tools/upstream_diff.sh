#!/usr/bin/env bash
# upstream_diff.sh — what changed in research_skills since this suite was derived from it.
#
#   tools/upstream_diff.sh [path to a research_skills clone] [--full]
#
# Reads the base commit from .claude/skills/UPSTREAM.md, fetches the clone, and prints the
# upstream CHANGELOG since then and the files changed among those this suite derives from
# (with --full, their diffs). Port what applies by hand; see UPSTREAM.md.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
clone="${1:-$here/../research_skills_}"
full="${2:-}"
base="$(grep -oE '[0-9a-f]{40}' "$here/.claude/skills/UPSTREAM.md" | head -1)"
if [ ! -d "$clone/.git" ]; then
  echo "No research_skills clone at $clone." >&2
  echo "Clone one: git clone https://github.com/valentinklotzbuecher/research_skills_ $clone" >&2
  exit 2
fi
git -C "$clone" fetch --quiet origin || echo "(fetch failed; using the local clone as is)" >&2
head="$(git -C "$clone" rev-parse origin/main 2>/dev/null || git -C "$clone" rev-parse HEAD)"
echo "Upstream base ${base:0:7} → current ${head:0:7}"
if [ "$base" = "$head" ]; then echo "No upstream changes."; exit 0; fi
tracked=(review/SKILL.md review/paper review/code-and-data review/claims review/challenge
         review/verdict review/modules/experiment-diagnostics review/modules/small-n-diagnostics
         review/modules/whimsical-assumptions-diagnostics
         review/modules/quantitative-model-diagnostics review/modules/controls-samples-diagnostics
         review/references review/assets review/scripts/check_manifest.py
         review/scripts/check_suite_version.py review/spec-changes.csv
         audit-review review-digest LICENSE)
echo; echo "== Upstream CHANGELOG since ${base:0:7} =="
git -C "$clone" diff "$base" "$head" -- CHANGELOG.md | sed -n 's/^+\([^+]\)/\1/p'
echo; echo "== Changed files this suite derives from =="
git -C "$clone" diff --stat "$base" "$head" -- "${tracked[@]}"
if [ "$full" = "--full" ]; then
  git -C "$clone" diff "$base" "$head" -- "${tracked[@]}"
fi
