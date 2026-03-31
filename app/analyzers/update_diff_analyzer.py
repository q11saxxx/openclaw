import hashlib
import re
from pathlib import Path
from typing import Any


class UpdateDiffAnalyzer:
    """版本差异分析器。

    规则描述：
    - 若提供 previous_path，则比较当前版本与历史版本的关键差异。
    - 若未提供 previous_path，则仅生成当前版本指纹。
    - 重点关注新增脚本、外部 URL、关键文件变化、风险面扩大。
    """

    URL_PATTERN = re.compile(r"https?://[^\s)\]>'\"]+")

    def analyze(
        self,
        current_path: str | Path,
        previous_path: str | Path | None = None,
    ) -> dict[str, Any]:
        current_root = Path(current_path)
        if not current_root.exists():
            raise FileNotFoundError(f"Current skill path not found: {current_root}")

        current_snapshot = self._build_snapshot(current_root)

        if previous_path is None:
            return {
                "has_baseline": False,
                "current_snapshot": current_snapshot,
                "findings": [
                    {
                        "level": "low",
                        "type": "no_baseline",
                        "message": "未提供历史版本基线，无法进行版本差异分析",
                    }
                ],
                "risk_score": 0,
            }

        previous_root = Path(previous_path)
        if not previous_root.exists():
            return {
                "has_baseline": False,
                "current_snapshot": current_snapshot,
                "findings": [
                    {
                        "level": "low",
                        "type": "baseline_not_found",
                        "message": f"历史版本路径不存在: {previous_root}",
                    }
                ],
                "risk_score": 0,
            }

        previous_snapshot = self._build_snapshot(previous_root)

        current_files = set(current_snapshot["files"].keys())
        previous_files = set(previous_snapshot["files"].keys())

        added_files = sorted(current_files - previous_files)
        removed_files = sorted(previous_files - current_files)
        changed_files = sorted(
            file_name
            for file_name in (current_files & previous_files)
            if current_snapshot["files"][file_name] != previous_snapshot["files"][file_name]
        )

        new_scripts = sorted(
            set(current_snapshot["scripts"]) - set(previous_snapshot["scripts"])
        )
        new_urls = sorted(
            set(current_snapshot["external_urls"]) - set(previous_snapshot["external_urls"])
        )

        findings: list[dict[str, Any]] = []
        risk_score = 0

        if added_files:
            findings.append({
                "level": "low",
                "type": "added_files",
                "message": f"新增文件: {added_files}",
            })
            risk_score += min(8, len(added_files) * 2)

        if removed_files:
            findings.append({
                "level": "low",
                "type": "removed_files",
                "message": f"删除文件: {removed_files}",
            })
            risk_score += min(6, len(removed_files))

        if changed_files:
            findings.append({
                "level": "medium",
                "type": "changed_files",
                "message": f"变更文件: {changed_files}",
            })
            risk_score += min(15, len(changed_files) * 3)

        if new_scripts:
            findings.append({
                "level": "high",
                "type": "new_scripts",
                "message": f"新增脚本/代码文件: {new_scripts}",
            })
            risk_score += 30

        if new_urls:
            findings.append({
                "level": "medium",
                "type": "new_external_urls",
                "message": f"新增外部 URL: {new_urls}",
            })
            risk_score += 15

        risk_drift = "low"
        if risk_score >= 30:
            risk_drift = "high"
        elif risk_score >= 15:
            risk_drift = "medium"

        return {
            "has_baseline": True,
            "added_files": added_files,
            "removed_files": removed_files,
            "changed_files": changed_files,
            "new_scripts": new_scripts,
            "new_urls": new_urls,
            "risk_drift": risk_drift,
            "findings": findings,
            "risk_score": risk_score,
            "current_snapshot": current_snapshot,
            "previous_snapshot": previous_snapshot,
        }

    def _build_snapshot(self, root: Path) -> dict[str, Any]:
        files: dict[str, str] = {}
        scripts: set[str] = set()
        external_urls: set[str] = set()

        for path in root.rglob("*"):
            if path.is_dir():
                continue

            rel = path.relative_to(root).as_posix()

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""

            files[rel] = self._hash_text(text)

            if path.suffix in {".sh", ".py", ".js", ".ts"}:
                scripts.add(rel)

            for url in self.URL_PATTERN.findall(text):
                external_urls.add(url)

        return {
            "files": files,
            "scripts": sorted(scripts),
            "external_urls": sorted(external_urls),
        }

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()