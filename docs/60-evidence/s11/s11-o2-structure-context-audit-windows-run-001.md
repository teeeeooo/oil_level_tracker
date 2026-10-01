# S11 O2 recorded structure-context audit — Windows report 001

Scope: user-transferred execution summary for the original R22-3 bundle, using
the extension published at `dfe56af`. Private output files were not available on
this host. Code hashes and artifact fingerprint were independently reproduced
locally; COMPLETE, output hashes, 12 input hashes and private contents below are
reported results, not locally reopened receipts.

## Identity and reported verification

| Item | Evidence |
|---|---|
| Experiment script SHA-256 | `65dbd1789fe54e72dfbcf24e6f7deeccded3fac496627a36afcf0146022bd5c4`; matches local source |
| Target-audit helper SHA-256 | `cc707ccb9bffea6416afdf6906131eb40d9a66e56bf383872a0a17b9c7791f5b`; matches local source |
| Artifact SHA-256 | `14d9c335c91295e3a8243122d88e0c4a6c81f5301d67299e19438aa05c6e79e3`; locally reproduced with target_audit + structure_context |
| Run | exit 0; COMPLETE reported; output `structure-context-audit-001` |
| Reference | inputs/scores/evaluation equality reported; original artifact `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9` |
| Preservation | experiment.json/summary.md output hashes match receipt; all 12 input hashes unchanged, as reported |
| Disposition | EXPLORATORY_UNCALIBRATED; auto_acceptance=false; production_decisions_emitted=false; FIELD FAIL; numeric_localization=NOT_MEASURED |
| Receipt transcription | Submitted text says `s11-02-structure-context-audit-v1` (digit zero). Exact matching code emits `s11-o2-structure-context-audit-v1` (letter o). Follow-up again reports digit zero for both files; conflicts with matching code. Subsequent user confirmation of equality=True and code point 111 resolves this as report transcription, not a stored schema mismatch |

The report calls its section “summary.md full text” but supplies candidate and
field-presence paraphrases rather than the generated numeric feature/penalty rows.
This is sufficient to record inventory findings, not feature-level discrimination.

## Reported inventory findings

- review-001 and review-002: same BASE Glass, 12 registered artifact templates,
  empty recipe exclusions. Candidate counts 23 and 23.
- review-003: Accum Glass, 14 registered templates, 27 candidates. This is another
  Glass's geometry/template set in the same original bundle recipe, not evidence
  of a different recipe version or independent filming.
- review-001 idx10 and idx12, among others, have recorded calibrated-artifact
  rejection reasons. This supports recorded template use for some candidates;
  it does not validate all template annotations or their recall.
- review-002 idx11 and review-003 idx15 remain human non_interface but recorded
  rejected=false. Candidate rejection and human identity are distinct axes.
  These facts alone cannot distinguish no match, missing geometry, a later stage
  issue or other reasons; no causal gate conclusion is claimed.
- review-002 idx0 remains human interface with typed_ambiguous_observation
  rejection. User-reported idx0/idx20 ambiguity remains attached to interpretation;
  formal labels and original reference are unchanged.
- Verified identity coverage 0.0 is expected without model predictions in this
  audit. It is not a measured classifier failure rate.

The presence of registered templates refutes an inference of “no artifact
registration” from O1's `vessel_fitting_geometry_unavailable`. It does not by itself
supply a validated identity discriminator or justify another threshold.

## Provenance corrections and unresolved transcription

1. The historical s1/s2 judgment reversal belongs to **review-002 idx10**, not
   idx11. idx11 is the structure-negative candidate with three off path judgments.
2. Human Y=213 versus guide RefY=212 belongs to **review-003 idx10's reference
   guide**, with related human Y=213 evidence for idx19. It is not an idx15 issue.
   idx15 canonical_y=313 is a separate coordinate, not a repair of that mismatch.
3. The new typed BASE Glass ID begins `8f94fb85`, whereas prior reports typed
   `8f94fb05`; the new Accum ID segment is `86c3-85514...` versus earlier
   `86c3-05514...`. Neither prose copy is silently treated as authoritative.
   Return exact stored strings from the existing experiment JSON. Successful
   joins are reported, so this does not yet establish any source-data mismatch.
4. Features and penalties use the **same fixed inventory of 27 field names** in
   this audit, with separate states/values. They are not different field sets.
5. A registered template set and ellipse differ per Glass; this does not imply
   separate recipe snapshots. Registration timing/independence remains unverified.

## Follow-up numeric extract and source interpretation

The user returned the eight requested candidates and nine fields separately for
features/penalties. This is transferred numeric evidence, not local access to the
private JSON. Follow-up file hashes are:

- complete.json: `aa82d45d7ee2649649f718909cb30a36d9343857313cf9ddf50b5fdd3cfbb876`;
- experiment.json: `5f0db76e34a968db447dc85049dc314dde960fa2210d261af65e408217531dc2`.

