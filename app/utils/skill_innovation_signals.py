"""技能包审计创新信号（区别于通用代码 SAST 的启发式聚合，不改变 findings 生成逻辑）。"""
from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path
from typing import Any

_LOCKFILE_NAMES = frozenset(
    {
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "pipfile",
        "pipfile.lock",
        "cargo.toml",
        "cargo.lock",
        "go.mod",
        "go.sum",
        "gemfile",
        "gemfile.lock",
    }
)
_SHELL_SUFFIXES = frozenset({".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"})


def _normalize_skill_md(text: str, max_chars: int = 80000) -> str:
    if not text:
        return ""
    chunk = text[:max_chars]
    return re.sub(r"\s+", " ", chunk).strip()


def _read_skill_md_text(skill_path: str) -> str:
    p = Path(skill_path)
    if p.is_dir():
        f = p / "SKILL.md"
        if f.is_file():
            try:
                return f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return ""
        return ""
    if p.is_file() and p.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(p, "r") as zf:
                for name in zf.namelist():
                    n = name.replace("\\", "/")
                    if n.endswith("/SKILL.md") or n == "SKILL.md":
                        return zf.read(name).decode("utf-8", errors="ignore")
        except (OSError, zipfile.BadZipFile, KeyError):
            return ""
    return ""


def _extract_file_rows(parsed: dict[str, Any]) -> tuple[list[dict[str, Any]], int, bool]:
    """从 ParserAgent 写入的 parsed 结构中提取文件行、总数、是否发现 SKILL.md。"""
    struct = parsed.get("structure")
    if not isinstance(struct, dict):
        return [], 0, False
    files = struct.get("files") or []
    if not isinstance(files, list):
        files = []
    inner = struct.get("structure") if isinstance(struct.get("structure"), dict) else {}
    total = inner.get("total_files")
    if isinstance(total, int) and total >= 0:
        n = total
    else:
        n = len(files)
    smd = bool(struct.get("skill_md_found"))
    return files, n, smd


def compute_intent_fingerprint(skill_path: str, manifest: dict[str, Any], files: list[dict[str, Any]]) -> dict[str, Any]:
    """声明意图 + 目录骨架 + SKILL.md 正文（截断）的稳定指纹，用于跨版本比对与溯源。"""
    md_raw = _read_skill_md_text(skill_path)
    md_norm = _normalize_skill_md(md_raw)
    paths = sorted({str(f.get("path") or "").replace("\\", "/") for f in files if f.get("path")})[:120]
    bundle = "\n".join(
        [
            f"name={manifest.get('name') or ''}",
            f"version={manifest.get('version') or ''}",
            f"desc_head={(manifest.get('description') or '')[:800]}",
            "paths=" + "|".join(paths),
            "skill_md_norm=" + md_norm[:50000],
        ]
    ).encode("utf-8", errors="ignore")
    full = hashlib.sha256(bundle).hexdigest()
    return {
        "algorithm": "sha256",
        "short_id": full[:16],
        "full_hash": full,
        "skill_md_included": bool(md_norm),
        "path_sample_count": len(paths),
        "note": "用于同一技能包不同版本或不同构建之间的「意图一致性」比对；非加密安全用途。",
    }


def _lockfile_hits(files: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    for f in files:
        rel = str(f.get("path") or "").replace("\\", "/")
        if not rel:
            continue
        name = Path(rel).name.lower()
        if name in _LOCKFILE_NAMES:
            hits.append(rel)
    return sorted(set(hits))[:30]


def _shell_like_count(files: list[dict[str, Any]]) -> int:
    n = 0
    for f in files:
        suf = str(f.get("suffix") or "").lower()
        name = Path(str(f.get("path") or "")).name.lower()
        if suf in _SHELL_SUFFIXES or Path(name).suffix.lower() in _SHELL_SUFFIXES:
            n += 1
    return n


def compute_declared_vs_surface_signals(
    manifest: dict[str, Any], files: list[dict[str, Any]], total_files: int, skill_md_found: bool
) -> list[dict[str, Any]]:
    """清单声明与仓库表面特征之间的张力（技能生态常见问题）。"""
    out: list[dict[str, Any]] = []
    deps = manifest.get("dependencies")
    dep_empty = not deps or (isinstance(deps, list) and len(deps) == 0)
    locks = _lockfile_hits(files)
    if dep_empty and locks:
        out.append(
            {
                "code": "deps_empty_but_lockfiles_present",
                "severity": "warning",
                "title": "声明依赖为空，但存在锁文件/包清单",
                "detail": f"Manifest 中 dependencies 为空，但发现: {', '.join(locks[:8])}{'…' if len(locks) > 8 else ''}",
            }
        )

    if total_files > 0 and not skill_md_found:
        out.append(
            {
                "code": "missing_skill_md",
                "severity": "info",
                "title": "未发现 SKILL.md",
                "detail": "多数技能包规范以 SKILL.md 为入口说明；缺少时人机可读性与平台发现能力会下降。",
            }
        )

    # 从 files 推断多入口：根目录脚本/可执行
    root_scripts = [
        f.get("path")
        for f in files
        if f.get("path")
        and "/" not in str(f.get("path")).replace("\\", "/").strip("/")
        and str(f.get("suffix", "")).lower() in (_SHELL_SUFFIXES | {".py", ".js"})
    ]
    if len(root_scripts) >= 4:
        out.append(
            {
                "code": "many_root_executables",
                "severity": "info",
                "title": "根目录可执行/脚本入口较多",
                "detail": f"共 {len(root_scripts)} 个候选根入口，技能边界与最小权限原则下建议收敛。",
            }
        )

    if total_files > 400:
        out.append(
            {
                "code": "very_large_skill_tree",
                "severity": "info",
                "title": "技能包文件规模偏大",
                "detail": f"约 {total_files} 个文件，审查与运行时暴露面更大，建议分层分包。",
            }
        )

    return out


def compute_autonomy_surface(files: list[dict[str, Any]], total_files: int) -> dict[str, Any]:
    """Agent 技能「自主执行面」粗粒度刻画：脚本/壳层密度（非等价于恶意）。"""
    shell_n = _shell_like_count(files)
    ratio = shell_n / max(total_files, 1)
    if shell_n >= 5 or ratio >= 0.08:
        hint = "偏高"
        level = "high"
    elif shell_n >= 2 or ratio >= 0.03:
        hint = "中等"
        level = "medium"
    else:
        hint = "偏低"
        level = "low"
    return {
        "shell_like_file_count": shell_n,
        "total_files": total_files,
        "shell_density": round(ratio, 4),
        "interpretation": f"壳层/脚本类文件相对规模「{hint}」——技能越常驱动子进程，越需在提示词与工具策略上做额外约束。",
        "level": level,
    }


def build_openclaw_innovation_bundle(data: dict[str, Any]) -> dict[str, Any]:
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    manifest = parsed.get("manifest") if isinstance(parsed.get("manifest"), dict) else {}
    files, total_files, skill_md_found = _extract_file_rows(parsed)
    skill_path = str(data.get("skill_path") or "")

    intent = compute_intent_fingerprint(skill_path, manifest, files)
    signals = compute_declared_vs_surface_signals(manifest, files, total_files, skill_md_found)
    autonomy = compute_autonomy_surface(files, total_files)

    return {
        "intent_fingerprint": intent,
        "declared_vs_surface": signals,
        "autonomy_surface": autonomy,
        "about": "OpenClaw 将「技能包」视为带声明意图的可执行知识单元；本节为声明—实现—执行面三维启发式，常规通用 SAST 通常不单独输出。",
    }
