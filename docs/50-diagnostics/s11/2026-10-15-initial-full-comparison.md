# Initial-FULL observation comparison

Status: local ROI preparation complete; implementation next. No Windows run or field acceptance.

The [fixed Work Plan order](../../00-project/work-plan.md#fixed-execution-order--2026-10-15)
and [bounded design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-15-initial-full-observation-comparison)
own this comparison. Original historical results and regression Recipes remain frozen.

## ROI preparation

The prior read-only review found rim points inside sample4's saved mask and whole
rectangular crops in the closed water/beer/milk path studies. Those failures do not
establish performance with an interior ROI. This run uses the local base recording
and sample4; sample2's short fixed window and quarantined sample3 remain regression
context. The closed public cup/source probes are not rerun or silently converted
into full analysis inputs.

- Local base: retain Recipe ellipse `(696, 366, 145, 148)`, margin `0.08`; stored
  full-source views show it already follows the inner sight glass. The overlaid
  High/1/3/Low graphics are internal artifacts, not outside-rim errors.
- sample4: prepare a separate comparison Recipe with ellipse `(595, 842, 37, 34)`,
  margin `0.08`, zero-line/calibration and other settings unchanged. This is an
  agent-selected inner-glass geometry from existing source views, not a physical
  boundary label. Inspect its mask at the retained beginning/middle/end frames
  before any detector comparison; preserve the original `(595, 850, 52, 52)` Recipe.
- Both use existing 2 Hz analysis windows and ordinary static preparation; explicit
  initial FULL is a mechanism stress condition for local replay, not a new physical
  truth assertion about either recording. UNKNOWN/EMPTY remain mechanical controls.
- Private Windows BASE/Accum geometry cannot be certified on Mac. The operator must
  check the interior and full movement range in Windows, save one Recipe, and use
  it for both OFF/ON runs. No private media transfer is needed.

The managed run `sample/output/s11-initial-full-roi-20261015-001` is closed with
three retained files: the separate sample4 Recipe, input/hash manifest and one
five-frame mask overlay. Source frames 0/450/900/1470/1680 were visually checked
before detector execution. At source X595, the frozen mask includes Y813/833/835/842/844
and excludes the reviewed rim Y880/882/887; geometry validation passes. These are
mask-membership checks, not new physical labels or proof of complete interface recall.
The unchanged base Recipe is reused; its duplicate copy was discarded.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: reviewed Windows checkpoints establish initial-FULL allowed-set exclusion; earliest whole-window physical loss remains unknown. ROI contamination is separately demonstrated in saved local inputs.
- Existing feature coverage: existing ellipse/margin masks and shared preprocessing are active; exclusions/templates remain empty and Local XY OFF. New comparison ROI is separate from immutable regression inputs. Static learning, session FULL confirmation and completed resolution are included in planned replay; private Windows setup remains unverified.
- Execution scope: source/ROI inspection followed by bounded local real-entry analysis and focused synthetic/integration controls. No raw Windows pixels, private-video replay, new learning operation or field acceptance. Results will be recorded after execution with exact inputs/source and runtime.
- Logic-map impact: NONE — ROI preparation and comparison preflight do not yet change the executing detector; update its optional route with the implementation step.
- Failure-registry impact: NONE — existing barrier, identity and provenance entries cover this trial; no physical failure is declared solved by preflight.
