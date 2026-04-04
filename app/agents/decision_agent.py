from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.scoring.evidence_merger import EvidenceMerger
from app.scoring.risk_model import RiskModel
from app.scoring.confidence_calculator import ConfidenceCalculator
import logging

logger = logging.getLogger(__name__)

class DecisionAgent(BaseAgent):
    name = "decision"

    def __init__(self) -> None:
        self.merger = EvidenceMerger()
        self.model = RiskModel()
        self.confidence_calc = ConfidenceCalculator()

    def run(self, context: AuditContext) -> None:
        logger.info(f"[{self.name}] 正在进行最终风险决策汇总...")

        # 1. 融合所有 Findings 和 溯源信息
        # 注意：context.provenance 需要在 ProvenanceAgent 中赋值
        provenance_data = getattr(context, "provenance", {})
        merged = self.merger.merge(context.findings, provenance_data)

        # 2. 执行评分模型
        decision_base = self.model.score(merged)

        # 3. 计算置信度
        conf = self.confidence_calc.calculate(merged)

        # 4. 构造最终决策结果
        final_decision = {
            "risk_level": decision_base["final_risk_level"],
            "suggestion": decision_base["disposal_suggestion"],
            "confidence": conf,
            "summary": decision_base["reason"],
            "details": {
                "critical_count": len(merged["critical_issues"]),
                "high_count": len(merged["high_issues"]),
                "medium_count": len(merged["medium_issues"]),
                "low_count": len(merged["low_issues"]),
            }
        }

        # 5. 回写 Context
        # 在 Context 中增加一个 decision 属性
        context.decision = final_decision
        logger.info(f"[{self.name}] 决策完成: {final_decision['risk_level']} -> {final_decision['suggestion']}")
