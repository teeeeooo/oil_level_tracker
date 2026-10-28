# v2 Architecture

**Status:** `ACTIVE`. Decided by the user on 2026-10-28: feature modules with
one-way dependencies.

This document owns the module boundaries, the dependency rule and the
cross-module principles. What the product does belongs to the
[Product SSOT](../10-product/product.md); how it looks belongs to
[DESIGN.md](../../DESIGN.md).

## Module map

```
src/oil_tracker/
  domain/     Recipe, Glass, JudgmentRule, Line (samples), Inspection;
              judgment and event computation. Pure: no I/O, no OpenCV,
              no clock.
  analysis/   One pass over the video for all Glasses: context image,
              background-subtracted view, Oil draft. NumPy and OpenCV.
  storage/    Recipe files, inspection folders, versioned edit documents,
              context-image cache, schema versions, SHA-256 of the source.
  report/     Self-contained report HTML; inlines web/render.js and the
              DESIGN.md tokens.
  server/     HTTP API on 127.0.0.1 (standard-library ThreadingHTTPServer),
              job progress, video file serving with HTTP Range.
  web/        index.html, tokens.css (from DESIGN.md), render.js (shared by
              editor and report), recipe.js, editor.js, api.js.
              Plain JavaScript modules, no build step.
  app.py      pywebview window bootstrap; owns process lifetime.
```

The modules are created as each work-order step needs them, not ahead of
time.

## Dependency rule

```
web ──(HTTP API only)──▶ server ──▶ analysis / storage / report ──▶ domain
app.py ──▶ server
```

- `domain` imports nothing from the package.
- `analysis`, `storage` and `report` import only `domain` and the standard
  library or their third-party libraries. They do not import each other.
  When one needs another's output, `server` passes it in as a domain object.
- `server` is the only composition point. It owns the use-case functions,
  for example "analyse inspection" or "save version".
- `web` never reads files directly. Everything goes through the API.

## Cross-module principles

- **The judgment is computed only in Python** (`domain`). After an edit the
  editor asks the API for a recomputed result. The judgment and event logic
  is never re-implemented in JavaScript.
- **Lines are dense samples at the analysis rate.**
  - The samples are the source of truth.
  - Grab-and-drag and the pencil are editor operations that produce new
    samples.
  - Each sample records where it came from: draft, edited or drawn.
- **FULL and EMPTY are derived** from a sample's position relative to the
  Glass top and bottom. "Cannot judge" stretches are stored explicitly.
- **One drawing module.** `web/render.js` draws the graph and the context
  overlay for both the editor and the report. It has no dependency on the
  editor state, so the report can inline it.
- **Saved data carries a schema version.** Readers reject unknown future
  versions. There is no v1 reader.
- **Long work runs as a server-side job.** Analysis is an example. The UI
  polls progress and the time left, and the job can be cancelled.
- **The source video** is referenced by path and SHA-256, and served to the
  built-in player with HTTP Range.

## Porting from v1

v1 code is ported one file at a time from tag `v1-final` after review, and
the source path goes in the commit message. Expected sources:
- `domain/judgment.py` (`judge_samples`);
- `domain/recipe.py` (`JudgmentRule`);
- `domain/enums.py`.

Expected spike sources (branch `spike/webui`, `spikes/webui/`):
- the context build in `context.py`;
- the drawing code in `static/render.js`;
- the local server binding fix in `server.py` (no reverse-DNS lookup on
  bind).

## Testing

| Layer | Test |
|---|---|
| `domain` | Unit tests with fixed cases. This is where the judgment criterion A3 is proven |
| `analysis` | Unit tests on small synthetic videos and arrays |
| `storage` | Round-trip, versioning, locking and schema-version tests |
| `server` | API tests against a running local server |
| `web` | Browser smoke checks with Playwright on macOS (`--channel chrome`). Windows behaviour is confirmed only by Windows runs |
