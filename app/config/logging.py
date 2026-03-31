"""日志配置。

规则描述：
- 统一封装日志初始化逻辑。
- 业务代码使用 logging.getLogger(__name__) 获取 logger。
- 后续可在此扩展 JSON 日志、链路追踪和审计日志落盘。
"""
import logging

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
