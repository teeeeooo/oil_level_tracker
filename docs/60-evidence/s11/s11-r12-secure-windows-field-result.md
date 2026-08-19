# S11-R12 Secure-Windows Field Result

## Result

The secure-Windows R12 Base/Accum replay fails the field-effectiveness gate.
R12 removed the former Base lower-rim path and made Foam validity independent,
but it did not recover the reviewed Base interface and still selected the
Accum Foam/residue track as Oil.

The transferred Windows bundle was created from a GitHub ZIP and does not
contain a Git SHA. Its sequence manifest identifies
`r12-phase-composition-replacement-v1`; the trace does not emit a detector
version. This result is therefore version- and bundle-identified evidence, not
an exact-SHA attestation.

## Accepted evidence

| Glass | rows | numeric Oil | public Foam |
|---|---:|---:|---:|
| Base | 601 | 0 | 0 |
| Accum | 601 | 164 | 43 |

- Base reviewed source Y is 437 at 540 s, 360 at 634 s and 435 at 674 s. No
  candidate exists within 25 px at 540 or 674 s. At 634 s, candidates at Y380
  and Y338 reach continuation authority but have no trajectory support.
- Base has 7,069 final continuation-eligible candidates and zero qualified
  anchor. The R11 Y724–873 wrong path is gone, but useful interface recall and
  publication remain absent.
- Accum publishes 92 wrong Oil rows at Y190–297 in two long runs. Eighty-five
  of those selected rows have material-texture conflict at least 0.5. The
  selected authority is continuation for 59 rows, semantic-sequence anchor for
  25 and corroborated-material-path for eight.
- The old `calibrated_dynamic_seed` and motion-keyframe compatibility fields
  are not R12 anchor indicators. The 33 anchor-authority residue rows are the
  actual seed set and agree with the 33 selected rows carrying cluster support.
- At 672 s, multiple reviewed lower-Oil candidates near Y450 have trajectory
  support but do not survive the final path/run result. At 684 and 689 s,
  reviewed lower candidates are demoted by track opposition while upper
  residue is published.
- Accum Foam is independently valid. At 670.5 and 673 s, CSV records
  `foam_is_valid=True` even though `oil_is_valid=False` and legacy
  `is_valid=False`. The 650–700 s funnel is 44 raw, 34 eligible and 20
  confirmed/public rows.
- The Result Review graph renderer does not currently mask points by each
  point's validity even though the graph model carries per-series validity.
  Invalid numeric Oil can therefore remain visible.

The causal record is
[`../../50-diagnostics/s11/s11-r12-windows-phase-authority-diagnostic.md`](../../50-diagnostics/s11/s11-r12-windows-phase-authority-diagnostic.md).

## Gate disposition

R12 local regression, replay and runtime results remain valid historical
evidence. They do not establish private-field effectiveness. R12 is not
accepted for release. The next implementation must replace the leaking
semantic authority and composition-agnostic trajectory behavior, recover Base
proposal recall without granting proposal authority, and make the renderer
honor per-series validity.
