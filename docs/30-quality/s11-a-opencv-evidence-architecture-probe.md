# S11-A OpenCV Evidence Architecture Probe

## Status and authority

- Role: S11-A OpenCV Evidence Architecture Probe Worker
- Starting authority: provisional Lane C — Independent Review
- Starting `main`: `0fd8ca0d423a1f632ad9a026d8f396686870d633`
- Probe branch: `feature/s11-a-detector-architecture-probe`
- Scope: diagnostic/test-only evidence; no production detector cutover
- Product truth: existing four repository-local `.oiltruth` files only
- Truth denominator: `15 reviewed / 13 usable / 2 unusable`

This probe does not change `src/oil_tracker`, DetectorSettings, Recipe/result/truth/debug schemas,
dependencies, temporal ownership, or any repository-local media/truth bytes.  Generated
photometric variants are metamorphic diagnostics only and never become new truth.

The complete deterministic result manifest is
`docs/30-quality/s11-a-opencv-evidence-architecture-probe-manifest.json`.
Its timing-free canonical result fingerprint is:

`9e29f0d8ebd7573b7abe5036dcbf1222f8198c1961d137f58bfcf57fabb58672`

## Direct owner / blast-radius inspection

The exact-main production path is:

1. `geometry_masks.build_mask_bundle`
2. `preprocessing.preprocess`
3. S5-A `detect_bottom_connected_foam` + `FoamTemporalGate`
4. `oil_shadow_observations.extract_raw_observations`
5. `build_bounded_proposals`
6. `evaluate_semantic_hypotheses`
7. `evaluate_typed_current_observation`
8. single serialized `OilHypothesisPipeline` / canonical reducer
9. `oil_hypothesis_projection.project_production_result`
10. fill-state projection and compatibility smoothing

The exposure-sensitive production evidence is concentrated in two current-frame owners:

- REGION_STEP / broad phase contrast uses signed band difference divided by the fixed 8-bit
  scale (`255`), so absolute phase strength can shrink with exposure.
- `_no_interface_evidence` adds absolute raw-gray `full` / `empty` state evidence directly to
  the positive no-interface likelihood and computes uniformity from raw-gray spread.

The S5-B single-frame identifiability margin, canonical typed outcome path, single temporal
owner, and S5-A Foam owner remain distinct.  The probe therefore lives under
`tests/diagnostics` and calls those owners without changing their production defaults.

## Probe variants

### P0 — exact current production evidence

P0 uses exact-main observation, semantic, no-interface, Foam, and canonical reducer behavior.
A fresh detector is used per reviewed frame so the frozen S6-D4 frame-level baseline is
comparable and independent of unrelated sequence history.

### P1 — relative/local-normalized positive phase fallback

P1 never replaces a P0 accepted boundary.  Only when the P0 current observation is ambiguous,
a bounded second evidence route is evaluated:

- REGION_STEP signed phase is `2 * (above - below) / (|above| + |below|)`, clipped to `[-1, 1]`;
- the same effective/glare masks, broad scales, raw/proposal caps, semantic formula,
  current-frame guards, Foam context, and canonical reducer are reused;
- only a canonical `ShadowBoundaryObservation` from the relative route may replace the P0
  ambiguity; no post-owner numeric Oil injection exists.

This is a mechanism probe, not a threshold search.  It asks whether local relative phase can
supply missing positive evidence while retaining existing structural guards.

### P2 — exposure-decoupled positive no-interface evidence

P2 keeps P0 phase evidence but changes only diagnostic no-interface construction:

- `full_likelihood` and `empty_likelihood` remain available as diagnostics;
- neither absolute brightness state contributes positive weight to interface absence;
- uniformity is evaluated on the already-owned normalized current frame;
- weak-boundary, visibility, glare-conflict, competing-boundary, and all downstream canonical
  acceptance thresholds remain unchanged.

Therefore a dark truth-positive frame can become `ambiguous`, but P2 cannot invent numeric Oil.