Twelve original input-preservation entries were again reported equal. Listing
those embedded entries is not independently rehashing the output files before and
after this read. Both schemas were again typed as `s11-02-structure-context-audit-v1`.
That conflicted with the exact-matching source at this stage; the subsequent
user confirmation of True/111 below resolves the schema discrepancy. Repeated
Glass strings match the previous transfer; they remain reported identifiers, not
locally verified UUIDs. The candidate subset request is complete; do not repeat it.

| Candidate (historical identity) | Artifact likelihood | Static contribution | Feature texture conflict | Penalty texture conflict | Material terminal support | Boundary likelihood |
|---|---:|---:|---:|---:|---:|---:|
| r001 idx10 (non_interface) | .032 | 0 | .033961 | .033961 | 0 | .512727 |
| r002 idx0 (interface, human-qualified ambiguity) | .228050 | 0 | .121142 | 0 | 0 | .163941 |
| r002 idx8 (interface) | .064 | .015518 | .245567 | 0 | 0 | .622078 |
| r002 idx10 (interface) | .12 | 0 | .086186 | 0 | 0 | .486649 |
| r002 idx11 (non_interface) | .12 | 0 | .175415 | 0 | .473216 | .480760 |
| r002 idx20 (non_interface, human-qualified ambiguity) | 0 | 0 | .261042 | .261042 | .012421 | .610174 |
| r003 idx10 (interface) | .056 | 0 | .666574 | .666574 | .690269 | .866443 |
| r003 idx15 (non_interface) | .138394 | .025653 | .251893 | .251893 | 0 | .475421 |

Table values are explicitly rounded descriptive extracts, not new score inputs.
For all eight, optics/glare conflict is absent in features; penalties are present
zero except r003 idx15 (.020902612826603325 for each). Feature
static_artifact_penalty is absent in all; penalty values are present and equal to
the displayed static contribution. Boundary and terminal are absent in penalties.
No reported missing field is interpreted as measured zero or present null.

`calibrated_artifact_match` is present in both containers only for r001 idx10:
0.9050349281666007, with rejected=true and the registered-template reason. It is
missing in both containers for the seven other selected candidates.

Source checks at `dfe56af` establish:

- `artifact_calibration.apply_artifact_templates` writes the match field only
  when a template reaches its existing 0.72 gate; otherwise the candidate passes
  through unchanged. Missing therefore is not a saved best-match score of zero
  and does not prove the matcher was never run. The private cause (no qualifying
  match, unavailable geometry, path applicability, etc.) is not resolved here.
- `phase_candidate_assembler` keeps material-context values in features and
  conditionally writes zero texture penalty when white_material_texture_present
  is false for oil/material-path enrichment; other generated candidates retain
  the value as a penalty. This explains how the containers can differ without
  lost data. This is a source-supported mechanism, not a replay of the private
  frame's branch history.
- `OilCandidateEvidence.from_candidate` consumes texture conflict as the maximum
  of features and penalties. A zero penalty does **not** mean the downstream typed
  evidence ignores the nonzero feature. No fix to copy that value into penalties
  is justified by this report. Both containers contain derived evidence; a generic
  raw-versus-evaluated semantic division would be inaccurate.
- `material_layer_context_features` computes generic raster texture/terminal
  context, not a physical Oil probability. Larger terminal support in a labeled
  negative does not redefine identity.

The selected controls do not justify a simple new context veto: r002 idx10 and
idx11 share artifact likelihood .12, static=0 and optics/glare=0 with similar
boundary values (.486649 vs .480760); terminal support is larger for the negative.
A higher texture-conflict veto would encounter r002 positive idx8 above negative
idx11, and r003 positive idx10 above negative idx15. Accum-specific direction or
a source-Y cutoff must not be generalized to BASE or a moving interface. These
counterexamples constrain simple proposals; they do not prove no multivariate or
additional spatial evidence could discriminate candidates.

## Schema resolution and decision

In response to the mechanical equality/code-point check, the user returned
`true 111`. This confirms the expected schema with lowercase `o` (U+006F), not
digit zero. The `02` in the transferred tables was a reporting transcription
error; no JSON rewrite, source repair or experiment rerun is required. This is
user-reported verification, not local inspection of the private files. The short
reply confirms the schema check only; it is not a new claim that every optional
hash/read-preservation line in the procedure was independently returned. Earlier
reported output/input preservation remains the corresponding evidence.

The requested structure-context investigation is complete without promotion.
No defensible new weight/threshold/template change or production bug fix follows
from the selected values. No additional feature listing, full audit replay or
human image review is requested at this point. The identity challenger remains
unselected; any future mechanism needs an explicitly distinct observable and
positive/negative/unresolved controls. Do not keep searching thresholds on this
eight-candidate subset or recast a reporting correction as model improvement.
Current work-plan owns the next engineering transition. FIELD FAIL is unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: unestablished causally. Numeric context was returned and constrains simple context-veto proposals, but private template-gate causes remain unestablished. The schema transcription issue is resolved by the reported True/111 check.
- Logic-map impact: NONE — transferred diagnostics evidence only; production and audit code are unchanged.
- Failure-registry impact: NONE — no identity repair or field efficacy is demonstrated.
