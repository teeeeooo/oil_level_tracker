#!/usr/bin/env bash
# Re-run saved-output audits. No detector rewrite, commit, push, or Windows operation.
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo 'Usage: bash reproduce.sh /absolute/repository /new/output/directory' >&2
  exit 2
fi
ROOT="$(cd "$1" && pwd)"
OUT="$2"
EXPECTED=5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6
if [[ "$OUT" != /* || -e "$OUT" ]]; then
  echo 'Output must be an absolute, non-existing path.' >&2; exit 2
fi
if [[ "$(git -C "$ROOT" rev-parse HEAD)" != "$EXPECTED" ]]; then
  echo 'Wrong HEAD. Read the current Work Plan; do not automatically checkout/reset.' >&2; exit 2
fi
if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then
  echo 'Working tree differs. Preserve user work and reconcile scope before running.' >&2; exit 2
fi
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then echo 'Repository .venv Python is required.' >&2; exit 2; fi
RUNS="$ROOT/sample/output/s11-p5-default-linkage-20261011-001"
if [[ ! -d "$RUNS" ]]; then
  echo 'Saved ignored source artifacts are required. This ZIP is not a media/trace bundle.' >&2; exit 2
fi
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$OUT"
unset PYTHONOPTIMIZE
cd "$ROOT"
"$PY" "$HERE/audit_s2_decision_geometry.py" --root "$ROOT" --out "$OUT/s2-decision-geometry.json" | tee "$OUT/s2-decision-geometry.log"
"$PY" docs/50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/verify.py --root "$ROOT" --output "$OUT/s2-reverification.json" | tee "$OUT/s2-reverification.log"
"$PY" docs/50-diagnostics/s11/2026-10-11-p5-default-linkage/verify.py --root "$ROOT" --runs "$RUNS" --output "$OUT/default-reverification.json" | tee "$OUT/default-reverification.log"
"$PY" docs/50-diagnostics/s11/2026-10-11-p2-shared-support/verify.py --readout docs/50-diagnostics/s11/2026-10-11-p2-shared-support/readout.json --out "$OUT/p2-reverification.json" | tee "$OUT/p2-reverification.log"
QT_QPA_PLATFORM=offscreen "$PY" -m pytest -q \
 tests/unit/test_s11_spatial_conjunction.py \
 tests/unit/test_s11_side_texture_probe.py \
 tests/unit/test_s11_shared_support_roles.py \
 tests/unit/test_s11_reference_constellation.py \
 tests/unit/test_s11_current_boundary_reference.py \
 tests/unit/test_s11_ordered_patch_correspondence.py \
 tests/unit/test_s11_foam_front_alternatives.py \
 tests/unit/test_s11_foam_gap_brackets.py \
 tests/unit/test_s11_support_boundary_faces.py \
 tests/test_s11_replay_provenance.py \
 tests/test_foam_component_diagnostics.py | tee "$OUT/focused-tests.log"
"$PY" scripts/check_detector_governance.py --base-ref "$EXPECTED" --include-worktree
git diff --check
git rev-parse HEAD
git status --short
