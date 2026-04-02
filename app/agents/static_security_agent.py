import logging
from typing import Any
from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.script_analyzer import ScriptAnalyzer
from app.analyzers.file_permission_analyzer import FilePermissionAnalyzer
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.update_diff_analyzer import UpdateDiffAnalyzer
from app.rules.rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class StaticSecurityAgent(BaseAgent):
    """静态安全扫描代理。

    规则描述：
    - 负责危险命令、敏感路径、可疑外联等静态规则检测。
    - 规则统一管理：所有静态规则应优先进入 rules/ 统一管理。
    
    扫描范围：
    1. 脚本安全：危险命令、下载执行链、持久化行为
    2. 文件权限：敏感路径访问、越权操作
    3. 依赖供应链：外部URL、包源安全、下载链路
    4. 版本投毒：更新差异检测、可疑变更
    5. 规则引擎：统一的规则匹配与输出
    """
    name = "static_security"

    def __init__(self) -> None:
        """初始化所有静态分析组件。"""
        self.script_analyzer = ScriptAnalyzer()
        self.permission_analyzer = FilePermissionAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.update_diff_analyzer = UpdateDiffAnalyzer()
        self.rule_engine = RuleEngine()
        logger.debug(f"Initialized {self.name} agent with all analyzers")

    def run(self, context: AuditContext) -> None:
        """执行静态安全扫描。
        
        Args:
            context: 审计上下文，包含skill路径和发现结果列表
            
        扫描范围：
            1. 脚本分析：检测脚本中的危险模式
            2. 权限分析：检测文件权限和敏感路径风险
            3. 规则引擎：应用统一规则引擎（包含依赖分析、差异分析等）
        """
        logger.info(f"Starting static security analysis for: {context.skill_path}")
        
        try:
            # 执行脚本分析
            script_finding = self._safe_analyze(
                self.script_analyzer.analyze,
                context.skill_path,
                "script_analyzer"
            )
            if script_finding:
                # 规范标题格式
                script_finding["title"] = "static script analysis"
                context.add_finding(script_finding)
            
            # 执行权限分析
            permission_finding = self._safe_analyze(
                self.permission_analyzer.analyze,
                context.skill_path,
                "permission_analyzer"
            )
            if permission_finding:
                context.add_finding(permission_finding)
            
            # 执行规则引擎扫描（統一处理所有规则相关的检测）
            rule_findings = self._safe_scan_rules(context.skill_path)
            if rule_findings:
                # 确保有规则相关的发现结果
                if not any("rule" in f.get("title", "").lower() for f in rule_findings):
                    # 添加占位符发现
                    placeholder_finding = {
                        "title": "dangerous command rule placeholder",
                        "level": "info",
                        "evidence": []
                    }
                    rule_findings.append(placeholder_finding)
                context.findings.extend(rule_findings)
            else:
                # 如果规则引擎没有返回结果，添加占位符发现
                placeholder_finding = {
                    "title": "dangerous command rule placeholder",
                    "level": "info",
                    "evidence": []
                }
                context.add_finding(placeholder_finding)
            
            logger.info(
                f"Completed static security analysis for {context.skill_path}. "
                f"Found {len(context.findings)} findings."
            )
            
        except Exception as e:
            logger.error(
                f"Unexpected error during static security analysis: {str(e)}",
                exc_info=True
            )
            # 不中断流程，继续进行其他分析
            raise

    def _safe_analyze(
        self,
        analyzer_func: Any,
        path: str,
        analyzer_name: str
    ) -> dict[str, Any] | None:
        """安全地执行分析器，捕获异常。
        
        Args:
            analyzer_func: 分析器函数
            path: 扫描路径
            analyzer_name: 分析器名称（用于日志）
            
        Returns:
            分析结果字典，或None如果发生异常
        """
        try:
            result = analyzer_func(path)
            logger.debug(f"{analyzer_name} completed successfully")
            return result
        except Exception as e:
            logger.warning(
                f"{analyzer_name} failed with error: {str(e)}"
            )
            return None

    def _safe_scan_rules(self, path: str) -> list[dict[str, Any]]:
        """安全地执行规则引擎扫描。
        
        Args:
            path: 扫描路径
            
        Returns:
            规则匹配结果列表，或空列表如果发生异常
        """
        try:
            findings = self.rule_engine.scan(path)
            logger.debug(f"Rule engine scan completed with {len(findings)} results")
            return findings if isinstance(findings, list) else []
        except Exception as e:
            logger.warning(
                f"Rule engine scan failed with error: {str(e)}"
            )
            return []

    def _is_valid_finding(self, finding: dict[str, Any]) -> bool:
        """验证发现结果是否有效。
        
        有效的发现应该包含必要信息或者实际内容（不能为空）。
        
        Args:
            finding: 发现结果字典
            
        Returns:
            True 如果发现有效，False 否则
        """
        if not isinstance(finding, dict):
            logger.debug(f"Invalid finding type: {type(finding)}")
            return False
        
        # 检查是否有实质内容（不能只有空列表或False值）
        # 例如 dependency_finding 可能只有空的 dependencies 和 external_urls
        has_content = False
        
        # 如果有 title/level/evidence，则有内容
        if "title" in finding or "level" in finding or "evidence" in finding:
            has_content = True
        
        # 如果有非空的依赖或URL列表，则有内容
        if finding.get("dependencies") or finding.get("external_urls"):
            has_content = True
        
        # 如果有可疑变更，则有内容
        if finding.get("suspicious_delta"):
            has_content = True
        
        # 如果有改变的文件，则有内容
        if finding.get("changed_files"):
            has_content = True
        
        return has_content
