# S11 Transparent-Interface Detector Direction Assessment

**Assessment date:** 2026-09-17
**Assessment status:** completed design decision; no production behavior or field
acceptance is changed by this document.
**Current runtime:** `opencv-phase-detector-r22-2-interface-path-diagnostics-v1`.
**Field disposition:** `FIELD FAIL` remains in force.

## Decision

Do **not** rewrite the whole detector and do **not** continue tuning scalar
thresholds in the current candidate/tracklet/lifecycle pipeline.

Proceed with a **bounded redesign of the observation layer** from
`FRAME-EVIDENCE` through `OIL-CANDIDATE`:

1. represent a possible liquid interface as a spatial contour with per-sector
   localization uncertainty instead of treating one median row as the physical
   object;
2. build one typed, current-frame interface witness from multiple local cues and
   explicit derivation lineage;
3. represent insufficient optical information as `UNOBSERVABLE`/`UNRESOLVED`,
   distinct from FULL, EMPTY and “candidate rejected”;
4. allow tracklet association, authority and lifecycle to consume that witness
   only after shadow-mode discrimination is validated; and
5. evaluate controlled illumination/background modes in parallel, because a
   transparent Oil/refrigerant interface can be absent from the passive RGB
   image rather than merely missed by a weak algorithm.

Retain the existing bounded candidate beam, exact same-frame provenance,
Oil/Foam independence, fail-closed publication, tracklet/lifecycle ownership,
selector/projection contracts and report pipeline. Those layers contain useful
safety constraints, but reviewed phase/owner exclusion remains a separate
failure mechanism. The public frame-local probe cannot exclude downstream causes.

The implementation contract for the observation redesign is the
[Interface Observability Witness Architecture](../../20-architecture/s11-interface-observability-witness-architecture.md)
and its [trace/shadow validation contract](../../30-validation/s11-interface-observability-witness-validation.md).
It refines item 1 of the broader
[Physical Interface Evidence Repair Design](../../20-architecture/s11-physical-interface-evidence-repair-design.md);
it does not activate that proposal's association, handoff or initial-FULL
behavior.

## Why this is a redesign rather than another detector revision

### Repository history

S11 revisions have progressively improved candidate fairness, typed evidence,
authority, physical tracklets, phase lifecycle, loss handling, owner handoff,
selection provenance and diagnostics. Those changes made failures more
observable and constrained unsafe recovery, but they did not create optical
information that is absent or distinguish every visible line from the true
Oil/refrigerant interface.

The remaining recurring mechanisms are upstream:

- `S11-F02`: the true interface is absent from the proposal lattice or only a
  weak member among many visually plausible structures;
- `S11-F04`: nearby stripes/reflections and the real interface can be associated
  as one identity, while source family, polarity and recurrence are not physical
  identity;
- `S11-F05`: broad material/texture summaries can reject a real textured
  interface or admit an internal structure; and
- `S11-F06`/`S11-F09`: multiple descendants of one raster measurement look like
  independent support unless measurement lineage is explicit.

R22-2 exposes existing native material-path geometry but deliberately leaves
`classification` and `independent_support` unevaluated. The rejected R23
experiment then demonstrated that even three common sectors with opposite gray
polarity cannot safely split identities: protected public observations regressed,
and a genuine translated curve with photometric reversal was split. That result
rules out another polarity/source/motion shortcut, not the full contour/context
direction.

### Reviewed private-Windows evidence

The reviewed R22 checkpoints expose two different failure classes:

- an Accum boundary near the reviewed Oil interface is present as a candidate,
  but broad texture/peer gating and existing ownership prevent it from becoming
  the selected owner; and
- BASE contains curved/localized interface evidence whose sector positions do
  not equal one scalar candidate Y. A nearby point was reviewed as a localization
  mismatch, not as a certified different physical structure.

Therefore a scalar row cannot be treated as the whole physical identity, and a
location error cannot be silently converted into a material-negative label.
The private evidence is sufficient to motivate a better measurement contract,
but not sufficient to choose operating thresholds.

## Public observability probe

A new non-production probe was added at
`tests/diagnostics/s11_interface_witness_probe.py`. It runs the existing R22-2
candidate generation and trace measurements on every usable checked-in Oil
truth annotation, using a fresh detector per frame. It does not learn a static
map, resolve a completed sequence, classify a witness or mutate detector
behavior.

