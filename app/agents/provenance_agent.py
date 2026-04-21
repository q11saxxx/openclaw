# app/agents/provenance_agent.py

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
        logger.info(f"[{self.name}] 正在执行深度供应链、依赖与溯源审计...")
        
        if not isinstance(context.provenance, dict):
            context.provenance = {}

        # 1. 运行核心分析器
        dependency_result = self._safe_run_dependency(context)
        diff_result = self._safe_run_diff(context)
        identity_findings = self._audit_identity(context)

        # 2. 收集原始风险项 (Raw Findings)
        raw_findings = []
        raw_findings.extend(identity_findings)
        raw_findings.extend(dependency_result.get("findings", []))
        raw_findings.extend(diff_result.get("findings", []))

        # --- 🔥 关键增强：提取新版 DependencyAnalyzer 的深度风险 ---
        
        # A. 处理可疑项 (Suspicious Items: 包括 Typosquatting 和 恶意源)
        for item in dependency_result.get("suspicious", []):
            raw_findings.append({
                "type": item.get("type"),
                "level": item.get("level"),
                "message": f"供应链威胁: {item.get('item') or item.get('package')} - {item.get('reason')}",
                "evidence": item
            })

        # B. 处理代码中的第三方库引用风险 (Code Reference Risks)
        for ref in dependency_result.get("code_references", []):
            sec_check = ref.get("security_check", {})
            if not sec_check.get("safe", True):
                for issue in sec_check.get("issues", []):
                    raw_findings.append({
                        "type": issue.get("type"),
                        "level": issue.get("level"),
                        "message": f"代码库引用风险: 模块 '{ref.get('module')}' 存在威胁 - {issue.get('reason')}",
                        "evidence": ref
                    })

        # 3. 统一标准化映射 (Standardization)
        # 确保每个项都包含 agent, type, risk_level, reason, evidence
        for f in raw_findings:
            standard_f = {
                "agent": self.name,
                "type": f.get("type", "provenance_risk"),
                "risk_level": str(f.get("level") or f.get("risk_level") or "low").lower(),
                "reason": f.get("reason") or f.get("message") or "检测到来源或依赖风险",
                "evidence": f.get("evidence") or f
            }
            context.add_finding(standard_f)

        # 4. 更新 Context 的溯源事实摘要 (用于 Report 展示)
        sum_data = dependency_result.get("summary", {})
        context.provenance.update({
            "dependencies": dependency_result.get("dependencies", []),
            "external_urls": dependency_result.get("external_urls", []),
            "code_references": dependency_result.get("code_references", []),
            "diff_summary": diff_result.get("findings", []),
            "stats": sum_data,
            # 计算一个简单的信任分数
            "trust_score": 1.0 - (sum_data.get("high_risk_items", 0) * 0.3),
            "summary": self._build_summary(raw_findings, sum_data)
        })

    def _audit_identity(self, context: AuditContext) -> list:
        """审计作者身份和许可证"""
        findings = []
        manifest = context.parsed.get("manifest", {})
        author = manifest.get("author")
        if not author or author.lower() in ["unknown", "none", ""]:
            findings.append({
                "type": "anonymous_publication",
                "level": "medium",
                "message": "该 Skill 未声明有效作者身份，存在匿名投毒和不可追溯风险。"
            })
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
            return {"findings": [{"level": "medium", "type": "dep_err", "message": str(exc)}]}

    def _safe_run_diff(self, context: AuditContext) -> dict:
        try:
            prev = getattr(context, "previous_skill_path", None)
            return self.update_diff_analyzer.analyze(context.skill_path, prev)
        except Exception as exc:
            return {"findings": [{"level": "medium", "type": "diff_err", "message": str(exc)}]}

    def _build_summary(self, findings: list, stats: dict) -> str:
        if not findings and not stats.get("total_dependencies"):
            return "未发现明显来源、依赖或版本漂移风险。"
        return (f"识别到 {stats.get('total_dependencies', 0)} 个依赖项和 "
                f"{stats.get('unique_urls', 0)} 个外部 URL。共发现 {len(findings)} 项风险。")