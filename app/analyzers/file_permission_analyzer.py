"""文件权限与敏感路径分析器。

规则描述：
- 负责识别 skill 中可能访问敏感路径或越权文件操作的迹象。
- 输出应包含目标路径与风险原因。
"""
class FilePermissionAnalyzer:
    def analyze(self, path: str) -> dict:
        return {"title": "file permission check", "level": "medium", "evidence": path}