The compact machine result is
[`s11-interface-witness-public-probe-summary.json`](s11-interface-witness-public-probe-summary.json).
The uncommitted full result is reproducible from the script and its SHA-256 is
recorded in that summary.

```bash
PYTHONPATH=src:. .venv/bin/python \
  tests/diagnostics/s11_interface_witness_probe.py \
  --transforms original,brightness_0.80,brightness_1.20,gamma_0.80,gamma_1.25,contrast_0.80,contrast_1.20 \
  --output /tmp/s11-interface-witness-public-probe.json
```

### Scope

- 13 usable truth frames from the four authoritative public videos;
- original image plus brightness 0.80/1.20, gamma 0.80/1.25 and contrast
  0.80/1.20 transforms;
- 91 frame/transform measurements total;
- exact frozen video/Recipe/truth hashes verified against the existing corpus
  manifest;
- `near_truth_geometry` means only `|candidate_y - truth_y| <= 8 px`; it is not
  a physical-identity label;
- rows at least 24 px away are named
  `remote_geometry_not_proven_negative`, not “false candidates.”

### Result

| Measure | Original | Range across all seven image variants |
|---|---:|---:|
| truth frames with a candidate within 8 px | 13 / 13 | 13 / 13 for every variant |
| nearest-candidate median error | 1.0 px | 1.0–1.5 px |
| nearest-candidate maximum error | 8.0 px | 6.0–8.0 px |
| Oil candidates per frame, median | 24 | 23–24 |
| near-truth candidates per frame, median | 4 | 3–4 |
| near-truth candidates per frame, range | 1–7 | 1–8 |

On the original frames, 53 candidates lie within 8 px of truth while 200 lie at
least 24 px away. Existing candidate/path sectors show substantial descriptor
overlap:

| Existing descriptor, median | Near truth geometry | Remote geometry, not a negative label |
|---|---:|---:|
| median near absolute gray contrast | 0.0731 | 0.0326 |
| median far absolute gray contrast | 0.1073 | 0.0480 |
| `abs(near) - abs(far)` | -0.0225 | -0.0218 |
| absolute peak offset | 2 px | 1 px |

The public result establishes only the following:

1. on this small public set, proposal recall is already high under simple global
   photometric transforms;
2. the proposal lattice is highly ambiguous, including multiple rows near the
   annotated interface;
3. the current near/far contrast and peak-location summaries are not a unique
   interface discriminator; and
4. selecting a new scalar threshold from these 13 frames would be overfitting.

It does **not** prove candidate recall on the private Windows videos, prove that
remote rows are false, establish field accuracy, or validate an interface
classifier.

## External evidence review

The external sources are recorded with provenance and reuse notes in the
[Implementation Reference Log](../../70-reference/implementation-reference-log.md).
Their useful implications are consistent with the repository evidence:

| Source class | Relevant result | Decision for this project |
|---|---|---|
| constrained-curve liquid-boundary work | evaluate a curve across the vessel using multiple image properties, rather than ranking one horizontal row | preserve per-sector contour geometry and combine complementary cues along its local normal |
| transparent-vessel reflection work | vessel curvature, fittings and reflections can create strong edges unrelated to contents | model vessel/optics opposition explicitly; edge strength is never identity |
| ECCV 2024 DTLD/TCLD | transparent contact-line estimation uses a Bézier curve representation and color rectification over a large purpose-built dataset | useful proposal/representation reference, but biomedical vessels and controlled dataset are not compressor field proof; any learned model starts as proposal-only |
| background-oriented schlieren | a controlled background and calibration convert refractive-index variation into measurable image displacement; glass/liquid layers require calibration/remapping | add structured-background or controlled-light experiments when fixture access permits; passive-video failure may be an acquisition problem |
| KRIWAN/Copeland commercial controls | commercial compressor/refrigeration products use dedicated optical point monitoring, floats or electronic oil controls at the measurement point | treat a dedicated sensor or controlled optical fixture as a legitimate escalation path, not as a failure of software engineering |

No external algorithm was copied. Marketing accuracy is not used as acceptance
evidence, and none of these sources proves performance on the private compressor
videos.

## Architecture boundary to preserve

The following current contracts remain correct and must survive the redesign:

- one generic detector path; no private Glass, timestamp, video or reviewed-Y
  branches;
- every numeric Oil result is an eligible same-frame candidate with exact source
  provenance;
