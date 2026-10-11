"""Verify the bytes of this handoff package; does not apply or execute its patch."""
from pathlib import Path
import hashlib
import sys

def main() -> int:
    root = Path(__file__).resolve().parent
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        print("Missing SHA256SUMS.txt", file=sys.stderr)
        return 2
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            print(f"Missing or invalid path: {relative}", file=sys.stderr)
            return 1
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            print(f"Hash mismatch: {relative}", file=sys.stderr)
            return 1
        checked += 1
    print(f"PASS: {checked} packaged files match SHA-256. No code was applied.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
