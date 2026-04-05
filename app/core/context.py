import datetime
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AuditContext:
    skill_path: str
    previous_skill_path: str | None = None
    
    # 记录审计开始时间，用于报告生成
    start_time: datetime.datetime = field(default_factory=datetime.datetime.now)
    # 运行选项，例如是否启用语义审计
    options: dict[str, Any] = field(default_factory=dict)
    
    # 核心数据存储
    parsed: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    
    # 错误追踪（记录哪个 Agent 运行失败了，但不中断流程）
    errors: dict[str, str] = field(default_factory=dict)

    def add_finding(self, finding: dict[str, Any] | list[dict[str, Any]]) -> None:
        """支持添加单个风险项或风险项列表"""
        if isinstance(finding, list):
            self.findings.extend(finding)
        elif isinstance(finding, dict):
            self.findings.append(finding)

    def add_error(self, agent_name: str, error_msg: str) -> None:
        """记录 Agent 运行错误"""
        self.errors[agent_name] = error_msg

    def to_dict(self) -> dict[str, Any]:
        """将 Context 转换为字典，便于 ReportService 处理和 JSON 序列化"""
        data = {
            "skill_path": self.skill_path,
            "previous_skill_path": self.previous_skill_path,
            "options": self.options,
            "start_time": self.start_time.isoformat(),
            "parsed": self.parsed,
            "findings": self.findings,
            "provenance": self.provenance,
            "decision": self.decision,
            "report": self.report,
            "errors": self.errors
        }
        return data
