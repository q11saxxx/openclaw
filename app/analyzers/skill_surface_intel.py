"""技能包表面情报分析（静态、确定性）。

补充通用规则引擎未覆盖的两类信号：
1) 疑似密钥 / 令牌形态（正则 + 简单熵启发，降低误报上限）
2) 文本中的 URL 暴露面（外链数量、file://、内网 IP 等）

适用于目录型技能包及 .zip 上传包内文本文件。"""
from __future__ import annotations

import math
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

# 仅扫描常见文本类扩展，避免二进制与大文件拖慢审计
_TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".markdown",
        ".txt",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sh",
        ".bash",
        ".ps1",
        ".env",
        ".cfg",
        ".ini",
    }
)

_MAX_FILE_BYTES = 512_000
_MAX_FILES = 450
_MAX_SECRET_FINDINGS = 12
_MAX_URL_HOSTS_IN_EVIDENCE = 48

# 已知令牌前缀 / 形态（高置信启发，非密码学证明）
_SECRET_PATTERNS: list[tuple[str, str, str]] = [
    (r"\bsk-[A-Za-z0-9]{16,}\b", "openai_api_like", "high"),
    (r"\bAKIA[0-9A-Z]{16}\b", "aws_access_key_id_like", "high"),
    (r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b", "github_token_like", "high"),
    (r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b", "slack_token_like", "high"),
    (r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]", "api_key_assignment", "medium"),
    (r"(?i)bearer\s+[A-Za-z0-9._\-]{24,}", "bearer_token_like", "high"),
    (r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", "jwt_like_blob", "medium"),
]

_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]{5,400}", re.IGNORECASE)
_PRIVATE_IP = re.compile(
    r"https?://(127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})([:/]|\b)",
    re.IGNORECASE,
)


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _iter_text_files_dir(root: Path) -> Iterator[tuple[str, Path]]:
    count = 0
    try:
        for p in root.rglob("*"):
            if count >= _MAX_FILES:
                break
            if not p.is_file():
                continue
            if p.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            try:
                if p.stat().st_size > _MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            yield rel, p
            count += 1
    except OSError:
        return


def _iter_text_files_zip(zpath: Path) -> Iterator[tuple[str, bytes]]:
    count = 0
    try:
        with zipfile.ZipFile(zpath, "r") as zf:
            for name in zf.namelist():
                if count >= _MAX_FILES:
                    break
                if name.endswith("/"):
                    continue
                suf = Path(name).suffix.lower()
                if suf not in _TEXT_SUFFIXES:
                    continue
                info = zf.getinfo(name)
                if info.file_size > _MAX_FILE_BYTES or info.file_size <= 0:
                    continue
                try:
                    raw = zf.read(name)
                except (RuntimeError, zipfile.BadZipFile, KeyError):
                    continue
                yield name.replace("\\", "/"), raw
                count += 1
    except (OSError, zipfile.BadZipFile):
        return


def _entropy_hits(text: str, per_file_cap: int = 2) -> list[tuple[int, str]]:
    """对疑似随机长串做熵筛选；每文件最多 per_file_cap 条。"""
    out: list[tuple[int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if len(s) < 40 or len(s) > 220:
            continue
        if not re.search(r"[A-Za-z]", s) or not re.search(r"\d", s):
            continue
        ent = _shannon_entropy(s)
        if ent < 4.3:
            continue
        if len(set(s)) < 12:
            continue
        out.append((i, s[:120]))
        if len(out) >= per_file_cap:
            break
    return out


def _host_from_url(u: str) -> str | None:
    try:
        m = re.match(r"https?://([^/?:#]+)", u, re.IGNORECASE)
        return m.group(1).lower() if m else None
    except Exception:
        return None


class SkillSurfaceIntelAnalyzer:
    name = "skill_surface_intel"

    def analyze(self, skill_path: str) -> list[dict[str, Any]]:
        root = Path(skill_path)
        findings: list[dict[str, Any]] = []
        if not root.exists():
            return findings

        secret_hits: list[dict[str, Any]] = []
        all_urls: list[str] = []

        def handle_file(rel: str, content: str) -> None:
            nonlocal secret_hits, all_urls
            if len(secret_hits) >= 100:
                return
            # 形态类密钥
            for pat, typ, sev in _SECRET_PATTERNS:
                for m in re.finditer(pat, content):
                    snippet = m.group(0)
                    if len(snippet) > 80:
                        snippet = snippet[:40] + "…" + snippet[-20:]
                    secret_hits.append(
                        {
                            "type": typ,
                            "risk_level": sev,
                            "reason": f"发现疑似敏感令牌/密钥形态（{typ}），请确认是否误提交真实凭据。",
                            "evidence": {
                                "file_path": rel,
                                "matched_sample": snippet,
                                "pattern": pat[:80],
                            },
                        }
                    )
                    if len(secret_hits) >= 100:
                        return
            # 熵启发
            for line_no, frag in _entropy_hits(content):
                secret_hits.append(
                    {
                        "type": "high_entropy_string",
                        "risk_level": "low",
                        "reason": "存在高熵长串，可能为硬编码密钥或随机种子，建议人工复核。",
                        "evidence": {
                            "file_path": rel,
                            "line_number": line_no,
                            "snippet": frag,
                        },
                    }
                )
                if len(secret_hits) >= 100:
                    return
            # URL（含 file://，不计入 http 统计但计入暴露面）
            for um in _URL_RE.finditer(content):
                u = um.group(0).rstrip(").,;]")
                all_urls.append(u)
            for fm in re.finditer(r"file://[^\s\"'<>)\]]{3,400}", content, re.IGNORECASE):
                all_urls.append(fm.group(0).rstrip(").,;]"))

        if root.is_dir():
            for rel, p in _iter_text_files_dir(root):
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                handle_file(rel, txt)
        elif root.is_file() and root.suffix.lower() == ".zip":
            for rel, raw in _iter_text_files_zip(root):
                try:
                    txt = raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                handle_file(rel, txt)
        else:
            return findings

        # 截断 secret 命中，避免淹没其它 agent
        secret_hits = secret_hits[:_MAX_SECRET_FINDINGS]
        for h in secret_hits:
            findings.append(
                {
                    "agent": "static_security",
                    "type": h["type"],
                    "risk_level": h["risk_level"],
                    "reason": h["reason"],
                    "evidence": h["evidence"],
                }
            )

        if not all_urls:
            return findings

        hosts: list[str] = []
        private_hits = 0
        file_scheme = 0
        for u in all_urls:
            lu = u.lower()
            if lu.startswith("file:"):
                file_scheme += 1
                continue
            if _PRIVATE_IP.search(u):
                private_hits += 1
            hh = _host_from_url(u)
            if hh:
                hosts.append(hh)

        uniq_external = sorted({h for h in hosts if h and not h.startswith("127.")})
        n_ext = len(uniq_external)
        if n_ext == 0 and file_scheme == 0 and private_hits == 0:
            return findings

        if file_scheme > 0:
            lvl = "high"
            reason = f"发现 {file_scheme} 处 file:// 引用，可能扩大本地文件暴露面。"
        elif n_ext > 20:
            lvl = "medium"
            reason = f"文本中共解析到较多外链主机（约 {n_ext} 个），技能运行时网络暴露面偏大，建议收敛。"
        elif n_ext > 0:
            lvl = "low"
            reason = f"文本中共解析到 {n_ext} 个不同外链主机，供供应链与数据出境评估参考。"
        else:
            lvl = "low"
            reason = "解析到 URL 但多为内网或 file 以外形态，已记录供复核。"

        findings.append(
            {
                "agent": "static_security",
                "type": "url_surface_summary",
                "risk_level": lvl,
                "reason": reason,
                "evidence": {
                    "unique_hosts_sample": uniq_external[:_MAX_URL_HOSTS_IN_EVIDENCE],
                    "unique_host_count": n_ext,
                    "file_scheme_count": file_scheme,
                    "private_ip_url_hits": private_hits,
                    "total_http_urls": len(all_urls),
                },
            }
        )

        return findings
