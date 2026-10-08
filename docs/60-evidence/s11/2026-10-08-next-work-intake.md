# S11 next-work intake and local results preservation — 2026-10-08

## Scope and baseline

Starting main: `49c6d3aebeaf90aea96cd5be4c0e91115011f5a7`, clean.
Remote main and the two diagnostic branch heads were checked through Git on
October 8 and matched main, `c4814bdc25c4da22776d985fbb7a2d66fbc4e1e8`
and `e5d4a0430ea69beab59736396a2817c09b5efd69` respectively.
The user authorized staged execution, results-folder disposition, logical
commits and push, with a stop when human judgment or Windows work is needed.

This record owns this intake's document integration, preservation and checks.
[Work Plan](../../00-project/work-plan.md) owns live state and authorization.
FIELD FAIL, W4/O2 acceptance, A0Q stability and independent report comprehension
remain unresolved. No detector/source-media/recipe/truth change or field run
is established here.

## Source import and succession

The supplied [specification](../../70-reference/s11-next-work-2026-10-08/S11-next-work-spec-2026-10-08.md)
and [shared verification](../../70-reference/s11-next-work-2026-10-08/S11-next-work-verification-2026-10-08.json)
are preserved byte-for-byte; only attachment transfer prefixes are removed from
filenames. [Import manifest](../../70-reference/s11-next-work-2026-10-08/import-manifest.json)
records their hashes, local artifacts and immutable source-commit links.

Verified during this intake:

- supplied specification SHA-256 `49d05c64046b4e74c2cbde208a64c89c147f642b90404c81cd70e9113f9ac00d`, matching the supplied JSON;
- cellular handoff ZIP SHA-256 `b9c08d8e9449f1f180826b1bc690a6d26162731a7e2588753e1c3240c26d046e`;
- Windows-first handoff ZIP SHA-256 `f1304ef519d933b1d62f717386f5093252766657fce96efe2e59f2c85e480379`;
- local audit receipt SHA-256 `73692f779bd422f884591d78c14bea6225cd1026a03503995e6273950ab73deb`.

The shared JSON is not a byte-identical copy of that local receipt. The source
audit's 872 member checks, 36-frame review and 294 tests are attributed previous
results, not repeated measurements in this intake. Production source,
dependencies, recipes and truth agree between main and the diagnostic delivery;
the whole delivery is not merged. Its fixed experiments stay closed without promotion.

The Work Plan was compacted from 617 lines to a current-state ledger and linked
obligations. Its starting bytes are recoverable at the starting Git commit and
in the local intake directory. Current O/W stages remain; D names are task aliases.
Accepted behavior/diagnostic/report baselines, field disposition, authorization,
named unknowns and closed human judgments are preserved. Completed detail stays
in existing evidence/diagnostic owners, including the uncertain Foam front,
unadopted ROI, paired-pulse controls and independent-data requirements.
Roadmap, retained commitments, validation contracts, reviewed truth and older
supplied audit originals retain their bytes and responsibilities.

## Results-folder disposition

The named sibling `../oil_level_tracker-s11-audit-20261007-results` was a standalone
results directory, not a registered worktree. Previous source-recovery ZIPs do
not constitute a complete backup of these results. No open handles were found.

All **279 files and 77 directories** were preserved, including the original
failed-run logs, images, cache files and filesystem metadata files; no content
exclusions were made. Original file bytes total **85,750,882**. Each archived file
was rehashed, the ZIP passed integrity checking, and extraction into a temporary
directory reproduced the complete path/content inventory. POSIX modes are recorded
in the manifest; ordinary ZIP extraction does not restore them automatically.

Local recovery directory:

```text
sample/output/s11-next-work-intake-20261008-001/
  s11-audit-20261007-results-preserved.zip
  results-manifest.json
  results-cleanup-receipt.json
  preserve_results.py
  remove_preserved_results.py
  work-plan.before.md
```

