# Windows diagnostic A/B: chromatic overlay support

**Prepared, NOT RUN.** This compares an unadopted mask candidate with its baseline.
The candidate has a known failing local sequence test; it is **not a locally
qualified release**. The user requested a stop when Windows work becomes needed.
No private media is executed by the Mac preparation task.

Read the [local result and failure](../60-evidence/s11/2026-10-14-overlay-support-guard.md),
[candidate contract](../20-architecture/s11-chromatic-overlay-support-design.md),
and [current field procedure](s11-current-windows-field-qualification.md).
The [reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
and its JSON companion own all nine segment judgments. This handoff changes no
truth, acceptance threshold or Recipe and does not authorize ignoring local FAIL.

## Exact identities

| Item | Identity |
|---|---|
| Baseline Git commit | `747c1bccaa8dab18d6cb3a2b3dc3e549bcfc668f` |
| Candidate code freeze | `0073defdd34d71c489f63acb4af574a244e7447d` |
| Published candidate branch | `work/s11-overlay-component-20261014` — record the fetched, checked-out full SHA |
| Candidate `src` Git tree | `4d5bb8217685d57802917d180b42de3424251f7d` |
| Candidate preprocessing SHA-256 | `c25950c59b604c74f35db8973130a81078e8658c8cc571a3464a2855ec17b902` |
| Baseline `src` Git tree | `d0734d84930f11637eb207e019846b10be3f2eda` |
| Detector version, both variants | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| Resolver version, both variants | `r22-oil-ownership-evidence-replacement-v1` |

Only preprocessing differs in production source. The unpromoted experiment has
not minted a release version; **version strings alone cannot distinguish these
variants**. Record Git SHA, source tree, preprocessing hash and runtime for each.
Later evidence/documentation commits may accompany the candidate but must retain
the exact source tree above. A source-tree mismatch requires a new review.

## Single-checkout preparation

Use the existing Windows development environment, with no concurrent analysis.
Preserve any local changes before checkout; the commands stop if the tree is dirty.
The private video and existing Recipe paths remain local to the operator.

```powershell
if (git status --porcelain) { throw 'Preserve local changes before switching.' }
$originalRef = git symbolic-ref --quiet --short HEAD
if (-not $originalRef) { $originalRef = git rev-parse HEAD }
git fetch origin work/s11-overlay-component-20261014
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed.' }
$candidate = git rev-parse FETCH_HEAD
$baseline = '747c1bccaa8dab18d6cb3a2b3dc3e549bcfc668f'
if ((git rev-parse "${candidate}:src") -ne '4d5bb8217685d57802917d180b42de3424251f7d') {
    throw 'Candidate source changed; do not blend evidence.'
}
git switch --detach $baseline
if ($LASTEXITCODE -ne 0) { throw 'Baseline checkout failed.' }
git rev-parse HEAD
git rev-parse HEAD:src
$env:PYTHONPATH = Join-Path $PWD 'src'
& .\.venv\Scripts\python.exe -m oil_tracker
```

Run the existing production GUI workflow on the original private source with
its reviewed Recipe, source interval **480–780 s**, identical sampling and
initial-state confirmation in both runs. Reuse the established 2 Hz setting
unless the existing field setup specifies otherwise; record it, never change it
between variants. Keep Recipe/ROI/Artifact/exclusion settings identical, with
Local XY OFF. Use separate output directories and names indicating baseline or
candidate. Confirm the actual analysis-start frame for every enabled Glass;
do not silently edit a Recipe to bypass confirmation. Preserve original reports,
tracking/events CSV and available trace, plus runtime and resource measurements.

Close the GUI before switching and run the candidate through the same workflow:

```powershell
if (git status --porcelain) { throw 'Preserve local changes before switching.' }
git switch --detach $candidate
if ($LASTEXITCODE -ne 0) { throw 'Candidate checkout failed.' }
git rev-parse HEAD
git rev-parse HEAD:src
$pre = (Get-FileHash 'src/oil_tracker/adapters/vision/preprocessing.py' -Algorithm SHA256).Hash.ToLower()
if ($pre -ne 'c25950c59b604c74f35db8973130a81078e8658c8cc571a3464a2855ec17b902') {
    throw 'Unexpected preprocessor.'
}
& .\.venv\Scripts\python.exe -m oil_tracker
```

After both runs close, restore the original checkout with `git switch $originalRef`
only if `git status --porcelain` is empty. Preserve results separately; do not
overwrite bundles or push private media. Record the source alias
`windows_sample1_heating_coldstart`, SHA-256, byte size, dimensions, FPS and duration
without the real filename, as required by the canonical procedure. No private
path or hash is invented by this handoff.

## Required return and decision boundary

Return the recorded Git/source/runtime identities and results for every segment:
`WS1-BASE-FULL-PREFIX`, `WS1-BASE-DRAIN`, `WS1-BASE-RAPID-REFILL`,
`WS1-BASE-FULL-SUFFIX`, `WS1-ACCUM-EMPTY`, `WS1-ACCUM-ENTRY-SPLASH`,
`WS1-ACCUM-FOAM-LAYERED`, `WS1-ACCUM-POST-FOAM`, `WS1-ACCUM-DRAIN`.
Use the canonical per-segment report fields and PASS/FAIL/NOT_EVALUATED semantics.

Specifically assess whether released chromatic regions expose actual fluid
interfaces or new structure/glare/splash owners, and whether Oil/Foam publication
preserves reviewed identity, direction, ordering and no-interface intervals.
Do not choose the variant by numeric count or use a graph bridge as observation.
Where trace exists, connect changed output to its same-frame candidate and mask;
otherwise retain causal uncertainty. Exact source-Y accuracy is NOT_EVALUATED
where the canonical owner has no reviewed anchor.

The local sample3 integration failure remains an explicit unresolved adoption
item even if the field comparison is favorable. Do not delete or rewrite that
test, widen its barrier, or claim FIELD PASS from this handoff. The current
Work Plan owns the subsequent decision; the accepted baseline remains unchanged.
