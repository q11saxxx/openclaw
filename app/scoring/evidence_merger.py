"""证据融合器。

规则描述：
- 负责把静态、语义、来源分析结果合并为统一结构。
- 合并时应保留来源字段，避免丢失可解释性。
"""
class EvidenceMerger:
    def merge(self, findings: list[dict], provenance: dict) -> dict:
        return {"findings": findings, "provenance": provenance}
