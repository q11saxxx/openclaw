"""风险评分模型。

规则描述：
- 输入为融合后的证据集合，输出风险等级与处置建议。
- 正式阶段应把权重、阈值与解释逻辑拆分配置化。
"""
class RiskModel:
    def score(self, merged: dict) -> dict:
        findings = merged.get("findings", [])
        count = len(findings)
        if count >= 5:
            level = "high"
            recommendation = "manual_review_or_block"
        elif count >= 2:
            level = "medium"
            recommendation = "manual_review"
        else:
            level = "low"
            recommendation = "allow"
        return {"level": level, "recommendation": recommendation}
