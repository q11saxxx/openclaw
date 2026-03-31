"""清单解析器。

规则描述：
- 负责解析 YAML/frontmatter/自定义元数据。
- 元数据提取应保持字段稳定，便于后续评分模块使用。
"""
class ManifestParser:
    def parse(self, path: str) -> dict:
        return {"name": "unknown", "version": "0.1.0", "path": path}
