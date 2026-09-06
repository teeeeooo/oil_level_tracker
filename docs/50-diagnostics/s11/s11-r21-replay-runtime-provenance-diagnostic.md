# S11-R21 Replay Runtime Provenance Diagnostic

**Status:** `LOCAL RECONCILIATION COMPLETE / NO GOLDEN CHANGE`

## Problem

R18–R20 checked Sample4 tracking fingerprint `0f202947...`, while the current
R21 checkout produces `e447626b...`. The R21 closeout already established that
clean source base `d50c143` produces the same current fingerprint and that its
113 tracking rows are identical to R21 apart from `run_id`.

The remaining question is whether the mismatch can be attributed to media,
Recipe/truth input identity, source behavior, or replay runtime drift without
silently rewriting the historical golden.

## Reconciliation

The R20-era tracked sample authority records `sample4.mp4` SHA-256
`ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892`.
The current file has the same SHA-256. The current Sample4 Recipe SHA-256 is
`53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849`,
and all four current replay samples match the frozen authoritative
MP4/Recipe/truth identities in the S11 evidence-probe manifest.

Therefore the available evidence does not support media replacement or current
Recipe/truth drift as the cause. This diagnostic corrects the narrower R21
closeout interpretation that the historical ignored-media hash was unavailable;
the historical evidence record itself remains immutable. Exact R18–R20
Python/OpenCV/video-decoder build identity was not captured, so historical
runtime/dependency drift remains the named provenance gap.

## Maintenance change

The replay/evidence harness now records one `s11-replay-runtime-provenance-v1`
signature containing Python implementation/version, platform system/release/
machine, NumPy/OpenCV/package versions, full OpenCV build-information hash,
Video I/O/FFmpeg component versions and the active OpenCV video backend.

Before replay or performance profiling, MP4, `.oilrecipe` and `.oiltruth`
identities are compared with the frozen S11 manifest. Missing or mismatched
inputs fail before detector execution.

Exact tracking comparison is now classified separately from runtime identity:

- same runtime + same tracking fingerprint → `EXACT_MATCH`;
- same runtime + tracking mismatch → `TRACKING_MISMATCH_SAME_RUNTIME`, hard fail;
- different expected runtime + tracking mismatch → `ENVIRONMENT_DRIFT`; exact
  fingerprint is not promoted to a detector-regression claim, while ordinary
  row/numeric and downstream truth/provenance contracts remain active; and
- no historical runtime fingerprint + tracking mismatch →
  `UNCLASSIFIED_TRACKING_MISMATCH`, preserving the prior fail-closed behavior.

Performance evidence is stricter: when an expected runtime fingerprint is
provided, any runtime mismatch fails before timing because cross-environment
latency is not attributable comparative evidence.

## Current runtime witness

The maintenance verification runtime produced fingerprint
`7b14134e3f811d06e45ea2cd44686b5ffedd22dc7e2848fd2e04bd838f8aa20d`
with Python `3.14.4`, OpenCV `4.14.0`, NumPy `2.5.1`, backend `FFMPEG`,
`avcodec 61.19.101`, `avformat 61.7.100`, `avutil 59.39.100` and
`swscale 8.3.100`.

A real R18 Sample2 worker replay using that expected runtime fingerprint
returned the historical Sample2 tracking fingerprint `85713bc...` and
classification `EXACT_MATCH`. The input preflight validated all three Sample2
identities before detector execution.

This current runtime fingerprint is a witness for future comparison, not the
missing historical R18–R20 runtime identity. It must not be paired retroactively
with the historical Sample4 `0f202947...` golden.

The Sample4 historical golden remains unchanged. If an exact historical
runtime later becomes available, it can be replayed against `0f202947...`.
Otherwise current behavior comparison must continue to distinguish exact
reproducibility from reviewed truth/provenance acceptance.

## Detector Governance

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F09`, `S11-F10`
- First harmful stage: no detector harmful stage is established by the Sample4 fingerprint drift; the supported seam is replay provenance because current `d50c143` and R21 rows agree while the historical runtime signature is unavailable.
- Logic-map impact: NONE — production publication and trace owners are unchanged; this maintenance adds only diagnostic input/runtime provenance and comparison classification.
- Failure-registry impact: NONE — F09 already owns provenance ambiguity and F10 already forbids changing truth/goldens or detector behavior to fit one replay environment.
