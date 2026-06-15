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
        paginated_items = items[start:end]
        
        # 导入需要的模块
        import datetime as dt
        from pathlib import Path
        import json
        
        # 预先加载所有报告的 metadata，构建 skill_name -> 最新审计时间的映射
        skill_audit_times = {}
        try:
            reports_dir = Path("data/reports")
            if reports_dir.exists():
                # 获取所有 JSON 报告文件
                report_files = list(reports_dir.glob("audit_*.json"))
                for report_file in report_files:
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        # 从 metadata 中获取 skill_name
                        skill_name = report_data.get('metadata', {}).get('skill_name', '')
                        if skill_name:
                            # 获取文件修改时间作为审计时间
                            audit_time = dt.datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
                            # 如果这个 skill 还没有记录，或者这个报告更新，则更新
                            if skill_name not in skill_audit_times or audit_time > skill_audit_times[skill_name]:
                                skill_audit_times[skill_name] = audit_time
                    except Exception:
                        # 单个报告解析失败不影响其他报告
                        continue
        except Exception:
            # 报告目录加载失败不影响列表显示
            pass
        
        # 增强返回数据：确保包含必要的显示字段
        for item in paginated_items:
            # 确保有 risk_level 字段（从 quick_check 或 last_audit 中获取）
            if not item.get('risk_level'):
                quick_check = item.get('quick_check', {})
                if isinstance(quick_check, dict):
                    item['risk_level'] = quick_check.get('level', 'unknown')
            
            # 确保有 last_audit 字段
            if not item.get('last_audit'):
                # 优先从 quick_check 的 timestamp 获取
                quick_check = item.get('quick_check', {})
                if isinstance(quick_check, dict) and quick_check.get('timestamp'):
                    item['last_audit'] = quick_check.get('timestamp')
                else:
                    # 尝试从预加载的报告映射中查找
                    skill_name = item.get('name', '')
                    if skill_name and skill_name in skill_audit_times:
                        item['last_audit'] = skill_audit_times[skill_name]
                    elif skill_name:
                        # 如果精确匹配失败，尝试通过路径匹配（提取文件名）
                        try:
                            skill_path = item.get('path', '')
                            if skill_path:
                                path_skill_name = Path(skill_path).name
                                if path_skill_name in skill_audit_times:
                                    item['last_audit'] = skill_audit_times[path_skill_name]
                        except Exception:
                            # 路径解析失败不影响显示
                            pass
        
        return {"items": paginated_items, "total": total}

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

    def delete(self, skill_id: str) -> dict | None:
        data = self._load()
        removed: dict | None = None
        kept: list = []
        for i in data.get("items", []):
            if i.get("id") == skill_id:
                removed = i
            else:
                kept.append(i)
        if removed is None:
            return None
        data["items"] = kept
        self._save(data)
        return removed