### P3 — P1 + P2

P3 combines the P2 no-interface semantics with the same P1 ambiguity-only relative phase fallback.

## Reproducible corpus identity

The manifest records SHA256 for every MP4, Recipe and `.oiltruth`.  The video SHA256 values are:

| sample | MP4 SHA256 |
| --- | --- |
| `base_sample_1` | `96cb3339cb90e8f5e7c4f71f5e5890cb12caa8996a432977413e15fe214b2c7e` |
| `sample2` | `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` |
| `sample3` | `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` |
| `sample4` | `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` |

No filename, hash, Recipe ID, or frame ID participates in detector scoring.  Those identities
exist only in the diagnostic corpus loader and result manifest.

## Photometric transformation identity

Every transform is applied to the decoded BGR frame before normal mask/preprocessing work.
Geometry and truth coordinates are unchanged.

- brightness: `round(clip(frame * factor, 0, 255))`
  - factors `1.00`, `0.80`, `0.60`, `0.45`
- gamma: `round(255 * (frame / 255) ** gamma)`
  - gamma `0.80`, `1.25`
- contrast: `round(clip((frame - 127.5) * factor + 127.5, 0, 255))`
  - factors `0.80`, `1.20`

The brightness `1.00` row is byte-identical to the native decoded frame and is the direct P0
reproduction anchor.

## P0 exact-main baseline

P0 reproduced S6-D4 exactly on current main:

- raw Oil coverage: `7/13 = 0.538462`
- matched Oil MAE: `31 / 7 = 4.428571 px`
- Foam precision: `7/7 = 1.000`
- Foam recall: `7/10 = 0.700`
- false no-interface on native truth-positive scenes: `0/13`

Native per-case Oil output:

| case | truth Oil Y | P0 | P1 | P2 | P3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| sample1 `144` | 386 | 395 | 395 | 395 | 395 |
| sample1 `156` | 386 | — | — | — | — |
| sample1 `240` | 386 | — | — | — | — |
| sample2 `0` | 592 | — | — | — | — |
| sample2 `30` | 592 | — | 599 | — | 599 |
| sample2 `60` | 592 | — | 598 | — | 598 |
| sample3 `900` | 316 | — | — | — | — |
| sample3 `1035` | 243 | 245 | 245 | 245 | 245 |
| sample4 `0` | 860.5 | 861 | 861 | 861 | 861 |
| sample4 `450` | 852.5 | 853 | 853 | 853 | 853 |
| sample4 `900` | 848.5 | 848 | 848 | 848 | 848 |
| sample4 `1470` | 855 | 866 | 866 | 866 | 866 |
| sample4 `1680` | 858.5 | 866 | 866 | 866 | 866 |

P1/P3 therefore improve native numeric coverage to `9/13`, but matched MAE becomes
`44 / 9 = 4.888889 px`.  The additional native matches are sample2 `30` at `599` (`7 px`)
and sample2 `60` at `598` (`6 px`).

## Aggregate photometric comparison

`NI` below means a truth-positive usable scene was classified as positive current-frame
no-interface.  It is therefore false no-interface for this metamorphic diagnostic.

