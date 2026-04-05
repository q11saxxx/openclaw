"""审计任务服务。

规则描述：
- 负责创建并执行审计任务。
- 所有审计流程统一委托给 Orchestrator。
"""
from app.core.orchestrator import Orchestrator

class AuditService:
    def __init__(self) -> None:
        self.orchestrator = Orchestrator()

    def run_audit(self, skill_path: str, options: dict = None) -> dict:
        return self.orchestrator.run(skill_path, options=options)
