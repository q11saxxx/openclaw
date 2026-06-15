"""Findings 去重与严重等级归并（提升决策侧信噪比）。

对 (agent, type, 规范化 reason 摘要, 证据定位键) 相同的项只保留一条，
若重复项风险等级更高则升级保留项。"""
from __future__ import annotations

import json
from typing import Any

_SEVERITY_RANK: dict[str, int] = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
    "unknown": 0,
}


def _risk_rank(level: str | None) -> int:
    return _SEVERITY_RANK.get(str(level or "low").lower(), 1)


def _evidence_loc_key(evidence: Any) -> str:
    if isinstance(evidence, dict):
        fp = str(evidence.get("file_path") or evidence.get("file") or "")
        ln = evidence.get("line_number") or evidence.get("line") or ""
        return f"{fp}:{ln}"
    if isinstance(evidence, str):
        return evidence[:160]
    try:
        return json.dumps(evidence, sort_keys=True, ensure_ascii=False)[:200]
    except TypeError:
        return str(evidence)[:160]


def dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not findings:
        return []
    buckets: dict[tuple[Any, ...], dict[str, Any]] = {}
    order: list[tuple[Any, ...]] = []
    for f in findings:
        if not isinstance(f, dict):
            continue
        reason = str(f.get("reason") or f.get("description") or "").strip().lower()[:160]
        key = (
            str(f.get("agent") or ""),
            str(f.get("type") or ""),
            reason,
            _evidence_loc_key(f.get("evidence")),
        )
        if key not in buckets:
            buckets[key] = dict(f)
            order.append(key)
        else:
            cur = buckets[key]
            if _risk_rank(f.get("risk_level")) > _risk_rank(cur.get("risk_level")):
                buckets[key] = dict(f)
    return [buckets[k] for k in order]