| transform | P0 Oil / MAE / NI | P1 Oil / MAE / NI | P2 Oil / MAE / NI | P3 Oil / MAE / NI |
| --- | --- | --- | --- | --- |
| brightness `1.00` | `7/13 / 4.43 / 0` | `9/13 / 4.89 / 0` | `7/13 / 4.43 / 0` | `9/13 / 4.89 / 0` |
| brightness `0.80` | `3/13 / 6.83 / 0` | `3/13 / 6.83 / 0` | `3/13 / 6.83 / 0` | `3/13 / 6.83 / 0` |
| brightness `0.60` | `1/13 / 11.00 / 1` | `3/13 / 20.50 / 1` | `1/13 / 11.00 / 0` | `3/13 / 20.50 / 0` |
| brightness `0.45` | `2/13 / 11.00 / 3` | `3/13 / 23.50 / 3` | `2/13 / 11.00 / 0` | `3/13 / 23.50 / 0` |
| gamma `0.80` | `6/13 / 3.33 / 0` | `9/13 / 12.56 / 0` | `6/13 / 3.33 / 0` | `9/13 / 12.56 / 0` |
| gamma `1.25` | `7/13 / 11.57 / 0` | `7/13 / 11.57 / 0` | `7/13 / 11.57 / 0` | `7/13 / 11.57 / 0` |
| contrast `0.80` | `8/13 / 10.13 / 0` | `10/13 / 13.90 / 0` | `8/13 / 10.13 / 0` | `10/13 / 13.90 / 0` |
| contrast `1.20` | `6/13 / 8.33 / 0` | `7/13 / 13.57 / 0` | `6/13 / 8.33 / 0` | `7/13 / 13.57 / 0` |

Numeric retention of each variant's native-success set under brightness was poor:

| variant | native numeric anchors | `0.80` retained | `0.60` retained | `0.45` retained |
| --- | ---: | ---: | ---: | ---: |
| P0 | 7 | 2/7 | 0/7 | 0/7 |
| P1 | 9 | 2/9 | 2/9 | 1/9 |
| P2 | 7 | 2/7 | 0/7 | 0/7 |
| P3 | 9 | 2/9 | 2/9 | 1/9 |

The apparent P1/P3 retention at low brightness is not sufficient evidence: sample4 `450`
becomes `804 px` at brightness `0.60` and `0.45`, a `48.5 px` truth error.

## Important per-case deltas

### sample1 `144 / 156 / 240`

- `144` is the native non-regression anchor: all variants keep `395` at brightness `1.00`.
- At brightness `0.45`, P0/P1 produce false no-interface for `144`; P2/P3 instead preserve
  ambiguity with no numeric Oil.
- `156` and `240` remain ambiguous natively under all variants despite strong explanatory
  overlay evidence.  Relative phase therefore does not by itself solve overlay attribution.
- Photometric perturbation can make `156`/`240` numerically resolvable around `397`, but this
  is metamorphic evidence only and is not a production acceptance argument.

### sample2 `0 / 30 / 60`

- `0` remains ambiguous natively and across the brightness sweep; no variant supplies a
  sufficient independent phase explanation.
- P1/P3 recover native `30 -> 599` and `60 -> 598` while P0/P2 remain ambiguous.
- The recovery disappears under brightness `0.80 / 0.60 / 0.45`, so the tested relative
  fallback is not exposure-robust enough to be sufficient.

### sample3 `900 / 1035`

- `900` remains ambiguous natively for every variant.
- P0/P1 turn `900` into false no-interface at brightness `0.60` and `0.45`.
  P2/P3 convert both to ambiguity without numeric injection.
- `1035` is a native anchor at `245`.  P0 loses it at brightness `0.60` and becomes false
  no-interface at `0.45`; P1 recovers `245` at `0.60`; P2 prevents the `0.45` false
  no-interface but does not recover numeric Oil.

### sample4 five usable anchors

All five native Oil+Foam cases remain numeric and truth-near under all four variants.
Under brightness reduction the independent Foam detector itself loses most accepted Foam:

- brightness `1.00`: `7/10` Foam truth-positive detections
- brightness `0.80`: `1/10`
- brightness `0.60`: `0/10`
- brightness `0.45`: `0/10`

No variant changes Foam results because P1/P2 operate only on Oil evidence.  The low-brightness
sample4 `450 -> 804` P1/P3 result is a material false-boundary warning, not a success.

## False no-interface discrimination

P2 directly isolates a real semantics defect in P0:

- brightness `0.60`: false no-interface `1 -> 0`
  - sample3 `900` becomes ambiguity instead of positive no-interface
