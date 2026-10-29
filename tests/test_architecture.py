"""The dependency rule in docs/20-architecture/architecture.md."""

import ast
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "oil_tracker"


def module_name(path: Path) -> str:
    parts = list(path.relative_to(PACKAGE.parent).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imports_of(path: Path) -> set[str]:
    name = module_name(path)
    package = name if path.name == "__init__.py" else name.rpartition(".")[0]
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")
                base = base[: len(base) - node.level + 1]
                found.add(".".join(base + ([node.module] if node.module else [])))
            else:
                found.add(node.module)
    return found


def violations(layer: str, allowed) -> list[str]:
    root = PACKAGE.joinpath(*layer.split("/"))
    if not root.exists():
        return []
    bad = []
    for path in sorted(root.rglob("*.py")):
        for imported in imports_of(path):
            if not allowed(path, imported):
                bad.append(f"{module_name(path)} imports {imported}")
    return bad


def is_stdlib(imported: str) -> bool:
    return imported.split(".")[0] in sys.stdlib_module_names or imported == "__future__"


def within(imported: str, *packages: str) -> bool:
    return any(imported == p or imported.startswith(p + ".") for p in packages)


def test_domain_imports_only_the_standard_library_and_itself():
    assert violations("domain", lambda _, i: is_stdlib(i) or within(i, "oil_tracker.domain")) == []


def test_application_imports_only_the_standard_library_domain_and_itself():
    def allowed(_, imported):
        return is_stdlib(imported) or within(imported, "oil_tracker.domain", "oil_tracker.application")

    assert violations("application", allowed) == []


def test_adapters_do_not_import_each_other_or_the_wiring():
    def allowed(path, imported):
        own = "oil_tracker.adapters." + path.relative_to(PACKAGE / "adapters").parts[0].removesuffix(".py")
        if within(imported, "oil_tracker.adapters"):
            return within(imported, own) or imported == "oil_tracker.adapters"
        if within(imported, "oil_tracker"):
            return within(imported, "oil_tracker.domain", "oil_tracker.application")
        return True

    assert violations("adapters", allowed) == []
