"""证据融合器。

规则描述：
- 负责把静态、语义、来源分析结果合并为统一结构。
- 合并时应保留来源字段，避免丢失可解释性。
"""

class EvidenceMerger:
    def merge(self, findings: list, provenance: dict) -> dict:
        """
        汇总所有发现。
        """
        merged = {
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": [],
            "provenance_summary": provenance or {}
        }

        for f in findings:
            level = f.get("risk_level", "low").lower()
            # 格式化证据
            entry = {
                "source": f.get("agent", "unknown"),
                "type": f.get("type", "unknown"),
                "description": f.get("reason") or f.get("description", ""),
                "evidence": f.get("evidence", "")
            }
            
            if level == "critical": merged["critical_issues"].append(entry)
            elif level == "high": merged["high_issues"].append(entry)
            elif level == "medium": merged["medium_issues"].append(entry)
            else: merged["low_issues"].append(entry)

        return merged
