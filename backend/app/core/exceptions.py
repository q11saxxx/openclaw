"""本文件说明：定义项目级自定义异常，后续统一映射为 API 错误响应。"""

class ScanEngineError(Exception):
    """本异常说明：核心扫描引擎执行失败时抛出。"""


class ReportExportError(Exception):
    """本异常说明：报告导出失败时抛出。"""
