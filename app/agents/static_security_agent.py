from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.script_analyzer import ScriptAnalyzer
from app.analyzers.file_permission_analyzer import FilePermissionAnalyzer
from app.rules.rule_engine import RuleEngine

class StaticSecurityAgent(BaseAgent):
    """静态安全扫描代理。

    规则描述：
    - 负责危险命令、敏感路径、可疑外联等静态规则检测。
    - 所有静态规则应优先进入 rules/ 统一管理。
    """
    name = "static_security"

    def __init__(self) -> None:
        self.script_analyzer = ScriptAnalyzer()
        self.permission_analyzer = FilePermissionAnalyzer()
        self.rule_engine = RuleEngine()

    def run(self, context: AuditContext) -> None:
        context.add_finding(self.script_analyzer.analyze(context.skill_path))
        context.add_finding(self.permission_analyzer.analyze(context.skill_path))
        context.findings.extend(self.rule_engine.scan(context.skill_path))