- brightness `0.45`: false no-interface `3 -> 0`
  - sample1 `144`, sample3 `900`, sample3 `1035` become ambiguity

P2 preserves native Oil `7/13`, native matched MAE `4.43 px`, and does not create numeric Oil.
This is positive evidence for a bounded no-interface semantics repair, but not sufficient S11
numeric detector recovery by itself.

## S5-B / glare / structural-Foam negative protection

The probe variants were also run directly against retained negative/protection fixtures:

| protection corpus | P0 false Oil | P1 false Oil | P2 false Oil | P3 false Oil |
| --- | ---: | ---: | ---: | ---: |
| S5-B observationally-equivalent collisions (16 scenes) | `0/16` | **`14/16`** | `0/16` | **`14/16`** |
| historical glare negatives | `0/21` | `0/21` | `0/21` | `0/21` |
| D4-style accepted-Foam + structural bands | `0/9` | `0/9` | `0/9` | `0/9` |

All nine structural-Foam probe frames retained accepted Foam (`9/9`) under every variant.

The S5-B collision result is decisive.  For seven of eight latent-cause collision pairs, P1/P3
produce the same numeric Oil for both the latent-glare and latent-Oil member.  The raster evidence
is observationally equivalent, so relative intensity normalization cannot establish the missing
causal distinction.  Accepting that output would violate the S5-B contract by converting
ambiguity into positive evidence.

Therefore P1 and P3 are rejected as production candidates in the probed form even though their
native corpus coverage is numerically higher.

## Resource and performance evidence

Deterministic retained-resource bounds did not expand:

- maximum raw observations observed: `36` (existing bound `48`)
- maximum proposals observed: `12` (existing bound `12`)
- maximum semantic hypotheses observed: `10` (existing bound `10`)
- no retained image/history/state is added
- no new dependency, schema, setting, or temporal owner is added

P0/P2 use one evidence route.  P1/P3 can execute one additional bounded relative route only when
the base current observation is ambiguous, so their deterministic compute ceiling is roughly one
extra current-frame Oil evidence pass, not additional persistent state.

One local diagnostic run observed native median per-case wall time of approximately:

- P0 `109.31 ms`
- P1 `130.78 ms`
- P2 `104.71 ms`
- P3 `129.43 ms`

Wall time is environment-dependent and is not part of the deterministic manifest fingerprint.
The useful architectural cost evidence is the bounded extra P1/P3 evidence pass above.

## Supplemental Scharr / LSD

Scharr and OpenCV LineSegmentDetector were intentionally not run.  The primary probe already
produced a stronger discriminator: P1's relative phase channel can recover two native cases but
fails the retained S5-B observational-equivalence contract.  Scharr/LSD could corroborate line
energy/geometry but cannot by themselves distinguish two retained scenes with equivalent current
observations, so running them would not change the bounded architecture conclusion.

## Architecture conclusion

**No sufficient P0/P1/P2/P3 variant is demonstrated for a production S11 detector cutover.**

- P0 remains the exact `7/13 @ 4.43 px` baseline and is highly exposure-sensitive.
- P1 improves native coverage to `9/13` but fails S5-B collisions `14/16` and produces a
  `48.5 px` low-brightness sample4 false boundary.  Reject as production candidate.
- P2 is the only variant that preserves all retained collision/glare/structural-Foam protection
  while eliminating the demonstrated low-exposure false no-interface cases.  It is a credible
  **bounded no-interface semantics repair candidate**, but it does not recover the missing numeric
  Oil boundary evidence and therefore is not sufficient for the overall S11 effectiveness gate.
- P3 inherits P1's S5-B collision failure.  Reject as production candidate.

The residual cases divide into two classes:

1. exposure can incorrectly strengthen positive no-interface semantics — P2 directly addresses
   this without inventing Oil;
2. actual Oil-vs-glare/overlay/structure attribution remains observationally underdetermined —
   the tested relative phase evidence is insufficient, and the next architecture candidate needs
   spatial consistency/path evidence or genuinely new positive temporal evidence rather than a
   stronger scalar contrast channel.

