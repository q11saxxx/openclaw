"""脚本分析器。

规则描述：
- 负责扫描脚本中的危险命令、下载执行链、持久化行为等模式。
- 尽量输出可定位到文件/行号的证据。

扫描范围：
1. 危险命令：eval、exec、system、rm -rf、dd 等
2. 下载执行链：curl|bash、wget和管道执行、base64解码执行等
3. 持久化行为：cron、systemd、rc.local、sudoers 修改等
4. 敏感操作：chmod 777、chown root、iptables、nc 反向shell等
5. 混淆代码：base64、hex、rot13 编码执行等
"""
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import tempfile

logger = logging.getLogger(__name__)


class ScriptAnalyzer:
    """静态脚本安全分析器。
    
    对脚本文件进行深度扫描，识别潜在的安全风险，包括危险命令、
    下载执行链、持久化行为等恶意或可疑的代码模式。
    """
    
    # 危险命令检测规则
    DANGEROUS_COMMANDS = {
        # 代码执行
        r'\beval\s*\(': {'name': 'eval', 'severity': 'critical'},
        r'\bexec\s*\(': {'name': 'exec', 'severity': 'critical'},
        r'\bsystem\s*\(': {'name': 'system', 'severity': 'high'},
        r'\bpopen\s*\(': {'name': 'popen', 'severity': 'high'},
        r'\bsubprocess': {'name': 'subprocess', 'severity': 'medium'},
        r'\bos\.system': {'name': 'os.system', 'severity': 'high'},
        r'\bShell=True': {'name': 'Shell=True', 'severity': 'high'},
        # 文件系统危险操作
        r'rm\s+-rf\s+/': {'name': 'rm -rf /', 'severity': 'critical'},
        r'dd\s+if=/dev': {'name': 'dd 写入设备', 'severity': 'critical'},
        r'chmod\s+777': {'name': 'chmod 777', 'severity': 'high'},
        r'chown\s+.*root': {'name': 'chown to root', 'severity': 'high'},
        # 目录遍历与删除
        r'rm\s+-rf\s+\*': {'name': 'rm -rf *', 'severity': 'high'},
        r'rm\s+-rf\s+\.': {'name': 'rm -rf .', 'severity': 'high'},
    }
    
    # 下载执行链检测规则
    DOWNLOAD_EXECUTE_PATTERNS = {
        # curl/wget + bash
        r'curl\s+.*\|.*bash': {'name': 'curl|bash', 'severity': 'critical'},
        r'wget\s+.*\|.*bash': {'name': 'wget|bash', 'severity': 'critical'},
        r'curl\s+.*\|.*sh': {'name': 'curl|sh', 'severity': 'critical'},
        r'wget\s+.*\|.*sh': {'name': 'wget|sh', 'severity': 'critical'},
        # base64 编码执行
        r'base64.*-d.*\|.*bash': {'name': 'base64|bash', 'severity': 'critical'},
        r'base64.*-d.*\|.*sh': {'name': 'base64|sh', 'severity': 'critical'},
        # 远程脚本加载
        r'source\s+<\(.*curl': {'name': 'source <(curl)', 'severity': 'critical'},
        r'source\s+<\(.*wget': {'name': 'source <(wget)', 'severity': 'critical'},
        # Python 特定的远程执行
        r'requests\.get.*eval': {'name': 'requests.get + eval', 'severity': 'critical'},
        r'urllib.*eval': {'name': 'urllib + eval', 'severity': 'critical'},
    }
    
    # 持久化行为检测规则
    PERSISTENCE_PATTERNS = {
        r'crontab\s+-e': {'name': 'crontab edit', 'severity': 'high'},
        r'\*/[0-9]+\s+\*\s+\*\s+\*\s+\*': {'name': 'cron job', 'severity': 'high'},
        r'@.*\s+/[a-zA-Z]': {'name': 'cron special', 'severity': 'high'},
        r'/etc/rc\.local': {'name': 'rc.local modification', 'severity': 'high'},
        r'systemctl\s+enable': {'name': 'systemd enable', 'severity': 'high'},
        r'/etc/systemd': {'name': 'systemd service', 'severity': 'high'},
        r'/etc/sudoers': {'name': 'sudoers modification', 'severity': 'critical'},
        r'sudo\s+.*NOPASSWD': {'name': 'sudoers NOPASSWD', 'severity': 'critical'},
        r'\.ssh/authorized_keys': {'name': 'SSH key injection', 'severity': 'high'},
        r'\.bashrc|\.bash_profile': {'name': 'shell rc modification', 'severity': 'medium'},
    }
    
    # 网络与反向壳检测规则
    NETWORK_PATTERNS = {
        r'nc\s+-.*-e.*sh': {'name': 'nc reverse shell', 'severity': 'critical'},
        r'bash\s+-i\s+>.*&1': {'name': 'bash reverse shell', 'severity': 'critical'},
        r'python\s+-c.*socket': {'name': 'python socket backdoor', 'severity': 'critical'},
        r'iptables\s+-': {'name': 'iptables modification', 'severity': 'high'},
        r'firewall-cmd': {'name': 'firewall modification', 'severity': 'high'},
        r'/dev/tcp/': {'name': '/dev/tcp connection', 'severity': 'high'},
    }
    
    # 混淆代码检测规则
    OBFUSCATION_PATTERNS = {
        r'base64\s+-d': {'name': 'base64 decode', 'severity': 'medium'},
        r'echo\s+.*\|.*base64': {'name': 'echo | base64', 'severity': 'medium'},
        r'xxd\s+-r': {'name': 'xxd decode', 'severity': 'medium'},
        r'od\s+-A': {'name': 'od decode', 'severity': 'medium'},
        r'\$\(.*base64': {'name': 'subshell base64', 'severity': 'medium'},
    }
    
    # 支持的脚本扩展名
    SCRIPT_EXTENSIONS = {'.sh', '.py', '.rb', '.pl', '.js', '.bash', '.ksh', '.zsh', '.php'}
    
    def analyze(self, path: str) -> Dict[str, Any]:
        """分析脚本文件中的安全风险。
        
        Args:
            path: skill路径，包含待分析的脚本文件
            
        Returns:
            包含分析结果的字典，格式为：
            {
                "title": str,           # 分析标题
                "level": str,           # 风险等级：critical/high/medium/low
                "evidence": list,       # 发现的证据列表，包含file/line/pattern/content等
                "summary": dict         # 统计摘要：危险命令数、下载链数等
            }
        """
        logger.debug(f"Starting script analysis for path: {path}")
        
        findings = {
            "dangerous_commands": [],
            "download_execute_chains": [],
            "persistence_behaviors": [],
            "network_operations": [],
            "obfuscation_code": [],
        }
        
        try:
            # 递归扫描路径中的所有脚本文件
            script_files = self._find_script_files(path)
            logger.debug(f"Found {len(script_files)} script files")
            
            for script_path in script_files:
                try:
                    content = self._read_file_safe(script_path)
                    if not content:
                        continue
                    
                    # 逐行分析
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        # 跳过注释行和空行
                        if self._is_comment_or_empty(line):
                            continue
                        
                        # 检测各类危险模式
                        self._detect_dangerous_commands(
                            line, line_num, script_path,
                            findings["dangerous_commands"]
                        )
                        self._detect_download_execute_chains(
                            line, line_num, script_path,
                            findings["download_execute_chains"]
                        )
                        self._detect_persistence_behaviors(
                            line, line_num, script_path,
                            findings["persistence_behaviors"]
                        )
                        self._detect_network_operations(
                            line, line_num, script_path,
                            findings["network_operations"]
                        )
                        self._detect_obfuscation(
                            line, line_num, script_path,
                            findings["obfuscation_code"]
                        )
                
                except Exception as e:
                    logger.warning(f"Error analyzing file {script_path}: {str(e)}")
                    continue
            
            # 构建返回结果
            return self._build_result(findings)
        
        except Exception as e:
            logger.error(f"Error during script analysis: {str(e)}", exc_info=True)
            return {
                "title": "script analysis failed",
                "level": "low",
                "evidence": [],
                "error": str(e)
            }
    
    def _find_script_files(self, path: str) -> List[str]:
        """递归查找目录中的所有脚本文件。
        
        Args:
            path: 目录路径
            
        Returns:
            脚本文件路径列表
        """
        script_files = []
        
        try:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                return script_files
            
            if os.path.isfile(path):
                # 如果是单个文件，直接检查
                if self._is_script_file(path):
                    script_files.append(path)
            else:
                # 递归遍历目录
                for root, dirs, files in os.walk(path):
                    # 跳过隐藏目录和常见的非脚本目录
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._is_script_file(file_path):
                            script_files.append(file_path)
        
        except Exception as e:
            logger.warning(f"Error finding script files: {str(e)}")
        
        return script_files
    
    def _is_script_file(self, path: str) -> bool:
        """检查文件是否为脚本文件。
        
        Args:
            path: 文件路径
            
        Returns:
            True 如果是脚本文件，False 否则
        """
        # 检查扩展名
        ext = Path(path).suffix.lower()
        if ext in self.SCRIPT_EXTENSIONS:
            return True
        
        # 检查 shebang
        try:
            with open(path, 'rb') as f:
                first_line = f.readline().decode('utf-8', errors='ignore')
                if first_line.startswith('#!'):
                    return True
        except Exception:
            pass
        
        return False
    
    def _read_file_safe(self, path: str) -> str | None:
        """安全地读取文件内容。
        
        Args:
            path: 文件路径
            
        Returns:
            文件内容，或 None 如果读取失败
        """
        try:
            # 限制文件大小（10MB）
            max_size = 10 * 1024 * 1024
            if os.path.getsize(path) > max_size:
                logger.warning(f"File too large, skipping: {path}")
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.debug(f"Error reading file {path}: {str(e)}")
            return None
    
    def _is_comment_or_empty(self, line: str) -> bool:
        """检查行是否为注释或空行。
        
        Args:
            line: 代码行
            
        Returns:
            True 如果是注释或空行，False 否则
        """
        stripped = line.strip()
        return not stripped or stripped.startswith('#') or stripped.startswith('//')
    
    def _detect_dangerous_commands(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测危险命令。"""
        for pattern, metadata in self.DANGEROUS_COMMANDS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "pattern": metadata['name'],
                    "severity": metadata['severity'],
                    "content": line.strip(),
                    "type": "dangerous_command"
                })
                logger.debug(f"Found dangerous command '{metadata['name']}' at {file_path}:{line_num}")
    
    def _detect_download_execute_chains(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测下载执行链模式。"""
        for pattern, metadata in self.DOWNLOAD_EXECUTE_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "pattern": metadata['name'],
                    "severity": metadata['severity'],
                    "content": line.strip(),
                    "type": "download_execute"
                })
                logger.debug(f"Found download-execute pattern '{metadata['name']}' at {file_path}:{line_num}")
    
    def _detect_persistence_behaviors(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测持久化行为。"""
        for pattern, metadata in self.PERSISTENCE_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "pattern": metadata['name'],
                    "severity": metadata['severity'],
                    "content": line.strip(),
                    "type": "persistence"
                })
                logger.debug(f"Found persistence pattern '{metadata['name']}' at {file_path}:{line_num}")
    
    def _detect_network_operations(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测网络与反向壳操作。"""
        for pattern, metadata in self.NETWORK_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "pattern": metadata['name'],
                    "severity": metadata['severity'],
                    "content": line.strip(),
                    "type": "network_operation"
                })
                logger.debug(f"Found network pattern '{metadata['name']}' at {file_path}:{line_num}")
    
    def _detect_obfuscation(
        self,
        line: str,
        line_num: int,
        file_path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测混淆代码。"""
        for pattern, metadata in self.OBFUSCATION_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": file_path,
                    "line": line_num,
                    "pattern": metadata['name'],
                    "severity": metadata['severity'],
                    "content": line.strip(),
                    "type": "obfuscation"
                })
                logger.debug(f"Found obfuscation pattern '{metadata['name']}' at {file_path}:{line_num}")
    
    def _build_result(self, findings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """构建分析结果。
        
        Args:
            findings: 各类发现的字典
            
        Returns:
            结构化的分析结果
        """
        all_findings = []
        severity_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_severity = 0
        
        # 合并所有发现
        for finding_list in findings.values():
            all_findings.extend(finding_list)
            for finding in finding_list:
                max_severity = max(
                    max_severity,
                    severity_levels.get(finding.get('severity', 'low'), 0)
                )
        
        # 按严重性排序
        all_findings.sort(
            key=lambda x: severity_levels.get(x.get('severity', 'low'), 0),
            reverse=True
        )
        
        # 确定风险等级
        severity_map = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low', 0: 'low'}
        level = severity_map.get(max_severity, 'low')
        
        # 如果没有发现，返回低风险
        if not all_findings:
            return {
                "title": "script analysis",
                "level": "low",
                "evidence": [],
                "summary": {
                    "total_findings": 0,
                    "dangerous_commands": 0,
                    "download_execute_chains": 0,
                    "persistence_behaviors": 0,
                    "network_operations": 0,
                    "obfuscation_code": 0
                }
            }
        
        return {
            "title": "static script analysis",
            "level": level,
            "evidence": all_findings,
            "summary": {
                "total_findings": len(all_findings),
                "dangerous_commands": len(findings.get("dangerous_commands", [])),
                "download_execute_chains": len(findings.get("download_execute_chains", [])),
                "persistence_behaviors": len(findings.get("persistence_behaviors", [])),
                "network_operations": len(findings.get("network_operations", [])),
                "obfuscation_code": len(findings.get("obfuscation_code", []))
            }
        }
