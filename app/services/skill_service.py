"""Skill 服务。

规则描述：
- 负责 skill 文件级操作：保存、解压、预解析、哈希计算等。
- 不直接承担审计决策逻辑。
"""
from app.analyzers.skill_parser import SkillParser

class SkillService:
    def __init__(self) -> None:
        self.parser = SkillParser()

    def parse_skill(self, path: str) -> dict:
        return {"path": path, "parsed": self.parser.parse(path)}
