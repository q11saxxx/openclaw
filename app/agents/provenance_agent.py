from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.update_diff_analyzer import UpdateDiffAnalyzer


class ProvenanceAgent(BaseAgent):
    """来源与依赖分析代理。

    规则描述：
    - 负责来源可信度、依赖清单、外部引用、版本差异分析。
    - 优先解析 SKILL.md frontmatter 与 _meta.json。
    - 对新增脚本、外部 URL、hook 引用、版本漂移做风险标记。
    - 若无历史版本基线，则只输出当前版本指纹，不做高置信 diff 判断。
    """
    name = "provenance"

    def __init__(self) -> None:
        self.dependency_analyzer = DependencyAnalyzer()
        self.update_diff_analyzer = UpdateDiffAnalyzer()

    def run(self, context: AuditContext) -> None:
        if not isinstance(context.provenance, dict):
            context.provenance = {}

        dependency_result = self._safe_run_dependency(context)
        diff_result = self._safe_run_diff(context)

        findings = []
        findings.extend(dependency_result.get("findings", []))
        findings.extend(diff_result.get("findings", []))

        risk_score = (
            dependency_result.get("risk_score", 0)
            + diff_result.get("risk_score", 0)
        )

        context.provenance["source"] = dependency_result.get("source", {})
        context.provenance["dependencies"] = dependency_result.get("dependencies", {})
        context.provenance["diff"] = diff_result
        context.provenance["findings"] = findings
        context.provenance["risk_score"] = risk_score
        context.provenance["summary"] = self._build_summary(findings, risk_score)

        # 同时把 provenance findings 打到总 findings，方便后续 DecisionAgent 统一处理
        for finding in findings:
            context.add_finding({
                "agent": self.name,
                "category": "provenance",
                **finding,
            })

    def _safe_run_dependency(self, context: AuditContext) -> dict:
        try:
            return self.dependency_analyzer.analyze(context.skill_path)
        except Exception as exc:
            return {
                "source": {},
                "dependencies": {},
                "findings": [
                    {
                        "level": "medium",
                        "type": "dependency_analyzer_failure",
                        "message": f"DependencyAnalyzer 执行失败: {exc}",
                    }
                ],
                "risk_score": 10,
            }

    def _safe_run_diff(self, context: AuditContext) -> dict:
        try:
            previous_path = getattr(context, "previous_skill_path", None)
            return self.update_diff_analyzer.analyze(
                current_path=context.skill_path,
                previous_path=previous_path,
            )
        except Exception as exc:
            return {
                "has_baseline": False,
                "findings": [
                    {
                        "level": "medium",
                        "type": "diff_analyzer_failure",
                        "message": f"UpdateDiffAnalyzer 执行失败: {exc}",
                    }
                ],
                "risk_score": 10,
            }

    def _build_summary(self, findings: list[dict], risk_score: int) -> str:
        if not findings:
            return "未发现明显来源、依赖或版本漂移风险。"

        high_count = sum(1 for f in findings if f.get("level") in {"high", "critical"})
        medium_count = sum(1 for f in findings if f.get("level") == "medium")

        return (
            f"来源分析完成：共发现 {len(findings)} 项相关问题，"
            f"其中高风险 {high_count} 项，中风险 {medium_count} 项，"
            f"来源风险评分为 {risk_score}。"
        )