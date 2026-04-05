"""Skill 仓储。简单的 JSON 文件存储实现（PoC）。"""
from pathlib import Path
import json
import uuid
import datetime
from threading import Lock


DB_PATH = Path("data/skills.json")
DB_LOCK = Lock()


class SkillRepository:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists():
            DB_PATH.write_text(json.dumps({"items": []}, ensure_ascii=False))

    def _load(self) -> dict:
        with DB_LOCK:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        with DB_LOCK:
            DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save(self, payload: dict) -> dict:
        data = self._load()
        item = payload.copy()
        if "id" not in item:
            item["id"] = uuid.uuid4().hex
        if "created_at" not in item:
            item["created_at"] = datetime.datetime.utcnow().isoformat()
        data.setdefault("items", []).append(item)
        self._save(data)
        return item

    def list(self, page: int = 1, size: int = 10, q: str | None = None, risk_level: str | None = None) -> dict:
        data = self._load()
        items = data.get("items", [])
        # simple filtering
        if q:
            items = [i for i in items if q.lower() in (i.get("name", "") or "").lower() or q.lower() in (i.get("path", "") or "").lower()]
        if risk_level:
            items = [i for i in items if (i.get("risk_level") or "").lower() == risk_level.lower()]
        total = len(items)
        # pagination
        start = max((page - 1) * size, 0)
        end = start + size
        return {"items": items[start:end], "total": total}

    def get(self, skill_id: str) -> dict | None:
        data = self._load()
        for i in data.get("items", []):
            if i.get("id") == skill_id:
                return i
        return None

    def update(self, skill_id: str, updates: dict) -> dict | None:
        data = self._load()
        changed = False
        for idx, i in enumerate(data.get("items", [])):
            if i.get("id") == skill_id:
                data["items"][idx] = {**i, **updates}
                changed = True
                result = data["items"][idx]
                break
        if changed:
            self._save(data)
            return result
        return None

