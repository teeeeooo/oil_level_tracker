"""Round-2 saved-report checks; not a detector, classifier or acceptance evaluator."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def confidence_obstruction(positive, opposition):
    """A necessary obstruction for accept iff confidence >= cutoff; no cutoff search."""
    for row in (*positive, *opposition):
        value = row["confidence"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("finite numeric confidence required")
    return [
        {"positive": p, "opposition": n}
        for p in positive for n in opposition
        if n["confidence"] >= p["confidence"]
    ]


def authority_collisions(units):
    """Only exact recorded authority tuples are tested; unknowns remain unknown."""
    seen, groups = set(), defaultdict(list)
    for unit in units:
        identity = unit["query"]["id"]
        if identity in seen:
            raise ValueError("duplicate candidate identity")
        seen.add(identity)
        if not unit.get("candidate_role_comparison_ready"):
            continue
        role = unit["physical_claim"]
        if role not in {"TARGET_CORRESPONDENCE", "OPPOSED_OIL_TARGET"}:
            raise ValueError("unsupported qualified role")
        authority = unit["authority"]
        signature = (authority["authority"], authority["reason"],
                     tuple(sorted(authority["failed_gates"])))
        groups[signature].append({"id": identity, "role": role})
    return [
        {"signature": [a, r, list(g)], "subjects": subjects}
        for (a, r, g), subjects in sorted(groups.items())
        if {s["role"] for s in subjects} == {"TARGET_CORRESPONDENCE", "OPPOSED_OIL_TARGET"}
    ]


class ReportHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references, self.sequences = [], []
        self._buffer = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("src", "href"):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == "script" and "sequence-data" in attrs.get("class", "").split():
            self._buffer = []

    def handle_data(self, data):
        if self._buffer is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._buffer is not None:
            self.sequences.append(json.loads("".join(self._buffer)))
            self._buffer = None


def local_asset(directory: Path, relative: str) -> Path:
    parsed = urlsplit(relative)
    if parsed.scheme or parsed.netloc:
        raise ValueError("external report dependency")
    path = (directory / unquote(parsed.path)).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError("report asset escapes bundle")
    if not path.is_file():
        raise ValueError(f"missing report asset: {relative}")
    return path


def inspect_sequences(report: Path):
    parsed = ReportHTML()
    parsed.feed(report.read_text(encoding="utf-8"))
    assets = {local_asset(report.parent, r) for r in parsed.references if urlsplit(r).path}
    summaries, all_frames, crop_fingerprints = [], [], {}
    overlap_count = 0
    for sequence in parsed.sequences:
        metadata = local_asset(report.parent, sequence["metadata_path"])
        if read_json(metadata) != sequence:
            raise ValueError("embedded/sidecar sequence mismatch")
        assets.add(metadata)
        if sequence["numeric_measurement"] is not False:
            raise ValueError("source context mislabeled as numeric measurement")
        geometry = sequence["geometry"]
        x, y, width, height = geometry["tile_content_xywh"]
        tile_size = sequence["tile_size"]
        if min(x, y, width, height) < 0 or min(width, height) == 0 or x + width > tile_size or y + height > tile_size:
            raise ValueError("invalid tile content bounds")
        if geometry["resize_scale"] != 1 or geometry["resize_method"] != "none":
            raise ValueError("this original-pixel audit requires unresized crops")
        if sequence["frame_count"] != len(sequence["frames"]):
            raise ValueError("sequence denominator mismatch")
        seen, frames, images = set(), [], {}
        try:
            for frame in sequence["frames"]:
                if frame["status"] != "AVAILABLE":
                    continue
                index = frame["frame_index"]
                if index in seen:
                    raise ValueError("duplicate available frame in sequence")
                seen.add(index)
                page = local_asset(report.parent, frame["page_path"])
                assets.add(page)
                if page not in images:
                    images[page] = Image.open(page).convert("RGB")
                image = images[page]
                tx, ty = frame["tile_xy"]
                if min(tx, ty) < 0 or tx + tile_size > image.width or ty + tile_size > image.height:
                    raise ValueError("sprite tile outside image")
                pixels = image.crop((tx + x, ty + y, tx + x + width, ty + y + height))
                digest = hashlib.sha256(pixels.tobytes()).hexdigest()
                key = (sequence["glass_id"], index, tuple(geometry["crop_source_xyxy"]))
                if key in crop_fingerprints:
                    overlap_count += 1
                    if crop_fingerprints[key] != digest:
                        raise ValueError("same source frame has different original pixels")
                crop_fingerprints[key] = digest
                frames.append({"frame_index": index, "actual_time_sec": frame["actual_time_sec"],
                               "crop_sha256": digest})
            if sequence["available_count"] != len(frames):
                raise ValueError("available count mismatch")
            indices = [f["frame_index"] for f in frames]
            if indices != sorted(indices):
                raise ValueError("source frame order is not increasing")
            native = bool(indices) and all(b == a + 1 for a, b in zip(indices, indices[1:]))
            summaries.append({"metadata_path": sequence["metadata_path"], "start_sec": sequence["start_sec"],
                              "end_sec": sequence["end_sec"], "reasons": sequence["reasons"],
                              "records": len(sequence["frames"]), "available": len(frames),
                              "consecutive_source_frames": native, "subsampled": sequence["subsampled"],
                              "frames": frames})
            all_frames.extend(frames)
        finally:
            for image in images.values():
                image.close()
    return {"asset_sha256": {str(p.relative_to(report.parent)): sha256(p) for p in sorted(assets)},
            "sequences": summaries, "records": len(all_frames),
            "unique_source_frames": len(crop_fingerprints), "overlap_pixel_checks": overlap_count}


def audit(root: Path, report: Path):
    root, report = root.resolve(), report.resolve()
    source_reuse = root / "docs/50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json"
    default_path = root / "docs/50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json"
    roster_path = root / "docs/50-diagnostics/s11/2026-10-12-scene-evaluation-roster.json"
    reuse, default, roster = map(read_json, (source_reuse, default_path, roster_path))
    review_pin = roster["source_pins"]["oil_output_review"]
    motion_pin = roster["source_pins"]["oil_motion"]
    for pin in (review_pin, motion_pin):
        if sha256(root / pin["path"]) != pin["sha256"]:
            raise ValueError("qualified reply pin mismatch")
    review = read_json(root / review_pin["path"])
    motion = read_json(root / motion_pin["path"])
    bundle = ResultBundleReader().read(report.parent)
    if len(bundle.glasses) != 1:
        raise ValueError("this bounded audit expects the retained single-Glass report")
    samples = {s.frame_index: s for s in bundle.samples}
    if len(samples) != len(bundle.samples):
        raise ValueError("duplicate completed frame")
    positives, oppositions, bindings = [], [], []
    roles = {(u["query"]["frame"], u["query"]["source_xy"][1]): u["physical_claim"]
             for u in reuse["oil_units"] if u["candidate_role_comparison_ready"]}
    for item in review["frames"]:
        saved, sample = item["stored_row"], samples[item["frame"]]
        fields = {"t": sample.timestamp_sec, "oil_y": sample.raw_oil_air_level_y,
                  "oil_h": sample.raw_oil_air_level_px_from_zero, "foam_y": sample.raw_foam_front_y,
                  "foam_h": sample.raw_foam_front_px_from_zero, "oil_valid": sample.oil_is_valid,
                  "foam_valid": sample.foam_is_valid, "state": sample.fill_state.value}
        if any(saved[k] != v for k, v in fields.items()) or set(saved["flags"]) != set(sample.flags):
            raise ValueError("reviewed output / retained bundle mismatch")
        role = roles.get((sample.frame_index, sample.raw_oil_air_level_y), "NOT_QUALIFIED_BY_CURRENT_ROLES")
        evidence = {"frame_index": sample.frame_index, "time_sec": sample.timestamp_sec,
                    "y": sample.raw_oil_air_level_y, "confidence": sample.oil_air_confidence,
                    "oil_is_valid": sample.oil_is_valid, "current_candidate_role": role}
        bindings.append(evidence)
        if role == "TARGET_CORRESPONDENCE":
            positives.append(evidence)
        elif role == "OPPOSED_OIL_TARGET":
            oppositions.append(evidence)
    numeric = [s for s in samples.values() if s.raw_oil_air_level_px_from_zero is not None]
    extremes = []
    for name, chosen in (("MINIMUM_OIL_LEVEL", min(numeric, key=lambda s: s.raw_oil_air_level_px_from_zero)),
                         ("MAXIMUM_OIL_LEVEL", max(numeric, key=lambda s: s.raw_oil_air_level_px_from_zero))):
        event = [e for e in bundle.events if e.event_type.value == name]
        if len(event) != 1 or event[0].representative_frame_index != chosen.frame_index or event[0].oil_level_px != chosen.raw_oil_air_level_px_from_zero:
            raise ValueError("event/sample extrema mismatch")
        extremes.append({"event": name, "frame_index": chosen.frame_index, "time_sec": chosen.timestamp_sec,
                         "y": chosen.raw_oil_air_level_y, "level_px": chosen.raw_oil_air_level_px_from_zero,
                         "reviewed_opposition": any(o["frame_index"] == chosen.frame_index for o in oppositions)})
    sequences = inspect_sequences(report)
    first, last = motion["appearance_correspondence_review"]["binding"]["displayed_frames"]
    covering = [s["metadata_path"] for s in sequences["sequences"]
                if set(range(first, last + 1)) <= {f["frame_index"] for f in s["frames"]}]
    production = {p: sha256(root / p) == h for p, h in default["inputs"].items() if p.startswith("src/")}
    return {"schema": "s11-round2-report-context-audit-v1", "production_changed_by_audit": False,
            "files": {str(p.relative_to(root)): sha256(p) for p in
                      (report, source_reuse, default_path, roster_path, root / review_pin["path"], root / motion_pin["path"], *bundle.files.values()) if p is not None},
            "producing_source_matches": sum(production.values()), "producing_source_files": len(production),
            "producing_source_mismatches": [p for p, equal in production.items() if not equal],
            "completed_counts": {"rows": len(samples), "numeric_oil": len(numeric),
                "numeric_foam": sum(s.raw_foam_front_y is not None for s in samples.values()), "events": len(bundle.events)},
            "reviewed_output_bindings": bindings, "extrema": extremes,
            "confidence_only_obstructions": confidence_obstruction(positives, oppositions),
            "authority_tuple_collisions": authority_collisions(reuse["oil_units"]),
            "all_candidate_role_counts": dict(Counter(u["physical_claim"] for u in reuse["oil_units"])),
            "sequences": sequences, "reviewed_motion_source_availability": {
                "first_frame": first, "last_frame": last, "required_source_frames": last-first+1,
                "complete_sequences": covering, "physical_trajectory_accuracy": "NOT_EVALUATED"},
            "independent_report_reading": "PENDING_ACTUAL_RESPONSE",
            "behavior_candidate": "NONE_ELIGIBLE_FROM_TESTED_EXISTING_SIGNALS",
            "limits": ["No new detector execution or physical labels", "Tuple/monotone contradictions do not rule out richer observations",
                       "Available source pixels do not establish human comprehension", "No target-Windows execution or acceptance"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output already exists")
    result = audit(args.repo, args.report)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("completed_counts", "behavior_candidate", "independent_report_reading")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
