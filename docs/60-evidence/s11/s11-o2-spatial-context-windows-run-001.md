# S11 O2 spatial-context Windows run 001 — transferred report

Source revision: `bd0185838c094d2529d6089870e37fb8552d90ed` (GitHub ZIP).
Evidence scope: user-transferred execution summary, not locally accessed private
outputs. COMPLETE, all output hashes and 12 input hashes are reported passing;
schema and artifact transcription are resolved by explicit user correction;
original generated summary/receipt are still needed for output inventory and mappings.
No rerun, score change, label change or detector improvement is established.

## Reported result

- Original review-002 frame 14386, revision 14; review-003 frame 16280, revision 4.
- Both baseline checks reported MATCH, zero mismatched bands. This supports
  gray/support-band reconstruction on the reported fields, not historical pixel
  equality or physical identity. The stated denominator 1416 needs per-case raw
  `summary.md` confirmation rather than inference from a prose aggregate.
- Twelve input files reported unchanged before/after/current: five original bundle
  files, source video, two labels, two packets and two existing bundle links.
- NOT_EVALUATED; EXPLORATORY_UNCALIBRATED; auto_acceptance=false;
  production_decisions_emitted=false; FIELD FAIL; numeric_localization=NOT_MEASURED.
- Source/crop/gray/mask PNGs and ordered strip SVGs are reported retained locally
  in `spatial-context-001`. Their contents and generated point mappings have not
  been supplied here. Wider spatial information/identity utility remains unassessed.

## Local source comparison and report corrections

The runner SHA-256 matches the reported value exactly:
`d412d98b424842c8f2898de3ba74306317164bd4b13438d395f60d91eec3b84d`.

| Item | Transferred text | Locally verified source / arithmetic |
|---|---|---|
| Schema | `s11-02-spatial-context-v1` | `s11-o2-spatial-context-v1`; character at index 4 is lowercase o, code point 111 |
| Artifact | `6aaf5f3ff6c4e1314d0bcb7effb745ff5b721c03940c57002214b039ef544910` | Windows-path reconstruction: `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910` |
| Hashed outputs | 33 | Listed inventory totals 31: 2 JSON/MD + 10 PNG + 19 SVG; complete.json is an additional unlisted receipt, hence 32 total files for that inventory |

The user explicitly confirmed that the artifact is identical, with `4d08cb`,
and that the schema is `o2`; both prior differences were copying errors. These
two issues are resolved by user confirmation, not by silently rewriting evidence.
The output count and per-case band denominators remain unconfirmed.
At this revision code-path keys use native separators, so the artifact itself is
platform dependent: the POSIX reconstruction is
`53fd2b73c8d387eb905d947307b09e18a9d27c3151b905fea0abde85dba93689`.
The Windows expectation above was recomputed using PureWindowsPath keys and the
same current code-file hashes/spec/schema; no source edit or private rerun was
performed. The corrected user-reported artifact matches that Windows expectation
exactly. No artifact-generation change or experiment rerun is needed.

The previous structure-context run's True/111 confirmation belongs to that older
receipt; this run now has its own explicit user correction above. Hand-copied
Glass UUIDs are not authoritative scene records.

## Next bounded action

Obtain original generated `summary.md` and `complete.json` from this output folder,
as files rather than another manually transcribed table. The remaining purpose
is actual output inventory, per-case band counts and point/profile mappings, not
a repeated schema/artifact confirmation.
No full detailed experiment JSON or source images are requested at this stage;
no execution is to be repeated. Reconcile the receipt first, then use exact
mappings to inspect whether wider context adds an observable beyond original O1.
A MATCH/COMPLETE result alone cannot establish a new discriminator. Human idx0/
idx20 ambiguity and all pinned labels remain unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: report transcription obscures exact receipt/identity; wider-context physical efficacy is not yet assessed.
- Logic-map impact: NONE — evidence intake only, no implementation change.
- Failure-registry impact: NONE — no new field cause or repair established.
