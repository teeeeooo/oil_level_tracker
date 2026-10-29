from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

HASH_CHUNK = 1 << 20


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write through a temporary file in the same folder, then replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def sha256_of(path: Path) -> str:
    """Implements application.ports.SourceHasher."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(HASH_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()
