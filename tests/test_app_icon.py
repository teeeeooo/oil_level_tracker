import importlib.util
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("make_icon", ROOT / "scripts" / "make_icon.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)

PNG = b"\x89PNG\r\n\x1a\n"


def entries(data: bytes) -> dict[int, bytes]:
    reserved, kind, count = struct.unpack_from("<HHH", data)
    assert (reserved, kind) == (0, 1)
    found = {}
    for index in range(count):
        side, _, _, _, _, _, length, offset = struct.unpack_from("<BBBBHHII", data, 6 + 16 * index)
        found[side or 256] = data[offset:offset + length]
    return found


def test_the_icon_file_holds_every_size_as_png():
    images = entries(script.OUT.read_bytes())
    assert sorted(images) == sorted(script.SIZES)
    for size, png in images.items():
        assert png.startswith(PNG)
        assert struct.unpack(">II", png[16:24]) == (size, size)


def test_an_icon_of_pngs():
    fake = {16: PNG + b"a", 256: PNG + b"bb"}
    assert entries(script.ico(fake)) == fake
