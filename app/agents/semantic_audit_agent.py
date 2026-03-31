from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.prompt_injection_detector import PromptInjectionDetector
from app.services.llm_service import LLMService

class SemanticAuditAgent(BaseAgent):
    """语义审计代理。

    规则描述：
    - 负责提示注入、越权诱导、社会工程类语义风险识别。
    - LLM 结果必须保留理由与证据摘要，不能只返回结论。
    """
    name = "semantic_audit"

    def __init__(self) -> None:
        self.detector = PromptInjectionDetector()
        self.llm = LLMService()

    def run(self, context: AuditContext) -> None:
        context.add_finding(self.detector.detect(context.skill_path))
        context.add_finding(self.llm.semantic_review(context.skill_path))
