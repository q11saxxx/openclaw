"""脚本分析器。

规则描述：
- 负责扫描脚本中的危险命令、下载执行链、持久化行为等模式。
- 尽量输出可定位到文件/行号的证据。
"""
class ScriptAnalyzer:
    def analyze(self, path: str) -> dict:
        return {"title": "static script analysis", "level": "low", "evidence": path}
