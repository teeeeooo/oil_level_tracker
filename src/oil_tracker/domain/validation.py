from __future__ import annotations

from dataclasses import dataclass

from .enums import ValidationSeverity


@dataclass(frozen=True)
class ValidationIssue:
    severity: ValidationSeverity
    code: str
    message: str
    glass_id: str | None = None
    field: str | None = None


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [x for x in self.issues if x.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [x for x in self.issues if x.severity == ValidationSeverity.WARNING]

    @property
    def is_structurally_valid(self) -> bool:
        return not any(x.severity == ValidationSeverity.ERROR and x.code.startswith("STRUCT_") for x in self.issues)

    @property
    def is_ready(self) -> bool:
        return not self.errors
