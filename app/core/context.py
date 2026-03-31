from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditContext:
    skill_path: str
    previous_skill_path: str | None = None
    parsed: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)

    def add_finding(self, finding: dict[str, Any]) -> None:
        self.findings.append(finding)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_path": self.skill_path,
            "previous_skill_path": self.previous_skill_path,
            "parsed": self.parsed,
            "findings": self.findings,
            "provenance": self.provenance,
            "decision": self.decision,
            "report": self.report,
        }