"""审计主流程编排。

规则描述：
- 所有 agent 调用顺序必须在这里统一控制。
- 新增 agent 时，应先定义输入输出契约，再接入流程。
- 推荐流程：解析 -> 静态扫描 -> 语义审计 -> 来源分析 -> 决策 -> 报告。
"""
from app.core.context import AuditContext
from app.agents.parser_agent import ParserAgent
from app.agents.static_security_agent import StaticSecurityAgent
from app.agents.semantic_audit_agent import SemanticAuditAgent
from app.agents.provenance_agent import ProvenanceAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.report_agent import ReportAgent
import logging

logger = logging.getLogger(__name__)


class AuditPipeline:
    def __init__(self) -> None:
        self.parser_agent = ParserAgent()
        self.static_agent = StaticSecurityAgent()
        
        # SemanticAuditAgent 初始化可能失败（无 API key），做异常处理
        try:
            self.semantic_agent = SemanticAuditAgent()
        except Exception as e:
            logger.warning(f"SemanticAuditAgent initialization failed: {e}. Will skip semantic audit.")
            self.semantic_agent = None
        
        self.provenance_agent = ProvenanceAgent()
        self.decision_agent = DecisionAgent()
        self.report_agent = ReportAgent()

    def run(self, skill_path: str, previous_skill_path: str = None, options: dict = None) -> dict:
        # 将 options 注入 Context，便于 Agent 根据选项调整行为
        context = AuditContext(
            skill_path=skill_path,
            previous_skill_path=previous_skill_path,
            options=options or {},
        )
        self.parser_agent.run(context)
        self.static_agent.run(context)
        
        # 仅当 semantic_agent 成功初始化时运行
        if self.semantic_agent:
            try:
                self.semantic_agent.run(context)
            except Exception as e:
                logger.error(f"Semantic agent execution failed: {e}")
        
        self.provenance_agent.run(context)
        self.decision_agent.run(context)
        self.report_agent.run(context)
        return context.to_dict()
