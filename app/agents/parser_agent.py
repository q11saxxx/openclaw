from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.skill_parser import SkillParser
from app.analyzers.manifest_parser import ManifestParser

class ParserAgent(BaseAgent):
    """Skill 解析代理。

    规则描述：
    - 只负责 skill 基础结构、SKILL.md、manifest 等解析。
    - 不在本 agent 内做风险评分。
    """
    name = "parser"

    def __init__(self) -> None:
        self.skill_parser = SkillParser()
        self.manifest_parser = ManifestParser()

    def run(self, context: AuditContext) -> None:
        context.parsed["structure"] = self.skill_parser.parse(context.skill_path)
        context.parsed["manifest"] = self.manifest_parser.parse(context.skill_path)
