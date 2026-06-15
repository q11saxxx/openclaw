from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.scoring.evidence_merger import EvidenceMerger
from app.scoring.risk_model import RiskModel
from app.scoring.confidence_calculator import ConfidenceCalculator
from app.utils.finding_dedupe import dedupe_findings
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

        # 0. 去重：相同定位与类型的重复发现合并，保留更高严重等级（提升信噪比）
        _n0 = len(context.findings)
        context.findings = dedupe_findings(context.findings)
        if len(context.findings) != _n0:
            logger.info("[%s] findings 去重: %s -> %s", self.name, _n0, len(context.findings))

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
