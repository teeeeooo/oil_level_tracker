"""Verify this delivery's hashes and internal accounting, not detector accuracy."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_PEER_SHA = "0376cf9044715f21c3389e89bf2528964edcf5821cd87d649a8d3ede055dfb6e"
EXPECTED_HEAD = "2c2ddd20b3dfe0eddcbc8d747b01e766522536a1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(root: Path) -> dict:
    root = root.resolve(strict=True)
    manifest = root / "SHA256SUMS.txt"
    seen: set[str] = set()
    for row in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = row.split("  ", 1)
        path = (root / relative).resolve(strict=True)
        require(root in path.parents, "Manifest path escapes delivery root")
        require(relative not in seen, f"Duplicate checksum entry: {relative}")
        require(path.is_file(), f"Not a file: {relative}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                f"Checksum mismatch: {relative}")
        seen.add(relative)
    required = {
        "S11-program-review-and-work-spec-2026-10-12.md", "README.md",
        "story-contract.json", "scripts/peer_probe.py", "scripts/check_delivery.py",
        "scripts/test_story_contract.py", "evidence/execution-receipt.json",
        "evidence/focused-tests.log", "evidence/story-contract-tests.log"
    }
    require(required <= seen, f"Required files missing from manifest: {required - seen}")
    receipt = json.loads((root / "evidence/execution-receipt.json").read_text(encoding="utf-8"))
    contract = json.loads((root / "story-contract.json").read_text(encoding="utf-8"))
    require(receipt["baseline_head"] == EXPECTED_HEAD, "Receipt baseline changed")
    require(contract["baseline_head"] == EXPECTED_HEAD, "Contract baseline changed")
    peer_sha = hashlib.sha256((root / "scripts/peer_probe.py").read_bytes()).hexdigest()
    require(peer_sha == receipt["script_sha256"] == EXPECTED_PEER_SHA,
            "Delivered probe is not byte-identical to the executed probe")
    sources = receipt["sources"]
    total = receipt["totals"]
    require(sum(x["frames"] for x in sources.values()) == total["frames"] == 116,
            "Frame accounting mismatch")
    require(sum(x["oil_candidate_joins"] for x in sources.values()) ==
            total["oil_candidate_joins"] == 2618, "Candidate accounting mismatch")
    require(sum(x["stored_support_values_reproduced"] for x in sources.values()) ==
            total["stored_support_values_reproduced"] == 1892,
            "Support accounting mismatch")
    require(total["oil_candidate_joins"] - total["stored_support_values_reproduced"] ==
            total["candidates_without_stored_support_field"] == 726,
            "Absent support fields incorrectly counted")
    require(all(x["support_mismatches"] == 0 for x in sources.values()),
            "Unexpected support mismatch")
    require(receipt["fresh_tests"]["passed"] == 124 and receipt["fresh_tests"]["failed"] == 0,
            "Fresh repository test count changed")
    require(receipt["physical_acceptance"] == "NOT_EVALUATED", "Physical claim changed")
    require(receipt["production_unchanged"] is True, "Production mutation claimed")
    require(contract["status"] == "PROPOSAL_NOT_ADOPTED", "Contract promoted")
    require(contract["model_challenger"]["status"] == "PROPOSED_NOT_EXECUTED",
            "Untested model promoted")
    scenes = contract["windows_scenes"]
    require(len(scenes) == len({x["scene_id"] for x in scenes}) == 9,
            "Windows scope has missing or duplicate scenes")
    require(all(x["current_run_status"] == "NOT_EVALUATED" and
                x["report_disposition"] == "U" for x in scenes),
            "Unexecuted Windows result promoted")
    return {
        "status": "DELIVERY_INTEGRITY_PASS",
        "hashed_payload_files": len(seen),
        "executed_peer_script_byte_identical": True,
        "repo_tests_passed": 124,
        "physical_acceptance": "NOT_EVALUATED",
        "limits": "Hashes and internal accounting only; not a fresh repo replay or field/report acceptance."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"DELIVERY_INTEGRITY_FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
