from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.services.report_service import ReportService

class ReportAgent(BaseAgent):
    """报告生成代理。

    规则描述：
    - 将上下文转换成用户可读、机器可读的报告。
    - 输出格式必须稳定，便于前端展示和后续导出。
    """
    name = "report"

    def __init__(self) -> None:
        self.report_service = ReportService()

    def run(self, context: AuditContext) -> None:
        context.report = self.report_service.build_report(context.to_dict())
