"""安全基础配置。

规则描述：
- 放置全局安全相关基础项，如允许的文件类型、最大上传大小、危险路径前缀等。
- 不要在规则引擎和安全配置之间重复定义同一份规则。
"""
ALLOWED_ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz"}
MAX_UPLOAD_SIZE_MB = 50
SENSITIVE_PATH_HINTS = ["/etc", "/root", "~/.ssh", ".env", "id_rsa"]
