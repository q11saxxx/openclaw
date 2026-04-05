"""多智能体总调度器。

规则描述：
- 负责协调一次完整审计任务的执行生命周期。
- 统一调用 pipeline，不直接耦合各 analyzer。
"""
from app.core.pipeline import AuditPipeline

class Orchestrator:
    def __init__(self) -> None:
        self.pipeline = AuditPipeline()

    def run(self, skill_path: str, options: dict = None) -> dict:
        return self.pipeline.run(skill_path, previous_skill_path=None, options=options)
