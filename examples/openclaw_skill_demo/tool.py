"""本文件说明：示例风险脚本，故意包含环境变量访问和外部请求，供演示使用。"""

import os


def run() -> str:
    token = os.environ.get("OPENAI_API_KEY", "")
    return f"demo token length: {len(token)}"
