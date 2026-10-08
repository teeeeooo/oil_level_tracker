# S11 Local XY supplied specification and native evidence

Source basis: `167126e5f095e4011bc8f7dfd51049df87dd84f6`.
The supplied material is historical design/experiment input, not the live work
plan or an adopted production patch.

| Material | Placement / authority |
|---|---|
| [Specification](S11_Local_XY_Detector_Work_Spec_2026-10-09.md), [delivery summary](S11_Local_XY_Execution_Summary_2026-10-09.json), [handoff](HANDOFF.md), [original checksums](SHA256SUMS.json) | Four ZIP entries preserved byte-for-byte; the separately attached JSON is identical to the ZIP entry. |
| [Import manifest](import-manifest.json) | Package hashes, native-copy mapping, complete local archive and preservation boundary. |
| `native-evidence/` | Byte-preserved native runners, preflights, summaries, support readout, logs and four overview images, plus all eight run summaries. These are distinct from the derived delivery JSON. |
| [Intake review](../../60-evidence/s11/2026-10-09-local-xy-spec-intake.md) and [verification receipt](../../60-evidence/s11/2026-10-09-local-xy-spec-intake.json) | This checkout's independent verification, scoped adoption and corrections. The receipt inventories every one of the 165 native files. |
| [Read-only verifier](verify_saved_outputs.py) | Intake tool; validates pins, file formats, saved statistics and completed resolution without decoding video or rerunning the frame detector. |

Complete native data remains at
`sample/output/s11-local-xy-exclusion-20261009-001/`. A verified archive of all
165 files and the supplied ZIP are also preserved under
`sample/output/s11-local-xy-intake-20261009-001/`. The manifest pins both archives.
These local archives are not off-machine backups and are absent from a fresh
Git clone. Original files were neither moved nor deleted.

The native runners are historical source snapshots, outside production and test
discovery. They resolve the repository from their original `sample/output/<run>`
depth and some write derived output without an overwrite guard. Do not execute
the copies in this documentation directory or over the original results. A new
run needs its own directory and frozen inputs; the intake verifier takes an
explicit repository and a new output receipt path instead:

```bash
.venv/bin/python docs/70-reference/s11-local-xy-2026-10-09/verify_saved_outputs.py \
  --repo . --output sample/output/<new-intake-check>/verification.json
```

Pinned source/input changes stop this historical check. Use the
[Work Plan](../../00-project/work-plan.md) for current sequencing and the
[adopted proposal boundary](../../20-architecture/s11-interface-observability-witness-architecture.md#local-xy-oil-measurement-exclusion--proposed-contract)
for implementation. Supplied `WP1`–`WP5` are implementation tasks inside D2/W4;
they are not new O/W milestones.
