# S11 O2 W4 paired-scale — Windows run 001

Date recorded: 2026-10-01. Executed code: `ae52f52`.
Evidence source: user-transferred Windows run report and generated summary.
Private experiment/receipt/input files remain on Windows; their byte hashes and
execution are reported, not independently recomputed in this checkout. Script
and artifact identities can be checked against the local source.

[Fixed hypothesis](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md#w4-paired-scale-local-comparison),
[acceptance limits](../../30-validation/s11-interface-observability-witness-validation.md#w4-paired-scale-controls),
[local controls](s11-o2-w4-paired-scale-local.md) and
[live work state](../../00-project/work-plan.md#s11-work-item-ledger) remain separate.

## Run identity and reported integrity

| Item | Reported value |
|---|---|
| Code commit | `ae52f527b77d8080f559c9ff04a5b07f4b84c3ee` |
| s11_shadow_experiment.py SHA-256 | `b6afbf86718742e27cac02dda60f5dbcd9b76ad6c8ea35adeb3b1bd1398e4645` |
| Python / platform | 3.14.3 / Windows-11-10.0.26200-SP0 |
| Artifact SHA-256 | `b4503f39d31a733c0821c677c581098a9fdb5b6273e6af6d5e0544ee3104ba5d` |
| Base spec / paired spec | `two-sided-localized-edge-ranking-v1` / `same-x-paired-scale-difference-v1` |
| Reference artifact SHA-256 | `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9` |
| Reference inputs/scores/evaluation equal | true |
| Receipt | `s11-o2-paired-scale-v1`, COMPLETE; artifact matches experiment |
| experiment.json SHA-256 | `7a32fd062444e5ebbc5f47eb0b257d6b617cd55911746c0b8af2eb12011c2a2e` |
| summary.md SHA-256 | `166831aef054020584d5efe4bc03984c52d3c6ec2880948c174375e1e2123931` |
| Output hashes / input preservation | 2/2 outputs verified; 7/7 inputs preserved |
| Output directory alias | `experiments/paired-scale-001` |
| Status | EXPLORATORY_UNCALIBRATED; auto_acceptance=false; FIELD FAIL |
| Numeric localization | NOT_MEASURED |

Inputs were review-001 labels-v2.json rev3, review-002 labels-v2.json rev14,
review-003 labels.json rev4, all `s11-o2-labels-v2`, plus their three packets and
the original fixed-score v1 reference. No new labels, geometry, freeze, threshold,
partition or detector changes were reported. No bundle/video was needed. Existing
snapshots remain historical rather than replacing these active labels.

## Results on separate tasks

C/R/T/U mean correct/reversed/tie/unscorable. Counts are per task, not pooled.

| Review / native-path task | Pairs | Legacy C/R/T/U | Joint baseline C/R/T/U | Paired C/R/T/U | Improved / regressed | Shared scale count histogram |
|---|---:|---|---|---|---|---|
| 002 / interface_location_same_x | 8 | 5/2/0/1 | 5/2/0/1 | 6/1/0/1 | 1 / 0 | 3:7, 0:1 |
| 002 / identity_negative_control_same_x | 9 | 5/2/0/2 | 7/0/0/2 | 7/0/0/2 | 0 / 0 | 1:7, 0:2 |
| 003 / identity_negative_control_same_x | 5 | 5/0/0/0 | 5/0/0/0 | 5/0/0/0 | 0 / 0 | 1:1, 2:1, 3:3 |

Review-001 has zero pairs in all tasks. Review-003 has zero primary location
pairs. All candidate-center tasks have zero pairs. These are unevaluated task
populations, not successes. Review-003 retains 19 native-path unreviewed points;
its five non-interface/off points are negative controls, not interface/off truth.

### One aggregation improvement

Review-002 positive idx8, native_path X=[130,236], Y=397 versus negative idx10,
same X and basis, Y=378. Both identities are interface; the second path point is
off_interface. All three scales are jointly available, so support is unchanged.

| BW | Positive combined | Negative combined | Difference |
|---|---:|---:|---:|
| 8 | 0.5991238600612279 | 0.4825010373793375 | 0.11662282268189034 |
| 16 | 0.44828499773135866 | 0.45981481109266327 | -0.011529814161304608 |
| 24 | 0.25505038193026147 | 0.2346619666585796 | 0.020388415271681865 |

Independent medians give difference -0.011529814161304608 (reversed); median
paired difference is +0.020388415271681865 (correct). This supports the narrow
aggregation-loss explanation while preserving locality. It does not show that
locality is generally beneficial or unnecessary.

### Two support changes, not aggregation gains

Review-002 idx10 Y363 and idx12 Y381 each compared with non-interface idx11 Y925,
all native_path X=[236,343], change legacy reversed to joint baseline correct.
Both then stay correct under paired aggregation. Only BW8 is jointly available;
differences are respectively 0.274105878009083 and 0.08099893056713788.
These two changes belong to `support_changed_orders`, not `improved`.

## Interpretation and limitations

The prespecified observed primary net gain is +1 with zero native negative-control
regressions. The comparator is **not rejected on these controls**, retained as a
bounded diagnostic result, and **not promoted** to production or identity ranking.
This closes the requested Windows run, not the full W4 candidate-identity work.

The only improvement is the already-known pair that motivated the hypothesis;
it is retrospective explanatory evidence, not a fresh holdout success. One
primary reversal and one unscorable pair remain. Their identities are not printed
in this changed-pairs-only summary; do not guess the remaining reversed pair.

Negative-control strength is limited beyond the small correlated sample count.
All seven usable review-002 negative pairs have one shared scale. With one scale,
paired and independent aggregation are identical. With two scales and the existing
linear-interpolated median, they are also algebraically identical (up to floating
arithmetic). Therefore only the three three-scale negative pairs in review-003
exercise a potentially different reducer. Absence of regression across every
reported pair is not twelve independent tests of the mechanism.

Candidate identity, scalar truth/eligibility, coverage gaps, generalization and
calibrated O2 acceptance remain unresolved. Pairwise cycles remain possible, so
there is no valid automatic total-rank/selected-candidate inference. No follow-on
formula, threshold tuning or W5/O3 entry is authorized by this observation alone.

## Bounded inspection request (completed by follow-up below)

Read the existing private `experiment.json`; do not rerun the experiment. Within
`paired_scale`, select case_id=review-002 and task
`native_path/interface_location_same_x`. Return the unchanged raw pair objects
whose `paired_outcome` is reversed or unscorable (expected one each), including
positive/negative geometry, all three outcomes, both differences, shared widths,
per-scale scores/differences and excluded-scale reasons. No relabeling or manual
numeric transcription is needed. Hash the input before/after this read.

The purpose is to distinguish the remaining score-order limitation from missing
support before selecting further implementation work. Do not optimize a new
formula for the remaining pair. Candidate-identity work still needs its own
observable and controls; this local comparison is not its substitute.

## Follow-up: remaining pair inspection

The user returned the two requested raw pair objects from the existing experiment.
No rerun, code/label/score change was reported. The accompanying seven preserved
input entries are consistent with the original experiment's preservation record;
they do not supply a separate before/after hash of experiment.json for this read.
Do not claim that additional byte-level verification was performed here.

### Persistent reversed pair: score-order limitation

Both candidates are interface identities. Positive idx9 is near_interface at
native_path X=[130,236], Y=382; negative idx10 is off_interface at the same X,
Y=378. There are three shared widths and no excluded scales.

| BW | Positive combined | Negative combined | Difference |
|---|---:|---:|---:|
| 8 | 0.4787061461567078 | 0.4825010373793375 | -0.003794891222629715 |
| 16 | 0.4468563212258939 | 0.45981481109266327 | -0.012958489866769351 |
| 24 | 0.2088245679507642 | 0.2346619666585796 | -0.0258373987078154 |

Legacy, joint baseline and paired outcomes are all reversed. Both differences
are -0.012958489866769351. Unlike the repaired idx8/idx10 pair, every available
scale already favors the off point. Pairing before taking the median therefore
cannot repair this ordering. Any common nonnegative weighting of these supplied
negative differences also remains negative (unless all weights are zero).
This is a limitation of the supplied combined scores, not evidence that an
alternative descriptor is impossible or that the human labels are wrong. The
component-level physical cause is not established by these combined values.
The 4 px Y separation is descriptive, not a label tolerance or a new rule.

### Persistent unscorable pair: missing joint support

Positive idx9 near Y417 versus negative idx8 off Y405, native_path X=[449,555].
Both have three scale records; common_scale_count=0, common_band_widths=[],
scales=[], and both differences are null. All three views remain unscorable.

| BW | Excluded fields |
|---|---|
| 8 | right.combined |
| 16 | left.combined, right.combined |
| 24 | left.combined, right.combined |

The earlier idx8 far_above.gray_mean gap explains right.combined at all widths.
The returned object additionally shows left.combined unavailable at BW16/24;
its underlying missing measurement is not identified by these exclusions. Do
not attribute it to the same far band without source evidence. The known right
side alone is already sufficient to eliminate all joint support. Missing scores
stay null rather than zero; no fallback or extra extraction is needed to close
this bounded aggregation experiment.

### Disposition and next work

The follow-up is complete. Retain the +1/0 retrospective local gain without
promotion; the remaining reversal is upstream of this reducer, and the remaining
unscorable pair has no joint support. Stop this aggregation experiment rather
than adjust a formula to the remaining pair. No additional Windows run or JSON
extraction is requested now.

Return to the open W1/W4 candidate-identity question: review available geometric
and contextual evidence against partial-positive, glare/structure and identical-
observable controls before selecting a new mechanism. No new identity formula,
collection request, threshold, phase change or O2 acceptance follows from this
local-position result. FIELD FAIL remains unchanged.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: the known local comparison reverses during independent scale reduction; paired reduction repairs it on this sample. The follow-up shows the remaining pair already reversed at all three combined-score scales; the underlying component-level physical cause and candidate-identity failures remain unresolved.
- Logic-map impact: NONE — transferred offline evidence and live status only; detector selection, scoring, geometry and publication behavior are unchanged.
- Failure-registry impact: NONE — narrow in-sample improvement is retained without identity or field acceptance, preserving existing provenance and no-private-rule constraints.
