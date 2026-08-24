# S11-R16 Secure-Windows Field Result

## Result

The R16 private-Windows Base/Accum replay failed S11 detector effectiveness.
Oil/Foam same-frame provenance and sequence-to-CSV projection were internally
consistent, and Accum initial-EMPTY suppression improved, but Base Oil recall,
Accum Oil continuity/accuracy and Foam false-positive suppression failed.

This record supersedes the preliminary R16 Windows counts that treated
top-level current-frame fields as completed-window sequence publication. It
does not authorize private-video coordinates, timestamps, global threshold
changes or Recipe retuning in production.

## Run identity

- bundle: `C:\0.Coding\oil_level_tracker-main\sample\oil_level_analysis_R16개선_add_artifact_20260824_145216`;
- run ID: `68195551-03b6-4b29-bf92-c57e41a9a80d`;
- run name: `R16개선_add_artifact`;
- result status: `REVIEW_REQUIRED`;
- detector: `opencv-phase-detector-r16-directed-interface-tracklets-v1`;
- sequence resolver: `r16-directed-interface-tracklets-v1`;
- analyzed interval: 480--780 s at 2 FPS;
- records: 601 Base and 601 Accum;
- initial state: Base `FULL_NO_INTERFACE`, Accum `EMPTY_NO_INTERFACE`;
- saved Recipes and Artifact templates were included; and
- bundle Git provenance: unavailable because the Windows transfer was not a
  Git checkout.

The user transferred a GitHub ZIP from `codex/ui-ux-refresh` and confirmed that
the source that generated the bundle was the transferred source. That branch
contains the R16 detector tree plus three UI/documentation commits; no detector
diff exists relative to `codex/r16-tracklet-refactor`. This is transfer
provenance supplied by the operator, not bundle-contained exact-head proof.

## Publication and integrity contract

Final Oil is a finite completed-window Oil result. Final Foam is
`foam_is_valid=True` with completed-window Foam Y, an episode-confirmed flag and
one selected same-frame Foam candidate. Top-level trace positions/candidates
are current-frame observations and are not completed-window publication.

The corrected audit found:

- Oil: selected candidate Y = completed-window source Y = CSV raw Oil Y for
  all 31 Accum Oil rows;
- Foam: selected candidate Y = completed-window Foam Y = CSV raw Foam Y for
  all 102 valid Foam rows (Base 5, Accum 97);
- every valid Foam row has exactly one selected completed-window Foam
  candidate and an R7/R8 episode-confirmed flag; and
- canonical candidate Y and CSV raw Y are already source coordinates; no crop
  origin is added.

Therefore coordinate, same-frame provenance and sequence-to-CSV equality pass.
Earlier claims of 243 Base and 93 Accum public Foam rows, missing selected Foam
candidates or absent episode confirmation are withdrawn extraction errors.

## Final publication

| Glass | Oil valid | Foam valid | Unknown | Oil tracklets confirmed / provisional |
|---|---:|---:|---:|---:|
| Base | 0 | 5 | 601 | 0 / 454 |
| Accum | 31 | 97 | 570 | 3 / 317 |

R14 is comparison evidence, not truth: Base Oil/Foam was 164/0 and Accum
Oil/Foam was 129/23. R16 therefore removed the R14 initial-EMPTY false Oil runs
but regressed Base Oil, Accum Oil coverage and Foam precision.

## Base Oil observation

Base published no Oil in 601 rows although source review identifies visible
Oil near Y437 at 540 s, Y360 at 634 s and Y435 at 674 s.

- 540 s: no candidate within 25 px; nearest bounded candidate was Y391, 46 px
  away, and did not confirm;
- 634 s: a Y338 candidate was within 22 px but did not confirm; and
- 674 s: no candidate within 80 px; nearest was Y351, 84 px away.

All 454 physical tracklets remained provisional. Track-level terminal failure
classification was 349 `ENTRANCE_ORIGIN_MISSING`, 102
`INSUFFICIENT_NET_PROGRESS` and three
`INSUFFICIENT_MOTION_OR_ANCHOR_EVIDENCE`. This is mixed proposal-recall and
bounded-confirmation failure, not a selector or publication-integrity failure.

## Accum Oil observation

R16 suppressed the four R14 false Oil runs in the reviewed 480--650 s initial
EMPTY interval. A real lower-entry trajectory was admitted and produced 31
same-frame Oil rows in five runs from 669.5022 through 701.4925 s.

The numeric rows were not uniformly accurate. At 677 s the R16 Y444 result was
6 px from reviewed Y450, while 684 s Y347 and 689 s Y360 were respectively
107 px and 114 px from reviewed Y454/Y474. Near those later truth rows,
proposal/admission had already removed or failed to create the reviewed
alternative. The surviving confirmed tracklet cannot alone establish the
first causal failure.

Run gaps remained UNKNOWN, and after 702 s Oil stayed non-numeric with
`ENTRANCE_ORIGIN_MISSING`. The initial-EMPTY entrance guard correctly blocks
stationary pre-entry false rows, but after bounded owner loss there is no
proven mid-glass filling-interface reacquisition path. The evidence does not
authorize globally relaxing the entrance guard or changing initial state over
time.

## Foam observation

Base's five valid Foam rows at 768.5177--772.9805 s, Y652--657, are reviewed
glare/lower structure rather than Foam.

Accum's 97 valid Foam rows split into:

| Reviewed class | Frames | Result |
|---|---:|---|
| Real rising dynamic Foam, 653.5--677 s | 24 | retained |
| Real later Foam, 758--774.5 s | 28 | retained |
| Y80 Oil two-phase/residue, 679--713 s | 27 | false Foam |
| Detached-looking non-Foam, 731.5--736.5 s | 7 | false Foam |
| Y519--525 non-Foam, 777.5--780 s | 6 | false Foam |
| Other reviewed non-Foam rows | 5 | false Foam |
| **Total** | **97** | **52 real / 45 false** |

All false rows legitimately passed R16 episode confirmation and same-frame
projection; the failure is episode/material discrimination, not serialization.
Single-feature ranges for material score, whiteness, texture, area, motion and
static overlap overlap between the reviewed true and false cohorts. Static
overlap of zero proves no learned-map match, not that no static map existed.
High registered motion on false regions proves the current evidence is not
discriminative there; its physical source is not established by this bundle.

## Disposition

R16 is now the integrated `main` baseline but is not field-qualified. The next
action is a corrected repair design informed by R11--R16 failures. It must
preserve initial-EMPTY suppression, real lower-entry admission, real Foam
recall, calibrated Artifact rejection and exact same-frame/CSV provenance.
Implementation and a new Windows replay remain separate later gates.
