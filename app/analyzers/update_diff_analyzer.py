"""版本差异分析器。

规则描述：
- 用于识别“先建立信任再投毒”的更新风险。
- 后续可接入 git diff、包版本对比、规则偏移分析。

扫描范围：
1. 版本变更检测：依赖版本升降、包源变更等
2. 文件差异分析：新增/删除/修改的危险文件
3. 行为变化：权限提升、网络操作的新增等
4. 内容偏移：代码混淆程度、文件大小异常等
5. 可疑更新：频繁小版本更新、构建脚本变化等
"""
import logging
import os
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class UpdateDiffAnalyzer:
    """版本差异与投毒风险分析器。
    
    对比版本之间的差异，识别"先建立信任再投毒"的攻击模式，
    检测版本更新中的恶意变化。
    """
    
    # 可疑的新增文件
    SUSPICIOUS_NEW_FILES = {
        'setup.py': {'level': 'high', 'reason': '新增安装脚本'},
        'conftest.py': {'level': 'high', 'reason': '新增测试配置'},
        'install.sh': {'level': 'high', 'reason': '新增安装脚本'},
        '.hidden': {'level': 'high', 'reason': '新增隐藏文件'},
        'requirements.txt': {'level': 'medium', 'reason': '新增依赖声明'},
    }
    
    # 危险的文件修改
    DANGEROUS_FILE_MODIFICATIONS = {
        '__init__.py': {'level': 'high', 'reason': '包初始化文件修改'},
        'main.py': {'level': 'high', 'reason': '主程序文件修改'},
        'setup.py': {'level': 'high', 'reason': '安装脚本修改'},
        '.gitignore': {'level': 'medium', 'reason': '隐藏规则变化'},
        'Dockerfile': {'level': 'high', 'reason': '容器配置修改'},
        'docker-compose.yml': {'level': 'high', 'reason': '容器编排配置修改'},
    }
    
    # 可疑的文件删除
    SUSPICIOUS_DELETIONS = {
        'TEST': {'level': 'medium', 'reason': '测试文件删除'},
        'README': {'level': 'medium', 'reason': '文档删除'},
        'LICENSE': {'level': 'low', 'reason': '许可证删除'},
        '.github': {'level': 'medium', 'reason': 'GitHub配置删除'},
    }
    
    # 可疑的版本号模式
    SUSPICIOUS_VERSION_PATTERNS = {
        r'0\.0\..*': {'level': 'high', 'reason': '0.0.x版本'},
        r'\d+\.\d+\.999': {'level': 'high', 'reason': '异常版本号'},
        r'.*-dev.*': {'level': 'medium', 'reason': '开发版本'},
        r'.*-pre.*': {'level': 'medium', 'reason': '预发布版本'},
    }
    
    # 可疑的大小变化阈值
    SIZE_CHANGE_THRESHOLD = 0.5  # 50% 变化被认为是可疑的
    
    def analyze(self, path: str) -> Dict[str, Any]:
        """分析版本差异与投毒风险。
        
        Args:
            path: skill路径，包含版本文件或配置
            
        Returns:
            包含分析结果的字典，格式为：
            {
                "title": str,              # 分析标题
                "level": str,              # 风险等级
                "changed_files": list,     # 变更的文件
                "suspicious_delta": bool,  # 是否有可疑变化
                "evidence": list           # 具体证据项
            }
        """
        logger.debug(f"Starting update diff analysis for path: {path}")
        
        findings = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "version_changes": [],
            "size_anomalies": [],
        }
        
        try:
            # 扫描文件系统
            file_stats = self._analyze_file_structure(path)
            
            # 检测各类风险
            self._detect_suspicious_new_files(file_stats.get("files", []), findings["new_files"])
            self._detect_suspicious_modifications(file_stats.get("files", []), findings["modified_files"])
            self._detect_version_anomalies(path, findings["version_changes"])
            self._detect_size_anomalies(file_stats.get("files", []), findings["size_anomalies"])
            
            return self._build_result(findings)
        
        except Exception as e:
            logger.error(f"Error during update diff analysis: {str(e)}", exc_info=True)
            return {
                "title": "update diff analysis failed",
                "level": "low",
                "changed_files": [],
                "suspicious_delta": False,
                "error": str(e)
            }
    
    def _analyze_file_structure(self, path: str) -> Dict[str, Any]:
        """分析文件结构。"""
        file_stats = {
            "files": [],
            "total_size": 0,
        }
        
        try:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                return file_stats
            
            if os.path.isfile(path):
                # 单个文件
                file_stats["files"].append(self._get_file_info(path))
                file_stats["total_size"] = os.path.getsize(path)
            else:
                # 目录遍历
                for root, dirs, files in os.walk(path):
                    # 跳过隐藏目录
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.git']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_info = self._get_file_info(file_path)
                            if file_info:
                                file_stats["files"].append(file_info)
                                file_stats["total_size"] += file_info.get('size', 0)
                        except Exception:
                            continue
        
        except Exception as e:
            logger.warning(f"Error analyzing file structure: {str(e)}")
        
        return file_stats
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any] | None:
        """获取文件信息。"""
        try:
            stat = os.stat(file_path)
            
            # 计算文件哈希（用于完整性检查）
            file_hash = None
            try:
                if stat.st_size < 10 * 1024 * 1024:  # 仅对小于10MB的文件计算
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
            except Exception:
                pass
            
            return {
                'path': file_path,
                'relative_path': os.path.relpath(file_path),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'hash': file_hash,
                'is_executable': os.access(file_path, os.X_OK),
            }
        except Exception as e:
            logger.debug(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def _detect_suspicious_new_files(
        self,
        files: List[Dict[str, Any]],
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测可疑的新增文件。"""
        for file_info in files:
            relative_path = file_info.get('relative_path', '')
            filename = os.path.basename(relative_path)
            
            # 检查可疑的新增文件模式
            for suspicious_name, metadata in self.SUSPICIOUS_NEW_FILES.items():
                if suspicious_name in filename.lower():
                    findings.append({
                        'file': relative_path,
                        'filename': filename,
                        'type': 'new_file',
                        'level': metadata['level'],
                        'reason': metadata['reason'],
                        'size': file_info.get('size', 0)
                    })
                    logger.debug(f"Found suspicious new file: {filename}")
            
            # 检查隐藏文件
            if filename.startswith('.') and filename not in ['.gitignore', '.github']:
                findings.append({
                    'file': relative_path,
                    'filename': filename,
                    'type': 'hidden_file',
                    'level': 'medium',
                    'reason': '隐藏文件',
                    'size': file_info.get('size', 0)
                })
    
    def _detect_suspicious_modifications(
        self,
        files: List[Dict[str, Any]],
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测可疑的文件修改。"""
        for file_info in files:
            relative_path = file_info.get('relative_path', '')
            filename = os.path.basename(relative_path)
            
            # 检查文件是否是危险的修改对象
            for danger_file, metadata in self.DANGEROUS_FILE_MODIFICATIONS.items():
                if filename == danger_file or relative_path.endswith(danger_file):
                    findings.append({
                        'file': relative_path,
                        'filename': filename,
                        'type': 'modified_dangerous_file',
                        'level': metadata['level'],
                        'reason': metadata['reason'],
                        'is_executable': file_info.get('is_executable', False)
                    })
                    logger.debug(f"Found suspicious modification: {filename}")
            
            # 检查可执行文件
            if file_info.get('is_executable'):
                findings.append({
                    'file': relative_path,
                    'filename': filename,
                    'type': 'executable_file',
                    'level': 'medium',
                    'reason': '可执行文件',
                })
    
    def _detect_version_anomalies(
        self,
        path: str,
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测版本号异常。"""
        version_files = [
            'version', 'VERSION', 'version.txt',
            'package.json', 'setup.py', 'pyproject.toml'
        ]
        
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file in version_files:
                        file_path = os.path.join(root, file)
                        content = self._read_file_safe(file_path)
                        if content:
                            versions = self._extract_versions(content)
                            for version in versions:
                                if self._is_suspicious_version(version):
                                    findings.append({
                                        'file': os.path.relpath(file_path),
                                        'version': version,
                                        'type': 'suspicious_version',
                                        'level': 'high',
                                        'reason': '异常版本号'
                                    })
                                    logger.debug(f"Found suspicious version: {version}")
        
        except Exception as e:
            logger.debug(f"Error detecting version anomalies: {str(e)}")
    
    def _extract_versions(self, content: str) -> List[str]:
        """从内容中提取版本号。"""
        import re
        versions = []
        
        # 常见的版本号模式
        patterns = [
            r'"version":\s*"([0-9.]+)"',
            r'version\s*=\s*["\']([0-9.]+)["\']',
            r'__version__\s*=\s*["\']([0-9.]+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            versions.extend(matches)
        
        return versions
    
    def _is_suspicious_version(self, version: str) -> bool:
        """检查版本号是否异常。"""
        import re
        
        for pattern in self.SUSPICIOUS_VERSION_PATTERNS:
            if re.match(pattern, version):
                return True
        
        return False
    
    def _detect_size_anomalies(
        self,
        files: List[Dict[str, Any]],
        findings: List[Dict[str, Any]]
    ) -> None:
        """检测文件大小异常。"""
        # 计算平均文件大小
        if not files:
            return
        
        total_size = sum(f.get('size', 0) for f in files)
        avg_size = total_size / len(files) if files else 0
        
        # 查找大小异常的文件
        for file_info in files:
            size = file_info.get('size', 0)
            filename = os.path.basename(file_info.get('relative_path', ''))
            
            # 跳过已知的大文件
            if filename.endswith(('.zip', '.tar', '.gz', '.whl', '.jar')):
                continue
            
            # 检查是否是已知的脚本文件但文件过大
            if filename.endswith(('.py', '.sh', '.js', '.rb')):
                if size > 1 * 1024 * 1024:  # 超过1MB
                    findings.append({
                        'file': file_info.get('relative_path'),
                        'filename': filename,
                        'type': 'size_anomaly',
                        'level': 'medium',
                        'reason': f'脚本文件过大 ({size / 1024:.1f}KB)',
                        'size': size
                    })
                    logger.debug(f"Found size anomaly: {filename} ({size / 1024:.1f}KB)")
    
    def _read_file_safe(self, path: str) -> str | None:
        """安全地读取文件内容。"""
        try:
            if os.path.getsize(path) > 5 * 1024 * 1024:
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _build_result(self, findings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """构建分析结果。"""
        all_findings = []
        severity_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_severity = 0
        suspicious_delta = False
        
        # 合并所有发现
        for finding_list in findings.values():
            all_findings.extend(finding_list)
            if finding_list:
                suspicious_delta = True
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
                "title": "version diff analysis",
                "level": "low",
                "changed_files": [],
                "suspicious_delta": False,
                "evidence": [],
                "summary": {
                    "total_findings": 0,
                    "new_files": 0,
                    "modified_files": 0,
                    "version_anomalies": 0,
                    "size_anomalies": 0
                }
            }
        
        return {
            "title": "version and update diff analysis",
            "level": level,
            "changed_files": [f.get('file') for f in all_findings],
            "suspicious_delta": suspicious_delta,
            "evidence": all_findings,
            "summary": {
                "total_findings": len(all_findings),
                "new_files": len(findings.get("new_files", [])),
                "modified_files": len(findings.get("modified_files", [])),
                "version_anomalies": len(findings.get("version_changes", [])),
                "size_anomalies": len(findings.get("size_anomalies", []))
            }
        }
