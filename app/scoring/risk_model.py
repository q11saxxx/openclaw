"""风险评分模型。

规则描述：
- 输入为融合后的证据集合，输出风险等级与处置建议。
- 正式阶段应把权重、阈值与解释逻辑拆分配置化。
- 综合考虑证据数量和严重性等级来评估供应链风险
"""
class RiskModel:
    """风险评估模型。
    
    供应链安全风险评分逻辑（从严重导轻）：
    
    HIGH RISK (manual_review_or_block):
    - 存在任何 CRITICAL 级别的 finding
    - 存在 2+ 个 HIGH 级别的 finding
    - 存在 HIGH + MEDIUM 组合且总数 >= 2
    
    MEDIUM RISK (manual_review):
    - 存在 1+ 个 HIGH 级别的 finding（无 critical）
    - 存在 2+ 个 MEDIUM 级别的 finding
    - 存在 MEDIUM + LOW 组合且总数 >= 3
    
    LOW RISK (allow):
    - 最多 1 个 MEDIUM 级别的 finding
    - 仅 LOW 级别的 finding
    - 无 finding
    """
    
    def score(self, merged: dict) -> dict:
        findings = merged.get("findings", [])
        
        if not findings:
            return {
                "level": "low",
                "recommendation": "allow"
            }
        
        # 计算严重性统计
        severity_count = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for finding in findings:
            severity = finding.get("severity", "medium").lower()
            if severity in severity_count:
                severity_count[severity] += 1
        
        # 风险评估逻辑（从严重到轻）
        
        # ===== HIGH RISK 评估 =====
        # 任何 CRITICAL finding
        if severity_count["critical"] > 0:
            return {
                "level": "high",
                "recommendation": "manual_review_or_block"
            }
        
        # 2+ 个 HIGH
        if severity_count["high"] >= 2:
            return {
                "level": "high",
                "recommendation": "manual_review_or_block"
            }
        
        # HIGH + MEDIUM 组合（1+ high 且 1+ medium）
        if severity_count["high"] >= 1 and severity_count["medium"] >= 1:
            return {
                "level": "high",
                "recommendation": "manual_review_or_block"
            }
        
        # ===== MEDIUM RISK 评估 =====
        # 单个 HIGH（无 critical，无其他 high）
        if severity_count["high"] >= 1:
            return {
                "level": "medium",
                "recommendation": "manual_review"
            }
        
        # 2+ 个 MEDIUM
        if severity_count["medium"] >= 2:
            return {
                "level": "medium",
                "recommendation": "manual_review"
            }
        
        # MEDIUM 元素存在（至少 1 个）
        if severity_count["medium"] >= 1:
            return {
                "level": "medium",
                "recommendation": "manual_review"
            }
        
        # ===== LOW RISK 评估 =====
        # 仅 LOW 或无 finding
        return {
            "level": "low",
            "recommendation": "allow"
        }
