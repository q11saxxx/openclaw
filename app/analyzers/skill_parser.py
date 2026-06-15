"""Skill 目录结构解析器。

规则描述：
- 负责解析 skill 目录中的文件、子目录、入口点、清单候选文件。
- 提供稳定的结构化输出，便于 ParserAgent 进一步验证和分析。
"""
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
import logging

from app.analyzers.manifest_parser import ManifestParser

logger = logging.getLogger(__name__)


class SkillParser:
    """OpenClaw skill 目录解析器。"""

    MANIFEST_CANDIDATES = {
        "SKILL.md",
        "manifest.yaml",
        "manifest.yml",
        ".instructions.md",
        ".prompt.md",
        ".agent.md",
    }
    ENTRYPOINT_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".bash", ".ps1"}
    ROOT_ENTRY_NAMES = {
        "main.py",
        "app.py",
        "run.py",
        "index.py",
        "skill.py",
        "start.sh",
        "entrypoint.sh",
        "index.js",
        "server.py",
    }

    def __init__(self) -> None:
        self.manifest_parser = ManifestParser()

    def parse(self, skill_path: str) -> Dict[str, Any]:
        """
        解析 skill 目录结构。

        Args:
            skill_path: skill 目录路径

        Returns:
            包含文件列表、结构元数据、入口点和清单候选文件的字典。
        """
        path = Path(skill_path)
        result: Dict[str, Any] = {
            "path": str(path),
            "skill_md_found": False,
            "manifest_files": [],
            "entry_points": [],
            "files": [],
            "structure": {
                "total_files": 0,
                "total_dirs": 0,
                "subdirectories": [],
                "file_types": {},
                "manifest_files": [],
            },
            "errors": [],
        }

        if not path.exists():
            result["errors"].append(f"Path does not exist: {skill_path}")
            return result

        if not path.is_dir():
            result["errors"].append(f"Path is not a directory: {skill_path}")
            return result

        file_types: Counter[str] = Counter()
        subdirectories = set()
        entry_points = []

        try:
            for item in path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(path)
                    suffix = item.suffix.lower()
                    file_types[suffix] += 1

                    result["files"].append(
                        {
                            "path": str(relative_path).replace("\\", "/"),
                            "name": item.name,
                            "suffix": suffix,
                            "size": item.stat().st_size,
                        }
                    )

                    if relative_path.parent != Path("."):
                        subdirectories.add(str(relative_path.parent).replace("\\", "/"))

                    if item.name == "SKILL.md":
                        result["skill_md_found"] = True

                    if item.name in self.MANIFEST_CANDIDATES and item.name not in result["manifest_files"]:
                        result["manifest_files"].append(item.name)

                    if self._is_entry_point(item, path):
                        entry_points.append(
                            {
                                "path": str(relative_path).replace("\\", "/"),
                                "type": "root" if relative_path.parent == Path(".") else "nested",
                            }
                        )

            if not entry_points:
                entry_points = self._guess_entry_points(path)

            result["entry_points"] = entry_points
            result["structure"]["total_files"] = len(result["files"])
            result["structure"]["total_dirs"] = len(subdirectories)
            result["structure"]["subdirectories"] = sorted(subdirectories)
            result["structure"]["file_types"] = dict(file_types)
            result["structure"]["manifest_files"] = result["manifest_files"]

        except Exception as exc:
            logger.error(f"Error scanning skill directory {skill_path}: {exc}", exc_info=True)
            result["errors"].append(str(exc))

        return result

    def _is_entry_point(self, item: Path, root_path: Path) -> bool:
        """判断文件是否可能是 skill 的入口点。"""
        if item.name.lower() in self.ROOT_ENTRY_NAMES:
            return True

        if item.suffix.lower() in self.ENTRYPOINT_EXTENSIONS:
            if item.parent == root_path:
                return True
            if item.parent.name.lower() in {"scripts", "bin", "src"}:
                return True

        return False

    def _guess_entry_points(self, root_path: Path) -> List[Dict[str, str]]:
        """在找不到明显入口时，尝试推断可能入口文件。"""
        candidates = []
        for item in root_path.iterdir():
            if item.is_file() and item.suffix.lower() in self.ENTRYPOINT_EXTENSIONS:
                candidates.append(
                    {
                        "path": str(item.name),
                        "type": "root",
                    }
                )
        return candidates


