#!/usr/bin/env python3
"""Read-only verifier for this handoff's existing local Mac evidence.

Does not run a detector, edit the repository, download data, or infer physical
accuracy. Missing ignored artifacts and a changed HEAD are reported explicitly.
Requires Python 3.11+ and only the standard library.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes repository: {relative}")
    return path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify(root: Path, summary: dict[str, Any], *, check_inputs: bool = True) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository directory does not exist: {root}")
    execution = inside(root, summary['execution_root_relative'])
    matched: list[str] = []
    missing: list[str] = []
    mismatched: list[str] = []

    def one(relative: str, expected: str) -> bool:
        if not re.fullmatch(r'[a-f0-9]{64}', expected):
            raise ValueError(f"Invalid SHA-256 in manifest: {relative}")
        path = inside(root, relative)
        if not path.is_file():
            missing.append(relative)
            return False
        if digest(path) != expected:
            mismatched.append(relative)
            return False
        matched.append(relative)
        return True

    preflight_ok = False
    for name, metadata in summary['local_artifacts'].items():
        relative = str((execution / name).relative_to(root))
        ok = one(relative, metadata['sha256'])
        if name == 'partition-trial/preflight.json':
            preflight_ok = ok
    inputs_checked = 0
    if check_inputs and preflight_ok:
        preflight = json.loads((execution / 'partition-trial/preflight.json').read_text(encoding='utf-8'))
        for relative, expected in preflight['inputs'].items():
            one(relative, expected)
            inputs_checked += 1
    try:
        head = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True, timeout=15).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        head = None
    base_matches = head == summary['base_head']
    state = ('MISMATCH' if mismatched else
             'INCOMPLETE_OR_DIFFERENT_HEAD' if missing or not base_matches else
             'RECORDED_LOCAL_EVIDENCE_MATCHES')
    return {'state': state, 'expected_head': summary['base_head'], 'actual_head': head,
            'base_matches': base_matches, 'matching_paths': len(matched),
            'input_pins_checked': inputs_checked, 'missing_paths': missing,
            'mismatched_paths': mismatched,
            'physical_detector_accuracy': 'NOT_EVALUATED',
            'note': 'Hash equality validates recorded evidence identity, not S11/O2/field acceptance.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--summary', type=Path,
                        default=Path(__file__).with_name('S11-execution-summary-cc17924-2026-10-09.json'))
    parser.add_argument('--skip-input-pins', action='store_true',
                        help='Verify only the listed output/runner hashes, not preflight input files.')
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding='utf-8'))
        result = verify(args.repo_root, summary, check_inputs=not args.skip_input_pins)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f'Verification could not complete: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['state'] == 'RECORDED_LOCAL_EVIDENCE_MATCHES' else 1 if result['state'] == 'MISMATCH' else 2


if __name__ == '__main__':
    raise SystemExit(main())
