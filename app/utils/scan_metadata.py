"""报告元数据增强：扫描可复现性、许可证类文件探测（不改变 findings 逻辑）。"""
from __future__ import annotations

import datetime as dt
import os
import zipfile
from pathlib import Path
from typing import Any

# 与 SPDX / 常见开源实践相关的文件名（小写匹配）
_LICENSE_BASE_NAMES = frozenset(
    {
        "license",
        "license.txt",
        "license.md",
        "copying",
        "notice",
        "authors",
        "third_party_notices.txt",
    }
)


def platform_engine_version() -> str:
    """与历史报告字段 metadata.engine_version 保持默认同级，可通过环境变量覆盖。"""
    return os.environ.get("OPENCLAW_ENGINE_VERSION", "OpenClaw-Risk-Platform-V1")


def _parse_start_time(start_iso: str | None) -> dt.datetime | None:
    if not start_iso or not isinstance(start_iso, str):
        return None
    try:
        return dt.datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    except ValueError:
        try:
            return dt.datetime.fromisoformat(start_iso)
        except ValueError:
            return None


def compute_duration_ms(start_iso: str | None) -> int | None:
    st = _parse_start_time(start_iso)
    if st is None:
        return None
    end = dt.datetime.now(st.tzinfo) if st.tzinfo else dt.datetime.now()
    return max(0, int((end - st).total_seconds() * 1000))


def safe_options_echo(options: Any) -> dict[str, Any]:
    if not isinstance(options, dict):
        return {}
    keys = ("semantic", "static_security", "dependency_check", "ai_preprocessing", "surface_intel")
    out: dict[str, Any] = {}
    for k in keys:
        if k not in options:
            continue
        v = options[k]
        if isinstance(v, (bool, int, float, str)):
            out[k] = v
    return out


def _license_like_path(rel: str) -> bool:
    base = Path(rel).name.lower()
    if base in _LICENSE_BASE_NAMES:
        return True
    if base.startswith("license.") or base.startswith("copying."):
        return True
    if "third_party" in base and "notice" in base:
        return True
    return False


def collect_license_like_paths(skill_path: str, parsed: dict[str, Any]) -> list[str]:
    """从已解析的结构或磁盘 / zip 中收集许可证类路径（仅展示名，不读内容）。"""
    found: set[str] = set()
    structure = parsed.get("structure") if isinstance(parsed.get("structure"), dict) else {}
    inner_files: list[Any] = structure.get("files") or parsed.get("files") or []
    for item in inner_files:
        if not isinstance(item, dict):
            continue
        rel = str(item.get("path") or item.get("name") or "").replace("\\", "/").strip()
        if rel and _license_like_path(rel):
            found.add(rel)

    p = Path(skill_path)
    try:
        if p.is_file() and p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p, "r") as zf:
                for name in zf.namelist()[:800]:
                    name = name.replace("\\", "/")
                    if name.endswith("/"):
                        continue
                    if _license_like_path(name):
                        found.add(name)
        elif p.is_dir():
            for item in p.rglob("*"):
                if not item.is_file():
                    continue
                try:
                    rel = str(item.relative_to(p)).replace("\\", "/")
                except ValueError:
                    continue
                if _license_like_path(rel):
                    found.add(rel)
    except OSError:
        pass

    return sorted(found)[:50]


def build_scan_block(data: dict[str, Any]) -> dict[str, Any]:
    start_iso = data.get("start_time")
    finished = dt.datetime.now().isoformat()
    return {
        "started_at": start_iso,
        "finished_at": finished,
        "duration_ms": compute_duration_ms(start_iso),
        "baseline_used": bool(data.get("previous_skill_path")),
        "options_applied": safe_options_echo(data.get("options")),
        "agent_errors": dict(data.get("errors") or {}),
    }
