# S11-R17 Secure-Windows Field Result

## Result

The R17 private-Windows replay of `windows_sample1_heating_coldstart` failed
the S11 field-effectiveness gate. Completed-window publication integrity
passed, and the initial Accum EMPTY interval remained fully suppressed, but
Base no-interface suppression and drain ownership, Accum Oil continuity after
partial fill, and Foam false-positive suppression failed.

This is the frozen field-result record. It incorporates the final extraction
corrections: top-level trace candidates are current-frame proposals, nested
`sequence` values are completed-window publication, initial EMPTY applies a
hard phase gate, and the apparent Accum detections near 733/754 s were final
Foam rather than final Oil.

## Run identity

- bundle: `C:\0.Coding\oil_level_tracker-main\sample\oil_level_analysis_R17개선_add_artifact_modify_20260825_091332`;
- run ID: `ffdd9e7b-bb95-43d9-b1cd-b1c9a6313a53`;
- sample alias: `windows_sample1_heating_coldstart`;
- sequence resolver: `r17-physical-observation-ownership-v3`;
- analyzed interval: 480--780 s at approximately 2 FPS;
- records: 601 Base and 601 Accum;
- Base Glass: `8f94fb85-d98e-4c71-9c97-3085168be1b2`;
- Accum Glass: `8fb6ebc7-7c56-401e-86c3-05514bf6380b`;
- Recipe, Artifact templates, trace/index and selected-frame artifacts were
  present; and
- bundle Git provenance is unavailable because the Windows transfer is not a
  Git checkout.

The operator transferred the source as a GitHub ZIP and confirmed that the
bundle generator and inspected source came from that transfer. This is
operator transfer provenance, not bundle-contained exact-head proof.

## Publication and coordinate integrity

Final Oil is a finite nested completed-window Oil result and final Foam is a
CSV-valid nested completed-window Foam result with one selected same-frame
candidate and an episode-confirmed flag. Top-level trace positions and
candidates do not by themselves constitute final publication.

| Glass | Oil valid | Foam valid | Selected same-frame equality | Sequence-to-CSV equality |
|---|---:|---:|---:|---:|
| Base | 339 | 0 | 339 / 339 Oil | 339 / 339 Oil |
| Accum | 26 | 99 | 26 / 26 Oil; 99 / 99 Foam | 26 / 26 Oil; 99 / 99 Foam |

For every final Oil row, selected candidate `canonical_y`, nested
`sequence_resolved_source_y` and CSV `raw_oil_air_level_y` are exactly equal.
For every final Foam row, selected candidate Y, nested Foam Y and CSV
`raw_foam_front_y` are exactly equal. Canonical and CSV raw Y are source-frame
coordinates; no crop-origin adjustment applies.

The 99 Accum Foam rows also form identical sets across nested selected Foam,
`R7_FOAM_EPISODE_CONFIRMED` and CSV `foam_is_valid=True`. Base has no final
Foam row.

## Exact reviewed-segment result

Segment membership uses the canonical reviewed-truth intervals, includes the
start and excludes the end except for the last segment, and assigns the first
479.9795 s decoded sample to the canonical 480 s start.

| Segment | Rows | Oil valid | Foam valid | Oil runs | Foam runs | Oil source-Y | Foam source-Y | Result |
|---|---:|---:|---:|---:|---:|---|---|---|
| `WS1-BASE-FULL-PREFIX` | 140 | 45 | 0 | 2 | 0 | 281--367 | - | FAIL |
| `WS1-BASE-DRAIN` | 225 | 201 | 0 | 11 | 0 | 363--908 | - | FAIL |
| `WS1-BASE-RAPID-REFILL` | 3 | 2 | 0 | 2 | 0 | 409--418 | - | FAIL |
| `WS1-BASE-FULL-SUFFIX` | 233 | 91 | 0 | 7 | 0 | 343--782 | - | FAIL |
| `WS1-ACCUM-EMPTY` | 347 | 0 | 0 | 0 | 0 | - | - | PASS |
| `WS1-ACCUM-ENTRY-SPLASH` | 37 | 17 | 16 | 3 | 5 | 496--548 | 334--511 | FAIL |
| `WS1-ACCUM-FOAM-LAYERED` | 16 | 8 | 13 | 2 | 2 | 219--276 | 80--337 | FAIL |
| `WS1-ACCUM-POST-FOAM` | 41 | 1 | 8 | 1 | 2 | 204 | 80 | FAIL |
| `WS1-ACCUM-DRAIN` | 160 | 0 | 62 | 0 | 7 | - | 80--525 | FAIL |

Runs are contiguous valid sampled rows within one Glass, not consecutive
integer source-frame indices. The segment totals are exactly 601 rows per
Glass and 1,202 rows overall, with no missing or duplicate assignment.

