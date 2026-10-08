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
assertions. S11 governance and whitespace checks pass. The local `docs-check.json`
records this bounded check; full detector or Windows execution was not performed
for the document/cleanup scope.

D1 needs the original Windows W3 `experiment.json`, whose raw SHA-256 is
`ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f`.
The [transferred W3 report](s11-o2-w3-target-audit-windows-run-001.md) names output
alias `experiments/target-context-audit-001`; no absolute Windows path is inferred.
The local `sample/output` filename inventory found no `experiment.json`; a saved
search receipt is in the intake directory. Private data are not reconstructed
from the prose report. Prepare the existing reader and handoff, then stop at the
Windows boundary. D2's concrete algorithm and new physical discrimination remain
unestablished; no blank classifier or production guard relaxation is introduced.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F09`, `S11-F10`.
- First harmful stage: no new detector execution; prior cellular replay records loss before the selector, while the original Windows loss seam remains unknown pending recorded filter data. Document intake and archive integrity cannot establish physical identity or field repair.
- Logic-map impact: NONE — the change preserves source artifacts and current-state routing without changing executing detector ownership or control flow.
- Failure-registry impact: NONE — rejected experiments remain closed and no new causal failure or accepted detector mechanism is asserted.
