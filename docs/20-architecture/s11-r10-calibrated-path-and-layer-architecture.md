# S11-R10 Calibrated Path and Layer Architecture

## Purpose

R10 recovers slow, intermittently evidenced Oil motion after explicit user
Artifact calibration and preserves independently confirmed Foam as a distinct
material layer. Base and Accum are evidence classes handled by one generic
detector and sequence resolver; no Glass, filename, timestamp or private-video
branch is allowed.

The R9 architecture remains the compatibility baseline except where this
document explicitly replaces its dynamic-path, Foam-alias, graph and Artifact
editor contracts.

## User Artifact calibration editor

**분석 영역 편집** uses a user-resizable horizontal splitter:

- the left pane owns video, ellipse, zero line and exclusion editing;
- the right pane owns Artifact explanation, proposal actions, status, proposal
  list and saved-template list; and
- global apply/cancel remains fixed outside the splitter.

**Detector 후보 찾기**, select-all and bulk apply are visible without scrolling
at the minimum supported dialog size. Only the list body may need scrolling.
Selection continues to highlight the exact source point/line/region. The dialog
exposes normal resize/maximize affordances, and resizing or dragging the
splitter cannot overlap either pane.

Detector proposals remain suggestions. Only explicit user selection plus
dialog/Profile apply creates normalized Artifact templates.

## Calibration-only proposal budget

R10 retains a bounded calibration-only high-recall pool. It keeps strong rows
but reserves part of the same fixed budget for vertically distributed local
peaks so one cluster of strong structures cannot remove every weaker Oil row.
This is budget reallocation, not unbounded proposal growth or global threshold
lowering.

Calibration rows:

- exist only when at least one user template is saved;
- remain outside ordinary top-k, semantic and cross-representation authority;
- are hard-rejected when matching a saved Artifact template;
- carry their original same-frame raster/motion evidence; and
- cannot publish Oil unless the calibrated path resolver promotes their exact
  same-frame row.

## Sparse-keyframe long-horizon bootstrap

R10 bootstrap remains disabled when the ordinary candidates already form a
qualified anchor path. Otherwise it considers only non-rejected calibrated
continuation rows outside eligible Foam proximity.

Candidate-local motion support is a keyframe signal, not a requirement on every
path member. A bounded path may bridge short missing-motion gaps using
continuation rows when Y displacement remains cadence-plausible. Promotion
requires all of the following at path level:

- explicit user Artifact calibration;
- at least two registered-motion keyframes with adequate coverage;
- a minimum bounded observation duration and member count;
- cumulative vertical span of at least the existing scale-aware movement floor;
- dominant direction consistency;
- no calibrated Artifact match, excessive ambiguity, track opposition or
  eligible-Foam alias;
- a unique best path under the competition margin; and
- same-frame candidate provenance for every published Oil value.

Bridging does not interpolate a coordinate. Frames without a retained path
member remain non-numeric. A static path cannot satisfy cumulative span, and
two similarly credible paths leave the sequence unresolved.

## Independent Oil/Foam layer identity

Oil temporal jump tolerance and Oil/Foam identity tolerance are separate.
Confirmed dynamic Foam above selected Oil is a legitimate layered observation,
including a thin layer. Alias hard rejection is limited to repeated
near-coincident boundaries under a small scale-bounded identity tolerance.

When separation exceeds identity tolerance, both selected Oil and confirmed
Foam remain public. Uncertain proximity may carry a review/possible-alias flag,
but it must not erase a materially changing confirmed episode solely because
Oil exists nearby. Foam still cannot create or move Oil/state authority.

## Graph observation contract

Every finite stored Foam observation is rendered as a visible point regardless
of whole-sample `is_valid`. Consecutive Foam observations may retain the dashed
line. Isolated observations and observations separated by missing rows remain
separate markers; no coordinate is fabricated across a gap.

Static report graphs and interactive Result Review graphs share this behavior.
Invalid/unknown state remains available through review styling and intervals,
not through removal of the Foam coordinate.

## Trace and performance

Final sequence diagnostics expose whether calibrated rows were path members,
registered-motion keyframes or promoted seeds. Existing authority, cluster,
trajectory, reject-stage and artifact-rejection provenance remains intact.

The calibrated proposal count and retained alternatives remain bounded.
Long-horizon path search must use bounded dynamic programming rather than
quadratic all-path enumeration. Debug-disabled timing is compared on the same
input and machine; UI layout and graph markers add no detector-frame work.

## Prohibited shortcuts

- no automatic acceptance of detector Artifact proposals;
- no global Oil or Foam threshold reduction;
- no Base/Accum/private-video special mode;
- no static or competing calibrated path promotion;
- no numeric Oil carry, interpolation or initial-state coordinate;
- no Foam deletion based on Oil temporal jump tolerance; and
- no suppression of finite confirmed Foam merely because whole-sample validity
  is false.