The archive is **16,229,676 bytes**, SHA-256
`3e20c1939ab0d07708c05f54afe4bfaaf5b199b572ddb11059548cbeef5147b8`.
Manifest SHA-256 is
`978cb78d4911eda3c65a432fc0118edb8c115dca9edc4173e04a6c9439826ac0`.
The [cleanup receipt](../../70-reference/s11-next-work-2026-10-08/results-cleanup-receipt.json)
records exact paths and checks. Immediately before removal the source inventory,
all hashes, archive/manifest hashes, worktree registration and open handles were
rechecked. The original directory was then removed. Net allocated file space
reclaimed, accounting for the ZIP, is **70,119,424 bytes** (about 66.9 MiB), before
the small receipts/scripts. The recovery archive stays local and ignored by Git;
no image or native experiment payload is uploaded by this change.

Restore by extracting the ZIP into a **new directory** and reading `manifest.json`;
`results/` contains every original path. Compare file sizes/SHA-256 with the
manifest before use. Historical scripts retain their original absolute paths;
adapt copies for a new execution and never rewrite archived originals.
The previous source recovery material remains separate and unchanged.

Only main is registered as a live Git worktree. The Windows-first and spatial
worktrees were already removed according to their matching cleanup receipts.
Their unmerged branches, both handoff ZIPs and existing audit receipts remain.
Merged report branches were not deleted merely to shorten the branch list.

## Verification and next boundary

Initial document checks pass: 451 local links/anchors across the changed Markdown,
imported hashes, protected roadmap/retained-commitment/Windows-truth bytes,
commit-pinned source existence, incoming Work Plan anchors and 17 named-obligation
assertions. S11 governance and whitespace checks pass. The local `docs-check-stage1.json`
records this bounded check; full detector or Windows execution was not performed
for the document/cleanup scope.

D1 initially used the transferred Windows W3 `experiment.json` raw SHA-256
`ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f`.
The [transferred W3 report](s11-o2-w3-target-audit-windows-run-001.md) names output
alias `experiments/target-context-audit-001`; no absolute Windows path is inferred.
The local `sample/output` filename inventory found no `experiment.json`; a saved
search receipt is in the intake directory. Private data are not reconstructed
from the prose report. Prepare the existing reader and handoff, then stop at the
Windows boundary. D2's concrete algorithm and new physical discrimination remain
unestablished; no blank classifier or production guard relaxation is introduced.

## D1 reader reuse and Windows handoff

Preparation is complete on main after the documentation intake `df74414`.
Only the following two files were reused byte-for-byte from diagnostic delivery
`e5d4a0430ea69beab59736396a2817c09b5efd69`; no failed challenger code was adopted:

| File | SHA-256 |
|---|---|
| `tests/diagnostics/s11_candidate_loss_audit.py` | `c5c4b058cc7d15d25006ab739bb8e851d4f00fe6f4f271c330817536110aad60` |
| `tests/unit/test_s11_candidate_loss_audit.py` | `b03a27f1660f31d36fbe289ad1724b330741fa47bb1156fecdd2da0e5fa53db8` |

Fresh verification: **40 passed in 0.34 s** using the existing project environment.
These include phase/owner filtering, absent/contradictory records, same-frame
selection identity, immutable inputs, fail-closed hash/schema checks, standalone
CLI from a foreign cwd with Unicode paths, and compatibility with the existing
W3 producer. The original 294-test audit is not added to this count.

The standalone handoff ZIP contains this exact reader, README and SHA256SUMS:

```text
sample/output/s11-next-work-intake-20261008-001/
  s11-d1-windows-readout-2026-10-08.zip
```

ZIP SHA-256: `6f5ac25f104c95ddf3f4f49ceab37e714879f9d8b27eacfad6fef2c9e9e8648c`.
Every ZIP member was verified. A separate packaging smoke extracted it and ran
the CLI with isolated Python (`-I`), a foreign cwd, Unicode paths and the existing
synthetic audit fixture. Source bytes, script identity and output hashes passed.
This is local macOS execution, not Windows or private-W3 acceptance. The logs,
JUnit XML, reader pins, package receipt and smoke receipt remain in the local
intake directory. No new permanent loader or evaluation framework was introduced.

