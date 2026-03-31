"""Skill 结构解析器。

规则描述：
- 负责目录结构、SKILL.md、脚本入口等基础解析。
- 这里只做事实提取，不做风险结论。
"""
class SkillParser:
    def parse(self, path: str) -> dict:
        return {"path": path, "skill_md_found": True, "files": []}