The layered segment proves segment-level Foam recall. Four simultaneous
published rows at 675.0077, 675.5082, 676.0087 and 677.0097 s satisfy the
reviewed ordering `foam_y < oil_y`. The reviewed truth contains no frame-exact
Y anchors for this interval, so individual Oil and Foam coordinate accuracy is
`NOT_EVALUATED`; candidate or publication Y is not promoted to truth.

## Material-phase observation

| Glass | Open | Filling | Filled barrier | Draining | Fill confirmation profile |
|---|---:|---:|---:|---:|---|
| Base | 601 | 0 | 0 | 0 | `none` in 601 rows |
| Accum | 560 | 41 | 0 | 0 | no completed barrier |

Base remained OPEN across the initial full/no-interface prefix, the real drain,
the rapid refill and the full/no-interface suffix. Accum entered FILLING for 41
rows but never formed a filled barrier or drain phase before the real reversal
near 700 s.

The initial-state phase gate is asymmetric:

- with `empty_entrance_motion_enabled=True`, no dynamic fill owner produces
  `allowed=frozenset()`, and `_constrain_layer()` removes every Oil node;
- with it `False`, the same branch produces `allowed=None`, leaving the layer
  unconstrained; and
- the reason `FILL_EVIDENCE_ACCUMULATING` does not choose the gate. The fixed
  policy value does.

The Accum policy has `empty_entrance_motion_enabled=True`; therefore both its
`INITIAL_EMPTY_ENTRY_PENDING` and `FILL_EVIDENCE_ACCUMULATING` rows use the
hard empty allowed-set gate when no dynamic owner exists. Earlier claims that
Accum `FILL_EVIDENCE_ACCUMULATING` implied an unconstrained selector are
withdrawn.

The Base policy behavior is `empty_entrance_motion_enabled=False` and therefore
unconstrained in the same no-owner branch. The exact confirmed-initial-state
value is not serialized in the trace; the policy behavior is code-derived from
the bundle behavior and source contract rather than direct trace provenance.

## Corrected 733/754 s interpretation

Accum has no final Oil row from 731--736.5 s or 752--756.5 s. Nested sequence
kind is `unknown`, sequence Oil Y is absent and CSV `oil_is_valid=False` in all
20 sampled rows. Top-level Oil proposals remain present, but are unselected
current-frame candidates and do not establish publication.

Final Foam is instead present at 733.48--735.48 s with Y468--485 and at
755.00--755.50 s with Y412--419. The reviewed truth says Foam is absent after
about 680 s, so these seven rows are false Foam. The Result Review graph reads
valid stored Oil/Foam series; with Oil absent, the visible series in these
intervals is Foam, not final Oil. The prior description of “Accum 733/754 s
false Oil” is withdrawn.

## Field disposition

- Base full/no-interface suppression: FAIL, 136 false numeric Oil rows across
  the two no-interface segments.
- Base real drain: FAIL, with correct-interface and lower/glare identities
  represented inside 201 rows and 11 fragmented runs.
- Base rapid refill closure: FAIL; no filled barrier formed.
- Accum initial EMPTY suppression: PASS, 347 rows with no Oil or Foam.
- Accum entry and layered publication: FAIL overall; Oil is intermittent and
  16 pre-Foam rows are false Foam.
- Accum post-Foam/drain: FAIL; only one Oil row exists before reversal, no Oil
  is published in the 160-row drain, and 70 post-Foam/drain rows are false
  Foam.
- Same-frame/sequence/CSV integrity: PASS.

R17 is locally validated but not field-qualified. This result does not
authorize private-video coordinate/timestamp exceptions, global threshold
changes, Recipe retuning or implementation conclusions that are not owned by
the corrected diagnostic.

## Named unknowns

- `oil_no_interface_full_likelihood` is absent from the bundle trace, so the
  Base 480 s first failure cannot be uniquely divided between no-interface
  state proposal and phase ownership.
- The exact failed subcondition inside each Base rapid-refill fill chain is not
  reconstructible from the serialized trace, although `fill_confirmation_profile=none`
  and absence of a barrier are observed.
- The layered interval has no frame-exact source-Y truth anchors; individual
  coordinate error remains `NOT_EVALUATED`.
- Oil-before-Foam ordering and lack of a post-Foam Oil correction pass are code
  facts, but their counterfactual causal effect on the layered selection is not
  proven by this bundle.

These unknowns are frozen rather than used to extend the field investigation.
The supporting causal boundaries are recorded in the
[R17 Windows diagnostic](../../50-diagnostics/s11/s11-r17-windows-phase-and-episode-diagnostic.md).