The [D1 operation](../../40-operations/s11-o2-local-shadow-evaluation.md#d1-recorded-candidate-loss-readout--windows-handoff)
contains the exact PowerShell command, hash checks, named candidate questions,
bounded return and stop conditions. The required original audit is unavailable
here, so **D1 Windows readout is pending and work stops for the user's Windows
handoff**. D2–D6 are not executed. The reader does not import the passive batch's
target roles; physical annotations, candidate membership and missing fields retain
their recorded scope. Production code/dependencies/recipes/truth remain unchanged.

## Windows hash correction received — 2026-10-08

The first Windows attempt stopped on hash mismatch. The user then supplied
`ba5fe84b28473f7e387e363ef7d40877f559c80b1852755d997e1dd04171937f`
as the actual Windows hash and suspected transcription error. The
[attributed correction](s11-o2-w3-target-audit-windows-run-001.md#d1-raw-file-pin-correction--2026-10-08)
retains the earlier value and its uncertainty. Work Plan and the D1 operation
now use the corrected execution pin, with file-hash and original audit-identity
confirmation on Windows. Source audit attachments, the initial ZIP/receipts and
historical results remain byte-preserved. The initial ZIP README's input pin is
superseded by this correction; its reader is unchanged and remains usable.
No source download or code change is needed to pass the corrected CLI argument.
D1 completion, physical cause and O2/field acceptance are still pending.

## D1 Windows return received — reconciliation open

Historical checkpoint: the bounded request below was subsequently answered in
[D1 saved-record reconciliation — closed](#d1-saved-record-reconciliation--closed).

The user returned a pasted Windows final report after the corrected pin was
supplied. This is attributed execution evidence; the original `complete.json`,
`summary.md` and `readout.json` bytes were not supplied or read locally.
The instructed source commit was `c9e99d2`, not an independently inspected
Windows checkout identity. The report states Python 3.14.3 on Windows 11,
the expected reader hash, schema `s11-o2-target-audit-v1`, the corrected raw
input hash before/after, and 23/23/27 candidates. It reports successful output
hash checks, `COMPLETE`, and false detector/video/auto-acceptance flags.

Reported output hashes:

- `readout.json`: `e4bf75c4e63c2a0a3fe169a3ff3bb72b99a3e2fbf504ca352358fe55ff923004`;
- `summary.md`: `921fb9fd541295cc26ad60454cf8435a46193fc2f7bdac12d4a20ad14933fe13`.

Output is `d1-candidate-loss-001` beneath the existing first target/context audit
directory on Windows. No local rehash of these outputs is claimed. The returned
report confirms the corrected input pin as Windows-measured; the cause of the
earlier transcription mismatch remains unproven.

### Consistent named-candidate statements in the return

| Candidate | Reported recorded boundary | Meaning and limit |
|---|---|---|
| review-002 idx0 / review-003 idx10 | `UNKNOWN_BEFORE_RETAINED_REFS` | No member/row record; earlier cause unavailable, not a proven generation/top-k failure |
| review-002 idx10/12/16 | `TRACKLET_NOT_ADMITTED` | Continuation authority; row/phase/publishability exclusions also reported. Fixed readout ordering is not proof of the first physical cause |
| review-002 idx8/9 | `PHASE_HARD_GATE` | Admitted/publishable row under `INITIAL_FULL_BARRIER`, `hard_gate`, empty allowed IDs |
| review-003 idx19 | `OWNER_NOT_ALLOWED` | Row owner `oil-tracklet:000388:0186` differs from allowed `oil-tracklet:000381:0181` |
| review-002 idx20, non_interface | `PHASE_HARD_GATE` | Negative also has all three admission flags true; admission does not certify identity |

These are internally consistent with the pinned reader and the earlier named
candidate record. They remain transferred statements rather than independently
reconstructed physical truth. They do not justify relaxing phase/owner gates.

### Local consistency findings

Arithmetic on the pasted identity/boundary table yields:

| Case | Before-retained unknown | Tracklet not admitted | Phase hard gate | Owner not allowed | Total |
|---|---:|---:|---:|---:|---:|
| review-001 | 12 | 11 | 0 | 0 | 23 |
| review-002 | 7 | 9 | 7 | 0 | 23 |
| review-003 | 9 | 8 | 0 | 10 | 27 |
| Total | 28 | 28 | 7 | 10 | 73 |

The total inventory is arithmetically consistent, but three distinctions require
correction or reconciliation before closing the handoff:

1. `selected_candidate=None` with the key present records **no selected candidate**.
   The reader emits `selection_outcome=NONE_SELECTED` for recorded members in
   this situation. `FINAL_SELECTION_UNRESOLVED` is a *candidate boundary* only
   when no recorded exclusion applies and the phase filter is available. The
   report's named gated candidates keep `PHASE_HARD_GATE`/`OWNER_NOT_ALLOWED`;
   the supplied aggregate has zero `FINAL_SELECTION_UNRESOLVED` entries. A null
   selected value is not an absent selection record. `ADMITTED` is not a boundary
   enum emitted by this reader.
2. The earlier [W3 report](s11-o2-w3-target-audit-windows-run-001.md#recorded-funnel-facts)
   lists review-001 as 7 `not_selected`, 7 `tracklet_not_admitted`, 9 absent refs
   and reports seven admitted negative rows. The new report instead gives
   11 tracklet rejections and 12 absent refs, with no admitted candidates.
   Refining phase filters cannot change retained membership. Neither report is
   silently substituted for the other: the first needs 14 retained members,
   the second 11. Overall prior 48 retained/25 absent versus new 45/28 is
   unreconciled. Differences in terminology alone cannot explain the absent count.
3. A missing member under `NOT_IN_RETAINED_REFS` is **unavailable**, not measured
   `tracklet_admitted=false`. The review-001 blanket wording must preserve this.
   All 73 candidates being listed does not mean all earlier loss causes are known.

The local check recomputed these sums and exercised the existing reader with
its existing synthetic fixture under hard-gate, excluded-owner and unconstrained
conditions. Each returned `NONE_SELECTED`, with its distinct expected boundary.
This verifies interpretation only; no Windows or detector rerun was performed.
The check receipt is local `d1-return-consistency-check.json` in the intake directory.

### Narrow Windows return still required

Read the already saved files only. Return the generated `summary.md` and
`complete.json`, plus a machine-extracted 23-row review-001 table joined by
`candidate_input_index` between the original audit's `recorded_funnel` and the
saved readout. Preserve original status, legacy first-known loss, presence/value
of member admission and row flags, and new boundary/exclusions/selection outcome.
Check that `readout.source_funnel` equals the original case's funnel and its
recorded logical hash; separately recheck the existing raw input/output pins.
Keep missing, null and false distinct. Return grouped counts directly from these
fields, without recreating an audit or rewriting the generated output.

See the [bounded reconciliation procedure](../../40-operations/s11-o2-local-shadow-evaluation.md#d1-return-reconciliation--saved-review-001-only).
At this checkpoint the execution was **reported complete**, but evidence
reconciliation remained OPEN. Work stopped for the Windows saved-record check;
D2–D6 had not started. The following return resolves that check without changing
FIELD FAIL or O2 acceptance.

## D1 saved-record reconciliation — closed

The user returned a second Windows report answering the bounded review-001
query. It reports unchanged before/after hashes for the four saved files,
matching existing input/output/tool pins, original/readout funnel deep equality,
matching funnel fingerprint, 23/23 witness hashes and zero legacy-loss or boundary
mapping mismatches. These remain **user-transferred Windows checks**: the raw
JSON/Markdown files were not supplied or independently hashed in this checkout.
The reported `complete.json` hash (`0c452760...966610`) and funnel fingerprint
(`f6e6cfe0...f895179`) are abbreviated and are not usable as new full execution pins.
The full input/readout/summary pins in the earlier return remain unchanged.

Reported review-001 source identity:

- frame: `11508`;
- Glass: `8f94fb85-d98e-4c71-9c97-3085168be1b2`;
- packet SHA-256: `d6ba31d9957322b39ab7d97f902c97cd1169477951b180921c0e6849ae7d117c`.

The returned ranges expand to the following disjoint original candidate indices:

| Original status / legacy loss | Indices | Count | D1 boundary |
|---|---|---:|---|
| `RECORDED` / `tracklet_not_admitted` | 1,2,6,7,11,13,14,15,17,18,21 | 11 | `TRACKLET_NOT_ADMITTED` |
| `NOT_IN_RETAINED_REFS` / `UNKNOWN_BEFORE_RETAINED_REFS` | 0,3,4,5,8,9,10,12,16,19,20,22 | 12 | `UNKNOWN_BEFORE_RETAINED_REFS` |
| `not_selected` legacy loss | none | 0 | none |

All 23 have recorded physical identity `non_interface`. The 11 recorded members
have `tracklet_admitted=false`, `selected=false`, `phase_admitted=false`,
`publishable=false`. Their four exclusions are `TRACKLET_NOT_ADMITTED`,
`ROW_NOT_PHASE_ADMITTED`, `ROW_NOT_PUBLISHABLE`, `PHASE_HARD_GATE`; their selection
outcome is `NONE_SELECTED`. The other 12 have no member/row or selection-outcome
field, rather than false admission or an inferred selection outcome.
All `final_choice_diagnosed` values are false. Review-001 phase is
`filled_barrier / INITIAL_FULL_BARRIER / hard_gate / []`; selection is recorded as
`resolved_kind=unknown`, `selected_candidate=null`. Recovery is reported EVALUATED,
direct/delayed NOT_EVALUATED, with null sequence positions.

### Correction and limits

The original audit and D1 readout agree **according to this saved-record check**.
The discrepancy was between the earlier transferred W3 table and these saved
records. Adopt the latter for this input: review-001's legacy loss counts are
0 `not_selected` / 11 tracklet rejections / 12 absent refs. The old 7/7/9 table and seven-admitted-negative claim
are superseded, not an additional dataset. The earlier report's provenance/error
cause is not reconstructed. With review-002/003 unchanged, total retained/absent
counts are **45/28**, replacing 48/25. The supplied specification and verification
originals remain byte-preserved; their inherited 48/25 and review-001 admitted
example must be read with this correction. Labels/packets are unchanged.

One explanatory sentence in the latest return calls review-002 `filling`.
It supplies no new review-002 field extraction and conflicts with the earlier D1
case table and W3 record: review-001 and review-002 are `filled_barrier`,
`INITIAL_FULL_BARRIER`, `hard_gate`; review-003 is `filling`, `owner_bounded`.
Do not adopt that sentence or infer different phase rules. Review-001 shows no
admitted negatives. The narrower supported counterexample remains **within
review-002**: interface idx8/9 and non-interface idx20 pass the same three row/
tracklet flags and are all blocked by the same hard gate. This is recorded
admission, not proof of physical identity, target role or scalar eligibility.

The local check expands the reported ranges, checks that each index 0..22 appears
once, and recomputes 11/12, total 73, retained/absent 45/28 and the four boundary
totals 28/28/7/10 from the transferred reports. It does not re-execute D1 or inspect
Windows artifacts. Receipt: local `d1-reconciliation-return-check.json` in the
intake directory. No full detector tests are repeated for this documentation change.

**Disposition: D1 CLOSED — recorded readout only, with named unknowns.** The
requested readout and review-001 reconciliation are complete at the transferred
evidence scope; no further Windows lookup, missing-original request or rerun is
required for D1. Pre-retention causes for 28 candidates, actual first physical
failure and final causal selection diagnosis remain unknown. Null final selection
remains a recorded `NONE_SELECTED`, not a `FINAL_SELECTION_UNRESOLVED` boundary.
No identity model, phase-gate repair, O2 acceptance or field recovery follows.
The next local stage is D2's concrete observable/control design under the current
architecture and validation owners; FIELD FAIL/O2 OPEN are unchanged.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F09`, `S11-F10`.
- First harmful stage: no new local detector execution. The Windows D1 return reports phase hard-gate and excluded-owner boundaries for named admitted members; review-001 saved-record reconciliation supersedes the old inventory. Pre-retention causes and the first physical cause remain unknown. Recorded exclusions do not establish a successful field repair.
- Logic-map impact: NONE — the change preserves source artifacts and current-state routing without changing executing detector ownership or control flow.
- Failure-registry impact: NONE — rejected experiments remain closed and no new causal failure or accepted detector mechanism is asserted.
