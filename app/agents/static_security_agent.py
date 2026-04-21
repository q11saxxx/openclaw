import logging
from typing import Any, List, Dict
from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.script_analyzer import ScriptAnalyzer
from app.analyzers.file_permission_analyzer import FilePermissionAnalyzer
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.update_diff_analyzer import UpdateDiffAnalyzer
from app.rules.rule_engine import RuleEngine

logger = logging.getLogger(__name__)

class StaticSecurityAgent(BaseAgent):
    name = "static_security"

    def __init__(self) -> None:
        self.script_analyzer = ScriptAnalyzer()
        self.permission_analyzer = FilePermissionAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.update_diff_analyzer = UpdateDiffAnalyzer()
        self.rule_engine = RuleEngine()
        logger.debug(f"Initialized {self.name} agent")

    def run(self, context: AuditContext) -> None:
        logger.info(f"Starting static security analysis for: {context.skill_path}")
        
        try:
            # 1. 执行脚本与权限分析 (这些通常返回单个 Dict)
            for analyzer_name, analyzer_func in [
                ("script_analysis", self.script_analyzer.analyze),
                ("permission_analysis", self.permission_analyzer.analyze),
                ("dependency_analysis", self.dependency_analyzer.analyze)
            ]:
                result = self._safe_analyze(analyzer_func, context.skill_path, analyzer_name)
                if result:
                    # 转换并添加
                    self._add_normalized_finding(context, result, analyzer_name)

            # 2. 执行规则引擎扫描 (返回 List[Dict])
            rule_results = self._safe_scan_rules(context.skill_path)
            if rule_results:
                for res in rule_results:
                    self._add_normalized_finding(context, res, "rule_engine")
            
            logger.info(f"Completed static security analysis. Current findings: {len(context.findings)}")
            
        except Exception as e:
            logger.error(f"Static analysis critical failure: {str(e)}", exc_info=True)

    def _add_normalized_finding(self, context: AuditContext, raw_data: Dict, category: str) -> None:
        if not self._is_valid_finding(raw_data):
            return

        # --- 特殊处理依赖分析：将其拆解为多个具体的 Finding ---
        if category == "rule_engine" and raw_data.get("title") == "dependency and supply chain analysis":
            # 1. 把具体的“可疑项”拆出来，每一项都是一个独立的 Finding
            suspicious_list = raw_data.get("suspicious", [])
            for item in suspicious_list:
                context.add_finding({
                    "agent": self.name,
                    "type": item.get("type", "suspicious_dependency"),
                    "risk_level": item.get("level", "medium"),
                    "reason": f"供应链风险: {item.get('reason')}",
                    "evidence": {
                        "file": item.get("file"),
                        "item": item.get("item") or item.get("pattern"),
                        "detail": item.get("reason")
                    }
                })
            
            # 2. 把“恶意库引用”拆出来
            for ref in raw_data.get("code_references", []):
                sec = ref.get("security_check", {})
                if not sec.get("safe", True):
                    context.add_finding({
                        "agent": self.name,
                        "type": "malicious_import",
                        "risk_level": sec.get("risk_level", "high"),
                        "reason": f"代码中引入了高风险第三方库: {ref.get('module')}",
                        "evidence": ref
                    })

            # 3. 最后只保留一个极简的“概览” (不塞入那 300 个 URL)
            summary = raw_data.get("summary", {})
            context.add_finding({
                "agent": self.name,
                "type": "dependency_overview",
                "risk_level": "low",
                "reason": f"依赖环境概览：共识别 {summary.get('total_dependencies')} 个库，{summary.get('unique_urls')} 个外部链接。",
                "evidence": f"高风险项已在上方单独列出。其余 {summary.get('unique_urls')} 个链接经过初筛暂无即时威胁。"
            })
            return 

        # --- 其他普通分析结果的标准化 (保持不变) ---
        finding = {
            "agent": self.name,
            "type": raw_data.get("type") or raw_data.get("title") or f"static_{category}",
            "risk_level": str(raw_data.get("risk_level") or raw_data.get("level") or "low").lower(),
            "reason": raw_data.get("reason") or raw_data.get("description") or "检测到异常",
            "evidence": raw_data.get("evidence") or raw_data
        }
        context.add_finding(finding)
    def _safe_analyze(self, analyzer_func: Any, path: str, name: str) -> Dict | None:
        try:
            return analyzer_func(path)
        except Exception as e:
            logger.warning(f"{name} failed: {e}")
            return None

    def _safe_scan_rules(self, path: str) -> List[Dict]:
        try:
            res = self.rule_engine.scan(path)
            return res if isinstance(res, list) else []
        except Exception as e:
            logger.warning(f"Rule engine failed: {e}")
            return []

    def _is_valid_finding(self, finding: Any) -> bool:
        """检查是否有实质性内容，避免产生空报告"""
        if not isinstance(finding, dict): return False
        
        # 检查是否包含关键内容，或者是占位符
        has_content = any([
            finding.get("evidence"),
            finding.get("title"),
            finding.get("type"),
            finding.get("description")
        ])
        
        # 排除只有 title 但没内容的占位符
        if finding.get("level") == "info" and not finding.get("evidence"):
            return False
            
        return has_content
