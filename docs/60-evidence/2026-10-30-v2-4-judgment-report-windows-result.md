# V2-4 judgment, submitting and report on the workstation — Windows result (2026-10-30)

**Verdict:** V2-4 does not close yet. Every judgment, submitting and
report row passes; two fixed criteria do not:
- **U1 fails:** with "수평·수직" on, an upright pencil stroke still draws a
  slant (as C4 did in the [re-check](2026-10-30-v2-3-editor-recheck-windows-result.md)).
- **R2's last condition fails:** the SPL#4 inspection has a working copy
  saved at 07:27:14, after v2 was submitted (07:24:28), where `edits
  none` was expected.

The user's two notes ask for changes to the editor's right column and the
report's first page; they wait on the user's decisions with U1.

- **Source run:** commit `95de064`, from the
  [request](../40-operations/2026-10-30-v2-4-judgment-report-windows-request.md)
  (`checked=95 mismatched=0`).
- **Who ran it:** the Windows agent ran §0–§4 and §6; the user worked the
  app and the browser (§5). Python 3.14.3.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=95 mismatched=0` | **pass** |
| B | `files_src` = `files_backup` | **pass**: 34 and 34 |
| S2 | `242 passed, 4 skipped` | **pass** (22.85 s) |
| C | J1–J18, U1, U2 all O | **fail**: U1 X; the rest O |
| T | no `Traceback` until the window closed | **pass**: stdout and stderr empty |
| R1 | `inspections=4 unreadable=0` | **pass** |
| R2 | SPL#4 1907: header `V24-모델` / `V24-시험2`; v1 and v2 with `report_bytes` ≥ 1; ACCUM `override` set and `reason_chars=13`, BASE `override=-`, in both; `edits none` | **fail on the last condition**: the rest holds (`report_bytes=99966` and `99968`, ACCUM `override=PASS`, computed `REVIEW`); an `edits saved_at=2026-10-30T07:27:14` working copy is there |
| R3 | SPL#1 1913: one `version v=1`, `report_bytes` 1–5,000,000 (A7); `checked_at` after §3's `saved_at`; `edits none` | **pass**: `report_bytes=377328` for 68 minutes; `checked_at=07:35:29` after `04:17:51`; the user found it opened quickly |
| R4 | 1910 and `V2-3 확인` as in §3; all `sha256_check=same` | **pass** |

**Schema 1 files read:** before the run all four inspections had
`header compressor_model="" test_type=""`, and the V2-3 edits of 1913 opened
undecided (J15).

## The two failures

**R2: a v3 working copy, most likely started by "고쳐서 다시 제출 (v3)…".**
On a locked version the server refuses saving, the header and
re-analysis; the only path that writes `edits.json` is revising, which
copies the latest version's edits. The working copy equals v2's: BASE
`oil=466/54/0/26` (J5's drag), both Glasses checked, ACCUM `override=PASS`
with 13 characters. It was written at 07:27:14, between J14 (v2's report)
and J15. To confirm with the user: the list would show "v3 고치는 중" for
1907. If so, the app did as designed and the step's wording, not the code,
left it.

**U1: an upright stroke is a 0.5 s slope.** A line holds one height per
sample, 0.5 s apart. The upright stroke (`lines.upright`, `ca7d3ee`) sets
the pressed sample at the pressed height and the next one at the
pointer's, so the riser spans 0.5 s, and the sample after that keeps its
old height, so the stroke is a narrow spike "/\". Zoomed in, both edges
read as slants. No change to the stroke code can draw a truly vertical
riser between samples; what the user wants the line to be after an
upright stroke is the user's decision.

## The user's notes

| Note | Outcome |
|---|---|
| The right column holds too much (원본 영상, Glass, 판정, 검사 정보, 메모, 분석). Enter 검사 정보 at submitting, not in the right column. Memos from a toolbar button: a memo list with 추가 (as now) and 삭제 (pick one or more, then 삭제). Order: 원본 영상 → 편집 → 판정 → the rest | Waits on the user's decisions, then mock-ups (DESIGN.md §5 changes) |
| The report's first page squeezes the graph and the context image under the header. Page 1: the inspection facts, the judgment and every Glass's graph (squeezed is fine); then one page per Glass | Waits on mock-ups (DESIGN.md §5 "Report" changes) |
