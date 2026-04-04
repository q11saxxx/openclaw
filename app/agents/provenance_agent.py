from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.update_diff_analyzer import UpdateDiffAnalyzer
import logging

logger = logging.getLogger(__name__)

class ProvenanceAgent(BaseAgent):
    name = "provenance"

    def __init__(self) -> None:
        self.dependency_analyzer = DependencyAnalyzer()
        self.update_diff_analyzer = UpdateDiffAnalyzer()

    def run(self, context: AuditContext) -> None:
        logger.info(f"[{self.name}] 正在执行供应链溯源与依赖审计...")
        
        if not isinstance(context.provenance, dict):
            context.provenance = {}

        # 1. 执行具体分析器
        dependency_result = self._safe_run_dependency(context)
        diff_result = self._safe_run_diff(context)

        # 2. 🔥 新增：身份合规性审计 (Identity Audit)
        identity_findings = self._audit_identity(context)

        # 3. 汇总所有原始 Findings
        raw_findings = []
        raw_findings.extend(dependency_result.get("findings", []))
        raw_findings.extend(diff_result.get("findings", []))
        raw_findings.extend(identity_findings)

        # 4. 🔥 核心修改：将所有 Findings 标准化（映射字段名，防止报告出现 None）
        standardized_findings = []
        for f in raw_findings:
            standard_f = {
                "agent": self.name,
                "type": f.get("type", "provenance_risk"),
                "risk_level": str(f.get("level") or f.get("risk_level") or "low").lower(),
                "reason": f.get("reason") or f.get("message") or "检测到来源或依赖风险",
                "evidence": f.get("evidence") or f
            }
            standardized_findings.append(standard_f)
            # 添加到上下文总列表
            context.add_finding(standard_f)

        # 5. 更新上下文溯源数据
        risk_score = sum(10 for f in standardized_findings if f["risk_level"] in ["high", "critical"])
        context.provenance.update({
            "source": dependency_result.get("source", {}),
            "dependencies": dependency_result.get("dependencies", {}),
            "diff": diff_result,
            "risk_score": risk_score,
            "trust_score": 1.0 - (risk_score / 100.0), # 简单的信任分计算
            "summary": self._build_summary(standardized_findings, risk_score)
        })

    def _audit_identity(self, context: AuditContext) -> list:
        """审计作者身份和许可证 (Identity & Compliance)"""
        findings = []
        manifest = context.parsed.get("manifest", {})
        
        # 检查匿名发布
        author = manifest.get("author")
        if not author or author.lower() in ["unknown", "none", ""]:
            findings.append({
                "type": "anonymous_publication",
                "level": "medium",
                "message": "该 Skill 未声明有效作者身份，存在匿名投毒和不可追溯风险。"
            })
            
        # 检查许可证
        if not manifest.get("license"):
            findings.append({
                "type": "missing_license",
                "level": "low",
                "message": "未检测到开源许可证声明，可能存在合规性隐患。"
            })
            
        return findings

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
