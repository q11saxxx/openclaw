from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.scoring.evidence_merger import EvidenceMerger
from app.scoring.risk_model import RiskModel
from app.scoring.confidence_calculator import ConfidenceCalculator

class DecisionAgent(BaseAgent):
    """风险融合决策代理。

    规则描述：
    - 负责汇总多源证据并输出最终风险等级与处置建议。
    - 决策逻辑应可解释，必须保留证据来源。
    """
    name = "decision"

    def __init__(self) -> None:
        self.merger = EvidenceMerger()
        self.model = RiskModel()
        self.confidence = ConfidenceCalculator()

    def run(self, context: AuditContext) -> None:
        merged = self.merger.merge(context.findings, context.provenance)
        decision = self.model.score(merged)
        decision["confidence"] = self.confidence.calculate(merged)
        context.decision = decision
