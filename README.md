# Oil Level Tracker v2

A Windows desktop tool for compressor sight-glass oil inspections.

1. The app builds a context image from the inspection video.
2. It draws a draft oil line on that image.
3. The user corrects the lines on a graph linked to the source video.
4. The app computes the judgment, and the user submits a versioned report.

## Status

V2 started on 2026-10-28.
- Current state and next step: [docs/work-plan.md](docs/work-plan.md).
- Product decisions: [docs/decisions.md](docs/decisions.md).
- Visual rules: [DESIGN.md](DESIGN.md).

## v1

v1 was the automatic-detector application, from Phases 1–2 through S11. It
is preserved, unchanged:
- tag `v1-final`;
- branch `archive/v1`.

v2 does not read v1 Recipes or result bundles. Code is ported from v1 one
file at a time, after review.

## Stack

- **Back end:** Python 3.14. A local server bound to `127.0.0.1`.
- **Window:** pywebview, which uses WebView2 on Windows.
- **Front end:** plain JavaScript with no build step. One drawing module is
  shared by the editor and the report.
- **Target:** Windows. Development happens on macOS.
