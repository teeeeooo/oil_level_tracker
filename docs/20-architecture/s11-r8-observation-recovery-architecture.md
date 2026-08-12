# S11-R8 Observation-Recovery Architecture

## Purpose

R8 exists to make the final Oil/Foam graph useful without converting glare,
rim, scratches, haze or a prior state into measured coordinates. Base and Accum
are validation failure classes, not separate detector modes. One detector and
one completed-window resolver serve every Glass.

## Observation ownership

Oil and Foam are independent observations. A Foam score, mask or
`material_texture_conflict` cannot veto Oil authority. An eligible Foam front
may apply a comparative local penalty to a coincident Oil proposal, but cannot
remove the only Oil candidate. A confirmed Foam episode is published even when
state remains `UNKNOWN_REVIEW`; it never fabricates Oil or makes that state
valid. If the Foam trajectory repeatedly aliases a very strong Oil boundary,
the public Foam episode is rejected and the raw candidates remain in trace with
`R8_FOAM_OIL_ALIAS_REJECTED`.

Static topology remains safety evidence. R8 does not globally zero material
topology. A cross-representation material front without registered Oil motion
remains candidate-only. With registered Oil motion and coverage, a material path
may fall through the no-semantic-corridor branch into continuation, but cannot
gain direct anchor authority from motion alone.

## High-recall representation

R8 adds two bounded lanes:

1. a raster-only material path independent of the Foam material map; and
2. one D2-derived distributed weak-Sobel proposal hidden behind stronger rows.

Both are additive. They do not consume the ordinary top-k budget, directly seed
semantic authority or anchor a trajectory without independent motion or anchor
graph support. No global boundary, ambiguity or artifact threshold is lowered.

Dynamic continuation may extend before a qualified anchor for at most twice the
configured Oil path horizon. Every published point still comes from an eligible
candidate in that exact frame. Extrema, events and captures retain anchor-grade
authority.

After an observed rise reaches the top entrance and disappears for the bounded
completed-fill gap, an upper material cap cannot release the barrier by position
alone. Reacquisition also needs a short same-frame candidate path progressing
downward into the Glass. This rejects turbulent cap motion while allowing a
missed drain entrance; it is inactive unless completed-fill history exists.

## User artifact calibration

The ellipse editor runs the same detector on the displayed source frame and
offers at most ten point/line boundary proposals plus bounded glare regions.
Nothing changes until the user selects a proposal and applies the editor.

Selected artifacts are stored in normalized ellipse coordinates as point, line
or region templates. Matching requires vertical and horizontal geometric
agreement; selecting one row does not suppress the same Y everywhere. A match:

- stays in raw/debug candidate data;
- receives `calibrated_artifact:<template-id>` provenance;
- is ineligible for Oil/Foam publication; and
- cannot consume the normal candidate budget. The generator adds at most three
  bounded replacement slots when calibration templates exist.

If exclusion leaves no supported observation, output remains
`UNKNOWN_REVIEW`. Calibration never proves FULL, EMPTY, Oil or Foam.

## Initial state and graph semantics

A current-run confirmed FULL/EMPTY prior never creates numeric Oil. If no public
Oil is observed anywhere and no direct opposite state appears, presentation
holds the confirmed initial state through the analysis end as a labeled graph
background. Raw samples, numeric fields and observed coverage remain unchanged.
The graph and report explicitly label this as an assumption, not an observation.
Presentation-only hold samples are not passed to event detection or judgment.

If later anchor-grade Oil exists, the established direction-compatible leading
prefix reconstruction applies. A contradiction yields review rather than a
state hold.

## Performance boundary

R8 keeps candidate counts bounded. Repeated material-path sliding windows and
sector phase extraction use vectorized array operations rather than Python
row loops. Performance validation measures debug-disabled detector time and
requires semantic output equality for optimization-only changes.

## Prohibited shortcuts

- no Glass/video/time-specific branch;
- no globally lowered Oil/Foam thresholds;
- no stale coordinate carry or numeric interpolation;
- no initial-state coordinate;
- no entire-Y artifact exclusion;
- no final Foam solely from static whiteness/texture/coherence; and
- no hiding missing observations in smoothing, events or graph rendering.
