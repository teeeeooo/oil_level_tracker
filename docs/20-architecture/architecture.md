# v2 Architecture

**Status:** `ACTIVE`.
- **2026-10-28:** the user decided on modules with one-way dependencies.
- **2026-10-29:** the user changed this to v1-style layers. Ports and
  adapters are wired in one place.
- **What v2 keeps from v1 is the philosophy,** not the detail. Its
  architecture is at `v1-final:README.md`, "Architecture".

This document owns the module boundaries, the dependency rule and the
cross-module principles. What the product does belongs to the
[Product SSOT](../10-product/product.md); how it looks belongs to
[DESIGN.md](../../DESIGN.md).

## Module map

```
src/oil_tracker/
  domain/          Recipe, Glass, JudgmentRule, Line (samples), Inspection;
                   judgment, events, FULL/EMPTY derivation.
                   Pure: no I/O, no NumPy, no OpenCV, no clock.
  application/     One module per use case, for example "analyse
                   inspection", "save version", "recompute judgment".
                   ports.py holds the ports (typing.Protocol).
                   Builds the data the editor and the report draw.
  adapters/
    video/         OpenCV and NumPy: one pass over the video for all
                   Glasses, context image, background-subtracted view,
                   Oil draft, frame reads.
    storage/       Recipe files, inspection folders, versioned edit
                   documents, context-image cache, schema versions,
                   SHA-256 of the source.
    report/        Self-contained report HTML; inlines web/render.js and
                   the DESIGN.md tokens.
    http/          HTTP API on 127.0.0.1 (standard-library
                   ThreadingHTTPServer): routes to use cases, job
                   progress, video file serving with HTTP Range.
                   API calls need the per-launch token and a local Host.
    desktop/       Operating-system integration: the native file dialog
                   (supplied by app.py from the pywebview window) and
                   opening a folder.
  web/             index.html, tokens.css (from DESIGN.md), render.js
                   (shared by editor and report), recipe.js, editor.js,
                   api.js. Plain JavaScript modules, no build step.
  bootstrap.py     Builds the concrete adapters and hands them to the use
                   cases. The only wiring point.
  app.py           pywebview window; owns process lifetime.
```

The modules are created as each work-order step needs them, not ahead of
time.

## Dependency rule

```
web ──(HTTP API only)──▶ adapters/http ──┐
adapters/video, storage, report ─────────┴──▶ application ──▶ domain
bootstrap.py ──▶ everything (wiring only)
app.py ──▶ bootstrap.py
```

- **`domain`** imports nothing from the package. It uses only the standard
  library.
- **`application`** imports only `domain` and the standard library.
  - No NumPy, OpenCV, HTTP or file I/O.
  - Image data, such as frames and context images, passes through it as
    opaque values. The adapters own their format.
- **Adapters** import `application` and `domain`, plus their own
  third-party libraries. They do not import each other.
  - When one needs another's output, a use case passes it on through a
    port.
  - `adapters/http` calls use cases; it never calls another adapter.
- **`bootstrap.py`** is the only place that constructs concrete adapters.
- **`web`** never reads files directly. Everything goes through the API.

## Ports

- **A port exists only at a real boundary:**
  - video reading and analysis;
  - Recipe and inspection storage;
  - the context-image cache;
  - report output;
  - progress and cancellation;
  - the desktop (file dialog, opening a folder).
- Internal helpers get no port.
- Use-case tests run with fake ports, without HTTP, files or OpenCV.

## Cross-module principles

- **The judgment is computed only in Python** (`domain`). The editor asks
  the API for a recomputed result. Judgment and event logic is never
  re-implemented in JavaScript.
- **`application` builds what the screen shows.** The editor and the
  report receive:
  - the line samples;
  - the FULL/EMPTY stretches;
  - the "cannot judge" stretches;
  - the events and the judgment.
  `render.js` draws only what it receives.
- **During a drag, only the lines redraw locally.** The FULL/EMPTY bands,
  the events and the judgment keep their last values. They update from the
  API response after the user releases.
- **Lines are dense samples at the analysis rate.**
  - The samples are plain Python values; they are the source of truth.
  - Grab-and-drag and the pencil are editor operations that produce new
    samples.
  - Each sample records where it came from: draft, edited or drawn.
  - `adapters/video` converts its Oil draft into domain samples.
- **FULL and EMPTY are derived in `domain`** from a sample's position
  relative to the Glass top and bottom. "Cannot judge" stretches are stored
  explicitly.
- **One drawing module.** `web/render.js` draws the graph and the context
  overlay for both the editor and the report. It has no dependency on the
  editor state, so the report can inline it.
- **Saved data carries a schema version.** Readers reject unknown future
  versions. There is no v1 reader. Each format has its own document:
  - [recipe-file.md](recipe-file.md).
- **Long work runs as a job.** Analysis is an example.
  - `application` reports progress and checks for cancellation through a
    port.
  - `adapters/http` runs the job on a thread.
  - The UI polls progress and the time left, and can cancel.
- **The source video** is referenced by path and SHA-256, and served to the
  built-in player with HTTP Range.

## What v2 does not take from v1

- separate `services/` and `use_cases/` directories;
- dozens of service modules;
- a port for every collaborator;
- the detector pipeline.

## Porting from v1

v1 code is ported one file at a time from tag `v1-final` after review, and
the source path goes in the commit message. Expected sources, all into
`domain/`:
- `domain/judgment.py` (`judge_samples`);
- `domain/recipe.py` (`JudgmentRule`);
- `domain/enums.py`.

Expected spike sources (branch `spike/webui`, `spikes/webui/`):
- the context build in `context.py`, into `adapters/video/`;
- the drawing code in `static/render.js`, into `web/`;
- the local server binding fix in `server.py` (no reverse-DNS lookup on
  bind), into `adapters/http/`.

## Testing

| Layer | Test |
|---|---|
| `domain` | Unit tests with fixed cases. This is where the judgment criterion A3 is proven |
| `application` | Use-case tests with fake ports |
| `adapters/video` | Unit tests on small synthetic videos and arrays |
| `adapters/storage` | Round-trip, versioning, locking and schema-version tests |
| `adapters/report` | Output tests on fixed screen data |
| `adapters/http` | API tests against a running local server, wired by `bootstrap.py` |
| `web` | Browser smoke checks with Playwright on macOS (`--channel chrome`). Windows behaviour is confirmed only by Windows runs |
