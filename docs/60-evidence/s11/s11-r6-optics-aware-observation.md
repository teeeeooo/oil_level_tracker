# S11-R6 Optics-Aware Observation Evidence

**Status:** `LOCAL PASS — SECURE-WINDOWS PENDING`

**Design commit:** `87b1a16`

**Observation-owner replacement commit:** `4530312`

**Material-motion/replay commit:** `f2369ab`

## Outcome

R6 locally replaces the field-failed R5 publication owners. It does not add
another reducer. The old `SequenceTrajectoryResolver` and
`SequenceFoamEpisodeResolver` were deleted, their valid contracts were migrated,
and production now composes one Oil/state observation owner with one independent
Foam episode owner.

The local result is accepted for secure-Windows validation, not for S11 closure.
The private raster that disproved R5 is unavailable in this checkout.

## Implemented responsibility changes

- unsaturated low-chroma vertical caustics and thin wide chromatic overlays are
  explicit optics opposition in preprocessing;
- Oil hypotheses are generated without raw/current Foam masking or a Foam-front
  cutoff;
- a five-sector material path recovers low-contrast interfaces, while broad
  terminal proof and same-frame provenance bound its authority;
- repeated bright material texture cannot anchor Oil unless independently
  registered internal change distinguishes it from a fixed raster;
- FULL/EMPTY requires typed current-image likelihood; an initial state is context
  only and prior-only rows are invalid;
- Foam confirmation uses eligible coherent material plus registered internal
  evolution and is composed only after Oil/state; and
- no resolver interpolates, carries or invents an Oil coordinate.

The cleanup removed obsolete D5 Foam→Oil authority tests and private tracker
counter assertions. Retained glare, collision, low-exposure, structural-Foam and
same-frame provenance protections were rewritten against the public R6 contract.

## Deterministic four-video replay

Run:

```text
.venv/bin/python -m tests.diagnostics.s11_r6_observation_replay
```

The command uses each checked-in MP4 with its Recipe, static-artifact learning,
production detector, completed-window resolver and production report path at
`2 Hz`. It verifies exact row counts, tracking fingerprints, same-frame numeric
provenance and the explicit visual safety guards.

| Video | Window | Numeric Oil | Foam frames / episodes | Fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | `0–14.4 s` | `0/30` | `0 / 0` | `83279239b61464ebecc6d7ce04a6695d6256d288ad6ef65df2eed8833f870e6e` |
| `sample2` | `0–2.0 s` | `5/5` | `0 / 0` | `55d608e38032ab03db49cb52ad6640d3f7ed73f0c8942847c698242bb73670b3` |
| `sample3` | `30.03–105 s` | `96/151` | `10 / 1` | `01f62d65b4556d2ebb6f7e66012b505e18ab20635cd50fc55c427446884b1f0d` |
| `sample4` | `0–56 s` | `89/113` | `7 / 3` | `e7a3410e06e475e4fd63c5d8b21fd49d1071747b66eca3b7953b8bc560283e22` |
| **Total** | — | **`190/299`** | **`17 / 4`** | — |

`190/299` (`63.5%`) is observation density, not detector accuracy. It is not the
acceptance reason. The accepted reasons are source-image agreement, removal of
known false authority and explicit UNKNOWN/dashed report gaps where the image
does not support a coordinate.

Every one of the `190` numeric Oil rows carries
`SEQUENCE_SAME_FRAME_CANDIDATE`; none is interpolation or prior projection.

## Truth and blind-annotation reconciliation

| Video | Numeric / usable checked truth | MAE | Maximum error | Blind visible numeric / in-range | Foam annotation agreement |
|---|---:|---:|---:|---:|---:|
| `base_sample_1` | `0/3` | — | — | — | `7/7` absent |
| `sample2` | `3/3` | `5.5 px` | `11.0 px` | provisional file conflicts with checked truth | not scored |
| `sample3` | `2/2` | `10.0 px` | `11.0 px` | `6/6`, `3/6` in range | `6/10` |
| `sample4` | `2/5` | `4.0 px` | `7.5 px` | `13/16`, `7/16` in range | `10/10` absent interval |

Base remains wholly UNKNOWN because its checked-in short interval is weak and
then contains encoded explanatory strokes; its old truth anchors are therefore
not promoted. Sample2's older provisional no-interface labels conflict with its
checked user truth and direct images; R6 retains the visible boundary rather than
optimizing to the provisional file.

Sample3 tells the required local story: the observed line rises from about
`325 px` to the high `241–245 px` region, the moving high cap remains numeric
through approximately `49 s`, `50.02–63.53 s` stays unavailable, and the
black/reframe barrier near `67 s` remains UNKNOWN. The final report uses solid
observed runs and dashed display-only gap connections; extrema, events, captures
and CSV remain observation-only.

Sample4 publishes no Foam through the ten annotated Foam-absent anchors ending
at `33.6 s`. Its remaining unavailable intervals are bounded (`0–2.5 s`,
`46–47.5 s`, `54.5–56 s`) instead of one long fabricated trajectory.

The detailed visual decisions, including the rejected `80/113` static-threshold
variant, are recorded in the
[checked-video reconciliation](../../50-diagnostics/s11/s11-r6-checked-video-reconciliation.md).

## Regression evidence

Final local commands:

```text
.venv/bin/python -m pytest -q
# 1502 passed in 180.18s

.venv/bin/python -m tests.diagnostics.s11_r6_observation_replay
# exact counts and all four tracking fingerprints verified

.venv/bin/python -m compileall -q src tests
git diff --check
```

Controlled coverage includes saturated/unsaturated glare, encoded overlays,
static textured material, pixel-identical latent-cause collision pairs, dynamic
material twins, Foam structure/noise, global exposure changes, same-frame Oil
provenance, initial-prior release and hard-unavailable state behavior.

## Remaining gate

Run the exact pushed R6 head on the synchronized private Base/Accum video. Base
must publish zero Foam and follow the descending/recovering real interface rather
than the fixed caustic. Accum must leave initial EMPTY when image-supported Oil
enters, acquire before the mid-Glass lock-in seen in R5, retain only the bounded
turbulent Foam interval and follow the fall. Any Base false Foam episode, Accum
prior lock-in or long fixed-glare Oil track is a field FAIL regardless of nominal
coverage.