- FULL/EMPTY never fabricate a coordinate;
- Oil and Foam remain independent until their defined composition point;
- missing, ambiguous, contradictory or unobservable evidence fails closed;
- no interpolation, coordinate carry or stale track identity repair;
- bounded history, candidate count, trace size and runtime; and
- target-Windows qualification is separate from local/public acceptance.

The redesign therefore stops at a typed witness boundary first. It does not
replace the resolver or lifecycle before the witness has demonstrated real
interface-versus-structure discrimination.

## Why the main alternatives are rejected

### Continue tuning existing scalar gates

Rejected. The public distributions overlap, private labels are sparse and
selected, and the same scalar is currently consumed by authority, phase,
tracklet, lifecycle and selection. Tuning it to pass one checkpoint would couple
many owners and repeat prior threshold escapes.

### Use motion or contrast polarity as identity

Rejected. Stationary interfaces are legitimate, reflections can persist or move,
and R23 already failed the polarity-reversal positive control. Motion is a
measurement over a verified physical association, not the verifier.

### Replace everything with a deep network

Rejected as the first step. DTLD demonstrates that a contact-line model can be
useful with a large domain-specific dataset, but this repository has only 13
usable public Oil annotations and non-exportable private media. A learned model
may later propose contours or embeddings, but cannot become publication
authority without compressor-domain labels, held-out negatives, uncertainty and
Windows qualification.

### Keep passive RGB as the only allowed sensor

Rejected as an unconditional assumption. When Oil and refrigerant are both
transparent and the optical path supplies no stable differentiating cue, the
correct output is unobservable. Controlled illumination, structured background,
polarization or a dedicated point sensor must remain available as engineering
options.

## Work completed in this assessment

- refreshed the S11 code topology and inspected current execution owners;
- reviewed the indexed S11 design/failure history through R23, the failure
  registry, private-Windows findings, validation contracts and current R22-2
  diagnostics;
- added the reproducible public interface-witness probe;
- recorded the compact 91-measurement summary without committing a 2.3 MB row
  dump;
- fixed the implementation direction as observation-layer redesign rather than
  whole-detector replacement; and
- wrote the implementation-ready witness architecture and dedicated trace/shadow validation contract.

No detector threshold, candidate, authority, tracklet, phase, selector, Foam or
publication behavior has changed.

## Next execution order

1. Implement the new witness fields in trace-only mode, preserving exact R22-2
   outputs with debug on/off.
2. Build synthetic and public positive/negative image pairs, including genuine
   curve translation with photometric inversion, internal stripes, reflections,
   glare, wall/fitting edges and localization perturbation.
3. Select operating points only with declared development/calibration/holdout
   separation; keep the existing selected private checkpoints out of ad hoc
   threshold selection. Any broader private field calibration first freezes a
   work-PC-only episode-level split with an untouched holdout.
4. Run a shadow classifier on the private Windows machine and review wrong
   structure, unresolved and true-interface cases separately.
5. Only after discrimination passes, allow the typed result into independent
   support and association; handoff and direction-neutral phase work remain
   later gates.
6. In parallel, compare passive fixed-camera, controlled illumination and
   structured-background acquisition modes. If all passive modes remain
   unobservable over required operating states, escalate the product sensing
   boundary instead of loosening software safety gates.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: the currently supported conclusion is a representation/observability and physical-identity gap at frame evidence/candidate formation; private intervals may still contain distinct first harmful stages and are not generalized without review.
- Prior mechanisms reviewed: R22 typed ownership/evidence replacement, R22-1 candidate-centered diagnostics, R22-2 native paths, reviewed BASE/Accum checkpoints, and the rejected R23 polarity-only association experiment.
- Prior mechanisms rejected: global threshold widening, scalar texture neutralization, source-family votes, polarity-only vetoes, motion-only bootstrap, private-coordinate branches, downstream selection repair, interpolation/carry and stale owner transfer.
- Preserved contracts: generic bounded detector, exact current-frame provenance, independent Oil/Foam, typed no-interface state, fail-closed ambiguity/unobservability, bounded history and separate target-Windows qualification.
- Difference from prior failures: candidate recall, contour localization, physical discrimination and acquisition observability are separated before any temporal behavior change; a missing visual cue is no longer treated as a score that should be lowered until it passes.
- Logic-map impact: NONE — the executing runtime remains R22-2; this document fixes the next design boundary and adds a diagnostic probe only.
- Failure-registry impact: NONE — the assessment consolidates existing mechanisms and does not claim a new field cause or repair.