The sample1 overlay `156/240`, sample2 `0`, and sample3 `900` remain valid discrimination anchors
for that next architecture probe.

## Lane / next-gate assessment

There is no direct basis for the Worker to downgrade the requested provisional Lane C.
The probe diff itself is diagnostic/tests/documentation-only and leaves runtime defaults untouched,
but the only positive repair direction (P2) changes S5-B production observability/no-interface
semantics.  P1/P3 additionally demonstrate why accepting new positive boundary evidence touches
the canonical observability contract.

The exact next gate is therefore Orchestrator review of:

1. this probe PR's actual lane and independent-audit requirement;
2. whether to authorize a narrowly scoped P2 production semantics repair;
3. whether the remaining numeric-recovery work should open a separate spatial-consistency or new
   temporal-positive-evidence architecture probe rather than extend this branch.

Worker does not declare `AUDIT: PASS`, merge approval, or detector accuracy PASS.

## Validation evidence

### Directly executed

1. Native diagnostic probe tests:

   `./.venv/bin/python -m pytest -q tests/test_s11_evidence_architecture_probe.py`

   Result: `6 passed in 17.66s`.

   This includes:
   - direct P0 diagnostic ↔ `OpenCvPhaseDetector` parity on all 13 usable native frames;
   - exact P0 `7/13` and P1 `9/13` native delta;
   - relative/local contrast multiplicative-scale mechanism check;
   - P2 low-exposure false-no-interface conversion to ambiguity;
   - explicit P1/P3 S5-B collision failure matrix;
   - all-variant structural-Foam false-Oil closure.

2. Relevant targeted production/protection suite:

   `./.venv/bin/python -m pytest -q tests/test_s11_evidence_architecture_probe.py tests/test_oil_single_frame_observability_contract.py tests/test_oil_observability_margin_regression.py tests/test_foam_phase_detector_integration.py tests/test_oil_production_cutover.py tests/test_oil_shadow_evidence.py`

   Result: `125 passed in 25.52s`.

3. Full deterministic corpus/photometric probe:

   `./.venv/bin/python -m tests.diagnostics.s11_evidence_probe --output <temporary-json>`

   Result fingerprint (timing excluded):
   `9e29f0d8ebd7573b7abe5036dcbf1222f8198c1961d137f58bfcf57fabb58672`.

   A fresh second full run reproduced the tracked manifest byte-for-byte; tracked manifest file
   SHA256 is `8f961f9de51be7173d12e4c1bce3bbff10aa857cd51742fd966f7bc8be056a29`.

4. Diff hygiene:

   `git diff --check`

   Result: clean before final commit preparation.

### Reused evidence provenance

S6-D4's historical `7/13`, `4.43 px`, Foam `7/7` precision and `7/10` recall were used only
as navigation expectations.  P0 was re-established directly from current exact-main decoded
frames, current Recipes, current `.oiltruth`, and current `OpenCvPhaseDetector`; the reproduced
numbers match the S6-D4 record.

The retained S5-B collision and historical-glare fixture identities and the D4 structural-Foam
fixture construction are existing repository-owned regression evidence.  They were rerun directly
for this probe; no prior Worker/Auditor pass result was accepted as substitute evidence.

### Intentional non-runs

- no full canonical/E2E suite: the diff is diagnostic/tests/documentation-only and the directly
  affected Oil/Foam/observability owner suites were run instead;
- no private Windows/company field-video reanalysis: not an acceptance dependency;
- no Windows packaging/release validation: no runtime/package/dependency change;
- no new truth annotation, Recipe regeneration, benchmark catalog mutation, or MP4 rewrite;
- no Scharr/LSD supplemental probe for the architecture reason documented above;
- no spatial graph/path, optical-flow, temporal-photometric-history, ML, or segmentation work.
