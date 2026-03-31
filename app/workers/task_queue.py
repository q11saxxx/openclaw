"""任务队列入口。

规则描述：
- 后续可替换为 Celery / RQ / Dramatiq。
- 当前保持轻量占位，避免过早引入复杂基础设施。
"""
class TaskQueue:
    def enqueue(self, name: str, payload: dict) -> dict:
        return {"task": name, "payload": payload}
