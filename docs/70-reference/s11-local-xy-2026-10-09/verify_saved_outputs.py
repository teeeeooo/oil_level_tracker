"""Read-only intake check of the native Local XY outputs; never decodes video.

Run with the repository venv, --repo ROOT and a new --output receipt path.
The saved source/input pins must still match. This verifies reproduction of
completed resolution and delivered statistics, not physical detector efficacy.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from copy import deepcopy
import csv
from dataclasses import asdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_text())


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        self.refs.extend(v for k, v in attrs if k in ("src", "href") and v)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    assert not args.output.exists(), args.output
    native = root / "sample/output/s11-local-xy-exclusion-20261009-001"
    supplied = Path(__file__).resolve().parent
    pre = read(native / "preflight.json")
    summary = read(supplied / "S11_Local_XY_Execution_Summary_2026-10-09.json")
    for name, digest in read(supplied / "SHA256SUMS.json").items():
        assert sha(supplied / name) == digest, name
    assert sha(native / "preflight.json") == summary["preflight_sha256"]
    assert sha(native / "run_xy.py") == summary["primary_runner_sha256"]
    pins = {**pre["inputs"], **pre["source_files"]}
    for name, digest in pins.items():
        assert sha(root / name) == digest, name
    for filename, runner in [("measurement-scope-preflight.json", "run_measurement_scope.py"),
                             ("pair-control-preflight.json", "run_pair_control.py"),
                             ("probe-preflight.json", "probe_contracts.py")]:
        assert read(native / filename)["runner_sha256"] == sha(native / runner)

    sys.path[:0] = [str(root / "src"), str(root)]
    from PIL import Image
    from oil_tracker.domain.detection import PhaseDetection, BoundaryCandidate
    from oil_tracker.domain.enums import BoundaryKind, FillState
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.adapters.vision.observation_sequence_resolver import ObservationSequenceResolver

    inventory = {}
    html_links = 0
    for path in sorted(native.rglob("*")):
        if not path.is_file():
            continue
        assert not path.is_symlink(), path
        inventory[str(path.relative_to(native))] = {"bytes": path.stat().st_size, "sha256": sha(path)}
        if path.suffix in (".json", ".oilrecipe"):
            value = read(path)
            if path.suffix == ".oilrecipe":
                InspectionRecipe.from_dict(value)
        elif path.suffix in (".png", ".jpg"):
            with Image.open(path) as im:
                im.verify()
        elif path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
        elif path.suffix == ".csv":
            list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
        elif path.suffix == ".html":
            links = Links()
            links.feed(path.read_text())
            for ref in links.refs:
                url = urlsplit(ref)
                if url.scheme or not url.path:
                    continue
                target = (path.parent / unquote(url.path)).resolve()
                assert target.is_relative_to(native.resolve()) and target.exists(), ref
                html_links += 1
        elif path.suffix == ".log":
            path.read_text()
        else:
            raise AssertionError(path)

    def decode(item):
        d = deepcopy(item)
        d["fill_state"] = FillState(d["fill_state"])
        d["candidates"] = [BoundaryCandidate(**dict(c, kind=BoundaryKind(c["kind"]))) for c in d["candidates"]]
        return PhaseDetection(**d)

    def fingerprint(rows):
        keys = {"raw_oil_y": "raw_oil_air_level_y", "raw_oil_px": "raw_oil_air_level_px_from_zero",
                "smoothed_oil_px": "smoothed_oil_air_level_px_from_zero", "raw_foam_y": "raw_foam_front_y",
                "smoothed_foam_px": "smoothed_foam_front_px_from_zero"}
        payload = [{**{k: r[k] for k in ("glass_id", "frame_index", "timestamp_sec", "fill_state", "is_valid", "flags")},
                    **{k: r[v] for k, v in keys.items()}} for r in rows]
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

    base_rows = read(native / "sample4-baseline/tracking.json")
    base_raw = read(native / "sample4-baseline/raw.json")
    variants = {v["id"]: v for v in summary["variants"]}
    runs = []
    for directory in sorted(native.iterdir()):
        if not directory.is_dir():
            continue
        raw, expected, rows, recorded = [read(directory / name) for name in ("raw.json", "completed.json", "tracking.json", "summary.json")]
        recipe_path = directory / "recipe.oilrecipe"
        if not recipe_path.exists():
            recipe_path = native / "sample4-baseline/recipe.oilrecipe"
        glass = InspectionRecipe.from_dict(read(recipe_path)).glasses[0]
        result = ObservationSequenceResolver().resolve([decode(d) for d in raw], glass, glass.initial_state)
        actual = json.loads(json.dumps([asdict(d) for d in result.detections]))
        assert actual == expected, directory.name
        assert len(raw) == len(expected) == len(rows) == recorded["results"]
        assert fingerprint(rows) == recorded["fingerprint"]
        for d, r in zip(expected, rows, strict=True):
            assert (d["glass_id"], d["frame_index"], d["time_sec"]) == (r["glass_id"], r["frame_index"], r["timestamp_sec"])
            for key in ("raw_oil_air_level_y", "raw_foam_front_y"):
                assert d[key] == r[key], (directory.name, key)
        if directory.name.startswith("sample4-"):
            v = variants[directory.name.removeprefix("sample4-")]
            assert fingerprint(rows) == v["tracking_fingerprint"]
            assert sum(r["raw_oil_air_level_y"] is not None for r in rows) == v["numeric_oil"]
            assert sum(r["raw_foam_front_y"] is not None for r in rows) == v["numeric_foam"]
            fields = ("raw_oil_air_level_y", "raw_foam_front_y", "oil_is_valid", "foam_is_valid", "fill_state")
            assert sum(any(a[k] != b[k] for k in fields) for a, b in zip(base_rows, rows, strict=True)) == v["public_changed_rows"]
            assert sum(a["raw_oil_air_level_y"] != b["raw_oil_air_level_y"] for a, b in zip(base_rows, rows, strict=True)) == v["oil_coordinate_changed_rows"]
            assert all((a["raw_foam_front_y"], a["foam_is_valid"]) == (b["raw_foam_front_y"], b["foam_is_valid"]) for a, b in zip(base_rows, rows, strict=True)) == v["completed_foam_coordinate_and_validity_exact_equal"]
            assert sum(a["raw_foam_front_y"] == b["raw_foam_front_y"] and all(b["debug_metrics"][k] == value for k, value in a["debug_metrics"].items() if k.startswith("foam_")) for a, b in zip(base_raw, raw, strict=True)) == v["current_foam_metrics_equal_rows"]
            missing, streak = [], []
            for r in rows:
                if r["raw_oil_air_level_y"] is None:
                    streak.append(r)
                elif streak:
                    missing.append(streak)
                    streak = []
            if streak:
                missing.append(streak)
            longest = max(missing, key=len)
            claimed = v["longest_non_numeric_oil_run"]
            assert (len(longest), longest[0]["timestamp_sec"], longest[-1]["timestamp_sec"]) == (claimed["samples"], claimed["first_sample_seconds"], claimed["last_sample_seconds"])
            for point in v["checkpoints"]:
                r = next(r for r in rows if r["frame_index"] == point["frame_index"])
                assert r["raw_oil_air_level_y"] == point["completed_raw_oil_source_y"]
        else:
            v = next(v for v in summary["baseline_runs"] if directory.name == v["sample"] + "-baseline")
            assert fingerprint(rows) == v["fingerprint"]
        runs.append({"run": directory.name, "rows": len(rows), "full_completed_reproduction": True,
                     "tracking_fingerprint": fingerprint(rows)})
        print(directory.name, len(rows), "complete outputs equal", flush=True)

    assert sum(r["rows"] for r in runs) == 751
    contracts = read(native / "contract-results.json")
    assert contracts["checks"] == summary["contract_checks"] and contracts["check_count"] == 12
    assert all(c["status"] == "PASS" for c in contracts["checks"])
    b40 = next(r for r in read(native / "sample4-oil_measurement_only/tracking.json") if r["frame_index"] == 1200)
    assert b40["oil_is_valid"] is False and b40["foam_is_valid"] is False
    assert all(flag in b40["flags"] for flag in summary["specific_validity_regression"]["observed_flags"])
    for name, meta in inventory.items():
        assert sha(native / name) == meta["sha256"], name
    for name, digest in pins.items():
        assert sha(root / name) == digest, name
    receipt = {"schema": "s11-local-xy-intake-verification-v1", "source_head": pre["source_head"],
               "native_root": str(native.relative_to(root)), "file_count": len(inventory),
               "total_bytes": sum(m["bytes"] for m in inventory.values()),
               "file_types": dict(Counter(Path(p).suffix for p in inventory)),
               "source_pins_verified": len(pre["source_files"]), "input_pins_verified": len(pre["inputs"]),
               "runs": runs, "completed_rows_reproduced": 751, "delivered_statistics_match": True,
               "html_local_links_checked": html_links, "inputs_and_artifacts_unchanged": True,
               "video_decoded": False, "frame_detector_rerun": False,
               "historical_tests_rerun": False, "physical_efficacy_verified": False,
               "verification_script_sha256": sha(Path(__file__)), "native_files": inventory}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    print("PASS", len(inventory), "native files; 751 saved completed rows reproduced", flush=True)


if __name__ == "__main__":
    main()
