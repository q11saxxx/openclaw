"""文件权限与敏感路径分析器。

规则描述：
- 负责识别 skill 中可能访问敏感路径或越权文件操作的迹象。
- 输出应包含目标路径与风险原因。

扫描范围：
1. 敏感系统路径访问：/etc、/root、/sys 等
2. 权限提升操作：chmod、chown 针对敏感文件
3. 密钥文件访问：.ssh、.aws、.config 等
4. 配置文件修改：/etc/passwd、sudoers、hosts 等
5. 日志文件操作：/var/log 删除或清空等
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FilePermissionAnalyzer:
    """文件权限与敏感路径分析器。
    
    检测脚本中对敏感文件、目录的访问和权限修改操作，
    识别可能的越权、权限提升或数据窃取行为。
    """
    
    # 敏感系统路径（高风险）
    SENSITIVE_SYSTEM_PATHS = {
        '/etc/passwd': {'level': 'critical', 'reason': '用户账户文件'},
        '/etc/shadow': {'level': 'critical', 'reason': '密码哈希文件'},
        '/etc/sudoers': {'level': 'critical', 'reason': '权限配置文件'},
        '/root': {'level': 'critical', 'reason': '根用户主目录'},
        '/root/.ssh': {'level': 'critical', 'reason': '根用户SSH密钥'},
        '/boot': {'level': 'critical', 'reason': '启动文件'},
        '/sys': {'level': 'high', 'reason': '内核参数'},
        '/proc': {'level': 'high', 'reason': '进程信息'},
    }
    
    # 关键配置文件
    CRITICAL_CONFIG_FILES = {
        '/etc/hosts': {'level': 'high', 'reason': '主机名解析'},
        '/etc/hostname': {'level': 'high', 'reason': '主机名'},
        '/etc/resolv.conf': {'level': 'high', 'reason': 'DNS配置'},
        '/etc/ssh/sshd_config': {'level': 'high', 'reason': 'SSH配置'},
        '/etc/cron.d': {'level': 'high', 'reason': '定时任务'},
        '/etc/crontab': {'level': 'high', 'reason': '定时任务'},
        '/etc/rc.local': {'level': 'high', 'reason': '启动脚本'},
        '/etc/systemd': {'level': 'high', 'reason': '系统服务'},
    }
    
    # 用户私密文件
    USER_PRIVATE_FILES = {
        '.ssh': {'level': 'high', 'reason': 'SSH密钥'},
        '.aws': {'level': 'high', 'reason': 'AWS凭证'},
        '.config': {'level': 'medium', 'reason': '应用配置'},
        '.bashrc': {'level': 'medium', 'reason': 'Shell配置'},
        '.bash_history': {'level': 'medium', 'reason': '命令历史'},
        '.gnupg': {'level': 'high', 'reason': 'GPG密钥'},
        '.kube': {'level': 'high', 'reason': 'Kubernetes配置'},
        '.docker': {'level': 'high', 'reason': 'Docker凭证'},
    }
    
    # 日志文件
    LOG_FILES = {
        '/var/log': {'level': 'medium', 'reason': '系统日志'},
        '/var/log/auth.log': {'level': 'high', 'reason': '认证日志'},
        '/var/log/secure': {'level': 'high', 'reason': '认证日志'},
        '/var/log/audit': {'level': 'high', 'reason': '审计日志'},
    }
    
    # 文件操作关键字
    FILE_OPERATIONS = {
        'chmod': {'type': 'permission', 'level': 'medium'},
        'chown': {'type': 'ownership', 'level': 'medium'},
        'chgrp': {'type': 'group', 'level': 'low'},
        'rm': {'type': 'delete', 'level': 'high'},
        'truncate': {'type': 'truncate', 'level': 'high'},
        'dd': {'type': 'raw_write', 'level': 'critical'},
    }
    
    def analyze(self, path: str) -> Dict[str, Any]:
        """分析文件权限与敏感路径访问。
        
        Args:
            path: skill路径，包含待分析的文件
            
        Returns:
            包含分析结果的字典，格式为：
            {
                "title": str,              # 分析标题
                "level": str,              # 风险等级
                "evidence": list,          # 发现的证据列表
                "summary": dict            # 统计摘要
            }
        """
        logger.debug(f"Starting file permission analysis for path: {path}")
        
        findings = {
            "sensitive_paths": [],
            "critical_configs": [],
            "private_files": [],
            "log_operations": [],
            "permission_changes": [],
        }
        
        try:
            # 查找所有文件
            files = self._find_all_files(path)
            logger.debug(f"Found {len(files)} files to analyze")
            
            for file_path in files:
                try:
                    content = self._read_file_safe(file_path)
                    if not content:
                        continue
                    
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        # 跳过注释和空行
                        if not line.strip() or line.strip().startswith('#'):
                            continue
                        
                        # 检测各类风险
                        self._detect_sensitive_paths(
                            line, line_num, file_path,
                            findings["sensitive_paths"]
                        )
                        self._detect_critical_configs(
                            line, line_num, file_path,
                            findings["critical_configs"]
                        )
                        self._detect_private_files(
                            line, line_num, file_path,
                            findings["private_files"]
                        )
                        self._detect_log_operations(
                            line, line_num, file_path,
                            findings["log_operations"]
                        )
                        self._detect_permission_changes(
                            line, line_num, file_path,
                            findings["permission_changes"]
                        )
                
                except Exception as e:
                    logger.warning(f"Error analyzing file {file_path}: {str(e)}")
                    continue
            
            return self._build_result(findings)
        
        except Exception as e:
            logger.error(f"Error during file permission analysis: {str(e)}", exc_info=True)
            return {
                "title": "file permission analysis failed",
                "level": "low",
                "evidence": [],
                "error": str(e)
            }
    
    def _find_all_files(self, path: str) -> List[str]:
        """递归查找目录中的所有文件。"""
        files = []
        
        try:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                return files
            
            if os.path.isfile(path):
                files.append(path)
            else:
                for root, dirs, filenames in os.walk(path):
                    # 跳过隐藏目录
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]
                    
                    for file in filenames:
                        file_path = os.path.join(root, file)
                        files.append(file_path)
        
        except Exception as e:
            logger.warning(f"Error finding files: {str(e)}")
        
        return files
    
    def _read_file_safe(self, path: str) -> str | None:
        """安全地读取文件内容。"""
        try:
            # 限制文件大小（5MB）
            if os.path.getsize(path) > 5 * 1024 * 1024:
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _detect_sensitive_paths(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测敏感系统路径访问。"""
        for path, metadata in self.SENSITIVE_SYSTEM_PATHS.items():
            if path in line:
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "target_path": path,
                    "level": metadata['level'],
                    "reason": metadata['reason'],
                    "content": line.strip(),
                    "type": "sensitive_path"
                })
                logger.debug(f"Found sensitive path '{path}' at {file_path}:{line_num}")
    
    def _detect_critical_configs(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测关键配置文件访问。"""
        for path, metadata in self.CRITICAL_CONFIG_FILES.items():
            if path in line:
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "target_path": path,
                    "level": metadata['level'],
                    "reason": metadata['reason'],
                    "content": line.strip(),
                    "type": "critical_config"
                })
                logger.debug(f"Found critical config '{path}' at {file_path}:{line_num}")
    
    def _detect_private_files(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测用户私密文件访问。"""
        for filename, metadata in self.USER_PRIVATE_FILES.items():
            if filename in line:
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "target_file": filename,
                    "level": metadata['level'],
                    "reason": metadata['reason'],
                    "content": line.strip(),
                    "type": "private_file"
                })
                logger.debug(f"Found private file '{filename}' at {file_path}:{line_num}")
    
    def _detect_log_operations(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测日志操作（删除、清空等）。"""
        for log_path, metadata in self.LOG_FILES.items():
            if log_path in line:
                # 检查是否包含删除操作
                if any(op in line.lower() for op in ['rm', 'truncate', 'clear', '>']):
                    findings.append({
                        "file": file_path,
                        "line": line_num,
                        "target_log": log_path,
                        "level": metadata['level'],
                        "reason": f"{metadata['reason']} - 日志操作",
                        "content": line.strip(),
                        "type": "log_operation"
                    })
                    logger.debug(f"Found log operation on '{log_path}' at {file_path}:{line_num}")
    
    def _detect_permission_changes(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测权限修改操作。"""
        for op, metadata in self.FILE_OPERATIONS.items():
            if op in line.lower():
                # 检查是否针对敏感路径
                for sensitive_path in list(self.SENSITIVE_SYSTEM_PATHS.keys()) + list(self.CRITICAL_CONFIG_FILES.keys()):
                    if sensitive_path in line:
                        findings.append({
                            "file": file_path,
                            "line": line_num,
                            "operation": op,
                            "target_path": sensitive_path,
                            "level": metadata['level'],
                            "operation_type": metadata['type'],
                            "content": line.strip(),
                            "type": "permission_change"
                        })
                        logger.debug(f"Found permission change '{op}' on '{sensitive_path}' at {file_path}:{line_num}")
    
    def _build_result(self, findings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """构建分析结果。"""
        all_findings = []
        severity_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_severity = 0
        
        # 合并所有发现
        for finding_list in findings.values():
            all_findings.extend(finding_list)
            for finding in finding_list:
                max_severity = max(
                    max_severity,
                    severity_levels.get(finding.get('level', 'low'), 0)
                )
        
        # 按严重性排序
        all_findings.sort(
            key=lambda x: severity_levels.get(x.get('level', 'low'), 0),
            reverse=True
        )
        
        # 确定风险等级
        severity_map = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low', 0: 'low'}
        level = severity_map.get(max_severity, 'low')
        
        if not all_findings:
            return {
                "title": "file permission check",
                "level": "low",
                "evidence": [],
                "summary": {
                    "total_findings": 0,
                    "sensitive_paths": 0,
                    "critical_configs": 0,
                    "private_files": 0,
                    "log_operations": 0,
                    "permission_changes": 0
                }
            }
        
        return {
            "title": "file permission and sensitive path analysis",
            "level": level,
            "evidence": all_findings,
            "summary": {
                "total_findings": len(all_findings),
                "sensitive_paths": len(findings.get("sensitive_paths", [])),
                "critical_configs": len(findings.get("critical_configs", [])),
                "private_files": len(findings.get("private_files", [])),
                "log_operations": len(findings.get("log_operations", [])),
                "permission_changes": len(findings.get("permission_changes", []))
            }
        }
