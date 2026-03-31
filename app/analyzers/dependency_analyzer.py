import json
import re
from pathlib import Path
from typing import Any


class DependencyAnalyzer:
    """依赖与来源分析器。

    规则描述：
    - 解析 SKILL.md frontmatter，抽取 name / description。
    - 解析 _meta.json，抽取 ownerId / slug / version / publishedAt。
    - 扫描脚本文件、hook 路径、外部 URL、可执行文件。
    - 输出结构化 findings 与风险分数，供 DecisionAgent 融合。
    """

    URL_PATTERN = re.compile(r"https?://[^\s)\]>'\"]+")
    LOCAL_SCRIPT_REF_PATTERN = re.compile(r"(?:\.?/|~/)[^\s)\]>'\"]*scripts/[^\s)\]>'\"]+")
    FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

    def analyze(self, skill_path: str | Path) -> dict[str, Any]:
        root = Path(skill_path)
        if not root.exists():
            raise FileNotFoundError(f"Skill path not found: {root}")

        source = self._analyze_source(root)
        dependencies = self._analyze_dependencies(root)

        findings: list[dict[str, Any]] = []
        risk_score = 0

        executable_files = dependencies.get("executable_files", [])
        if executable_files:
            findings.append({
                "level": "medium",
                "type": "executable_files",
                "message": f"发现可执行脚本文件: {executable_files}",
            })
            risk_score += 20

        hook_paths = dependencies.get("hook_paths", [])
        if hook_paths:
            findings.append({
                "level": "medium",
                "type": "hook_reference",
                "message": f"发现 hook / 脚本调用路径: {hook_paths}",
            })
            risk_score += 15

        external_urls = dependencies.get("external_urls", [])
        if external_urls:
            findings.append({
                "level": "medium",
                "type": "external_urls",
                "message": f"发现外部 URL 引用: {external_urls}",
            })
            risk_score += 10

        manifest_files = dependencies.get("manifest_files", [])
        if manifest_files:
            findings.append({
                "level": "low",
                "type": "manifest_files",
                "message": f"发现依赖/清单相关文件: {manifest_files}",
            })
            risk_score += 5

        folder_name = source.get("folder_name")
        declared_name = source.get("declared_name")
        slug = source.get("slug")

        if declared_name and folder_name and declared_name != folder_name:
            findings.append({
                "level": "low",
                "type": "name_mismatch",
                "message": f"目录名 `{folder_name}` 与 SKILL.md 声明名 `{declared_name}` 不一致",
            })
            risk_score += 5

        if slug and folder_name and slug != folder_name:
            findings.append({
                "level": "low",
                "type": "slug_mismatch",
                "message": f"_meta.json slug `{slug}` 与目录名 `{folder_name}` 不一致",
            })
            risk_score += 5

        if not source.get("version"):
            findings.append({
                "level": "low",
                "type": "missing_version",
                "message": "未发现版本信息",
            })
            risk_score += 3

        if not source.get("published_at"):
            findings.append({
                "level": "low",
                "type": "missing_published_at",
                "message": "未发现发布时间字段",
            })
            risk_score += 2

        return {
            "source": source,
            "dependencies": dependencies,
            "findings": findings,
            "risk_score": risk_score,
        }

    def _analyze_source(self, root: Path) -> dict[str, Any]:
        result = {
            "folder_name": root.name,
            "declared_name": None,
            "description": None,
            "owner_id": None,
            "slug": None,
            "version": None,
            "published_at": None,
        }

        skill_md = root / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            frontmatter = self._parse_frontmatter(content)
            result["declared_name"] = frontmatter.get("name")
            result["description"] = frontmatter.get("description")

        meta_file = root / "_meta.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                result["owner_id"] = meta.get("ownerId")
                result["slug"] = meta.get("slug")
                result["version"] = meta.get("version")
                result["published_at"] = meta.get("publishedAt")
            except json.JSONDecodeError:
                pass

        return result

    def _analyze_dependencies(self, root: Path) -> dict[str, Any]:
        scripts: set[str] = set()
        executable_files: set[str] = set()
        external_urls: set[str] = set()
        hook_paths: set[str] = set()
        manifest_files: set[str] = set()

        for path in root.rglob("*"):
            if path.is_dir():
                continue

            rel = path.relative_to(root).as_posix()

            if path.name in {
                "requirements.txt",
                "package.json",
                "package-lock.json",
                "pnpm-lock.yaml",
                "yarn.lock",
                "pyproject.toml",
                "poetry.lock",
            }:
                manifest_files.add(rel)

            if path.suffix in {".sh", ".py", ".js", ".ts"}:
                scripts.add(rel)

            if path.suffix == ".sh":
                executable_files.add(rel)

            if path.suffix.lower() in {".md", ".json", ".sh", ".py", ".js", ".yaml", ".yml", ".txt"}:
                text = path.read_text(encoding="utf-8", errors="ignore")

                for url in self.URL_PATTERN.findall(text):
                    external_urls.add(url)

                for ref in self.LOCAL_SCRIPT_REF_PATTERN.findall(text):
                    hook_paths.add(ref)

        return {
            "scripts": sorted(scripts),
            "executable_files": sorted(executable_files),
            "external_urls": sorted(external_urls),
            "hook_paths": sorted(hook_paths),
            "manifest_files": sorted(manifest_files),
        }

    def _parse_frontmatter(self, content: str) -> dict[str, str]:
        match = self.FRONTMATTER_PATTERN.search(content)
        if not match:
            return {}

        data: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
        return data