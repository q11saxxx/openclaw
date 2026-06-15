"""依赖分析器。

规则描述：
- 负责依赖文件、外部 URL、包源和潜在供应链链路识别。
- 为后续接入 SBOM/漏洞聚合预留能力。

扫描范围：
1. 依赖文件识别：requirements.txt、package.json、Gemfile、go.mod 等
2. 外部URL提取：HTTP/HTTPS URL、FTP 链接等
3. 包源识别：PyPI、npm、RubyGems、Maven 等官方源与第三方源
4. 供应链风险：包名相似度、源URL可信度、依赖版本锁定等
5. 下载链接分析：直接下载的二进制、脚本等
"""
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """依赖与供应链分析器。
    
    检测脚本和配置文件中的依赖声明和外部链接，
    识别潜在的供应链攻击、依赖冲突和不安全的包源。
    """
    
    # 依赖文件类型
    DEPENDENCY_FILES = {
        'requirements.txt': {'type': 'python', 'parser': 'parse_requirements'},
        'setup.py': {'type': 'python', 'parser': 'parse_setup_py'},
        'pyproject.toml': {'type': 'python', 'parser': 'parse_pyproject'},
        'Pipfile': {'type': 'python', 'parser': 'parse_pipfile'},
        'poetry.lock': {'type': 'python', 'parser': 'parse_poetry_lock'},
        'package.json': {'type': 'nodejs', 'parser': 'parse_package_json'},
        'yarn.lock': {'type': 'nodejs', 'parser': 'parse_yarn_lock'},
        'package-lock.json': {'type': 'nodejs', 'parser': 'parse_package_lock'},
        'pnpm-lock.yaml': {'type': 'nodejs', 'parser': 'parse_pnpm_lock'},
        'Gemfile': {'type': 'ruby', 'parser': 'parse_gemfile'},
        'Gemfile.lock': {'type': 'ruby', 'parser': 'parse_gemfile_lock'},
        'go.mod': {'type': 'golang', 'parser': 'parse_go_mod'},
        'go.sum': {'type': 'golang', 'parser': 'parse_go_sum'},
        'pom.xml': {'type': 'java', 'parser': 'parse_maven'},
        'build.gradle': {'type': 'java', 'parser': 'parse_gradle'},
    }
    
    # 官方包源
    OFFICIAL_SOURCES = {
        'https://pypi.org': 'PyPI',
        'https://registry.npmjs.org': 'npm',
        'https://rubygems.org': 'RubyGems',
        'https://proxy.golang.org': 'Go',
        'https://maven.apache.org': 'Maven Central',
        'https://repo.maven.apache.org': 'Maven Central',
    }
    
    # 可疑源或镜像
    SUSPICIOUS_SOURCES = {
        'http://': {'level': 'medium', 'reason': '非HTTPS source'},
        'localhost': {'level': 'high', 'reason': '本地源'},
        'file://': {'level': 'medium', 'reason': '本地文件源'},
    }
    
    # URL提取正则
    URL_PATTERN = r'https?://[^\s\'"}<>\[\]]*'
    
    # 包名可疑模式（可能是名称相似度攻击）
    SUSPICIOUS_PACKAGE_NAMES = [
        r'django.*s',  # django shadow packages
        r'requests.*s',
        r'numpy.*s',
        r'pandas.*s',
    ]

    # 支持代码引用检测的文件扩展名
    CODE_FILE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.rb', '.go', '.java', '.php', '.sh', '.bash'
    }

    # 常见代码语言导入/依赖引用模式
    LANGUAGE_IMPORT_PATTERNS = {
        'python': [
            (r'^\s*import\s+([a-zA-Z0-9_\.]+)', 'python_import'),
            (r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import', 'python_from_import'),
        ],
        'javascript': [
            (r'require\(\s*[\"\']([^\"\']+)[\"\']\s*\)', 'node_require'),
            (r'^\s*import\s+.*from\s+[\"\']([^\"\']+)[\"\']', 'node_import'),
            (r'^\s*import\s+[\"\']([^\"\']+)[\"\']', 'node_side_effect_import'),
        ],
        'ruby': [
            (r'^\s*require\s+[\"\']([^\"\']+)[\"\']', 'ruby_require'),
        ],
        'golang': [
            (r'^\s*import\s+[\"\']([^\"\']+)[\"\']', 'go_import'),
        ],
        'java': [
            (r'^\s*import\s+([a-zA-Z0-9_\.]+);', 'java_import'),
        ],
        'php': [
            (r'^\s*use\s+([a-zA-Z0-9_\\]+);', 'php_import'),
        ],
        'shell': [
            (r'^\s*source\s+[\"\']?([^\"\'\s]+)[\"\']?', 'shell_source'),
        ],
    }
    
    def analyze(self, path: str) -> Dict[str, Any]:
        """分析依赖与供应链风险。
        
        Args:
            path: skill路径，包含依赖配置文件
            
        Returns:
            包含分析结果的字典，格式为：
            {
                "title": str,          # 分析标题
                "level": str,             # 风险等级
                "dependencies": list,     # 发现的依赖项
                "external_urls": list,    # 发现的外部URL
                "code_references": list,  # 代码引用的第三方库
                "suspicious": list,       # 可疑项目
                "summary": dict           # 统计摘要
            }
        """
        logger.debug(f"Starting dependency analysis for path: {path}")
        
        dependencies = []
        external_urls = set()
        suspicious_items = []
        code_references = []
        
        try:
            # 查找所有文件
            files = self._find_all_files(path)
            logger.debug(f"Found {len(files)} files to analyze")
            
            for file_path in files:
                try:
                    content = self._read_file_safe(file_path)
                    if not content:
                        continue
                    
                    # 检查是否为依赖文件
                    filename = os.path.basename(file_path)
                    if filename in self.DEPENDENCY_FILES:
                        file_deps = self._parse_dependency_file(
                            file_path, filename, content
                        )
                        if file_deps:
                            dependencies.extend(file_deps)
                    
                    # 检测代码中的第三方库引用
                    if self._is_code_file(file_path):
                        refs = self._detect_code_references(file_path, content)
                        if refs:
                            code_references.extend(refs)
                    
                    # 提取所有URL
                    urls = self._extract_urls(content)
                    external_urls.update(urls)
                    
                    # 检测可疑项
                    suspicious = self._detect_suspicious_items(file_path, content)
                    if suspicious:
                        suspicious_items.extend(suspicious)
                except Exception as e:
                    logger.warning(f"Error analyzing file {file_path}: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error during dependency analysis: {str(e)}", exc_info=True)
            return {
                "title": "dependency analysis failed",
                "level": "low",
                "dependencies": [],
                "external_urls": [],
                "error": str(e)
            }
        
        return self._build_result(dependencies, external_urls, suspicious_items, code_references)
    
    def _find_all_files(self, path: str) -> List[str]:
        """递归查找所有文件。"""
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
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                    
                    for file in filenames:
                        file_path = os.path.join(root, file)
                        files.append(file_path)
        
        except Exception as e:
            logger.warning(f"Error finding files: {str(e)}")
        
        return files
    
    def _read_file_safe(self, path: str) -> str | None:
        """安全地读取文件内容。"""
        try:
            if os.path.getsize(path) > 5 * 1024 * 1024:
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _is_code_file(self, file_path: str) -> bool:
        """判断文件是否为代码文件。"""
        return Path(file_path).suffix.lower() in self.CODE_FILE_EXTENSIONS
    
    def _is_local_reference(self, module_name: str) -> bool:
        """判断导入是否为本地模块或相对引用。"""
        return module_name.startswith('.') or module_name.startswith('/')
    
    def _language_from_ext(self, extension: str) -> str:
        if extension in {'.py'}:
            return 'python'
        if extension in {'.js', '.jsx', '.ts', '.tsx'}:
            return 'javascript'
        if extension in {'.rb'}:
            return 'ruby'
        if extension in {'.go'}:
            return 'golang'
        if extension in {'.java'}:
            return 'java'
        if extension in {'.php'}:
            return 'php'
        if extension in {'.sh', '.bash'}:
            return 'shell'
        return 'unknown'
    
    def _detect_code_references(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """检测代码文件中的第三方库引用，并进行安全性评估。"""
        references = []
        extension = Path(file_path).suffix.lower()
        language = self._language_from_ext(extension)
        lines = content.splitlines()

        patterns = self.LANGUAGE_IMPORT_PATTERNS.get(language, [])
        if not patterns:
            return references

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            for pattern, import_type in patterns:
                match = re.search(pattern, stripped)
                if not match:
                    continue

                module_name = match.group(1).strip()
                if not module_name or self._is_local_reference(module_name):
                    continue

                ref = {
                    'file': file_path,
                    'line': line_num,
                    'module': module_name,
                    'import_type': import_type,
                    'language': language,
                }
                
                # 对第三方库进行安全检查
                security_check = self._check_library_security(module_name, language)
                ref['security_check'] = security_check
                
                references.append(ref)
                break

        return references
    
    def _check_library_security(self, module_name: str, language: str) -> Dict[str, Any]:
        """对第三方库进行安全性检查。"""
        security_issues = []
        risk_level = 'safe'
        
        # 1. 检测已知恶意或可疑包
        malicious = self._check_malicious_package(module_name)
        if malicious:
            security_issues.append(malicious)
            risk_level = 'critical'
        
        # 2. 检测包名相似度攻击 (typosquatting)
        typo_risk = self._check_typosquatting(module_name, language)
        if typo_risk:
            security_issues.append(typo_risk)
            if risk_level != 'critical':
                risk_level = 'high'
        
        # 3. 检测常见包的安全使用模式
        pattern_risk = self._check_dangerous_patterns(module_name)
        if pattern_risk:
            security_issues.append(pattern_risk)
            if risk_level == 'safe':
                risk_level = 'medium'
        
        return {
            'risk_level': risk_level,
            'issues': security_issues,
            'safe': risk_level == 'safe'
        }
    
    def _check_malicious_package(self, module_name: str) -> Dict[str, Any] | None:
        """检查已知恶意包列表。"""
        # 已知恶意包示例（在实际应用中应从外部数据源加载）
        known_malicious = {
            'event-stream': {
                'reason': '历史上存在供应链攻击',
                'level': 'critical'
            },
            'eslint-scope': {
                'reason': '曾被入侵，发布恶意版本',
                'level': 'critical'
            },
            'ua-parser-js': {
                'reason': '曾被入侵，发布恶意版本',
                'level': 'critical'
            },
        }
        
        if module_name.lower() in known_malicious:
            data = known_malicious[module_name.lower()]
            return {
                'type': 'malicious_package',
                'package': module_name,
                'level': data['level'],
                'reason': data['reason']
            }
        
        return None
    
    def _check_typosquatting(self, module_name: str, language: str) -> Dict[str, Any] | None:
        """检测包名相似度攻击（typosquatting）。"""
        # 常见的目标包及其常见拼写错误
        common_packages = {
            'python': {
                'requests': ['reqests', 'request', 'reqeust', 'requests-', 'request-'],
                'django': ['dajngo', 'djanog', 'django-'],
                'flask': ['flak', 'flask-'],
                'numpy': ['numpyy', 'numpy-'],
                'pandas': ['panda', 'pandas-'],
            },
            'javascript': {
                'react': ['reactjs', 'react-', 'reat'],
                'vue': ['vuejs', 'vue-', 'veu'],
                'express': ['expresss', 'express-', 'expres'],
                'lodash': ['lodashjs', 'lodash-', 'lodash_'],
                'axios': ['axiosjs', 'axios-'],
            }
        }
        
        target_packages = common_packages.get(language, {})
        
        for legitimate, suspicious_variants in target_packages.items():
            if module_name.lower() in suspicious_variants:
                return {
                    'type': 'typosquatting_risk',
                    'package': module_name,
                    'suggested_package': legitimate,
                    'level': 'high',
                    'reason': f'包名可能是 "{legitimate}" 的拼写错误'
                }
        
        return None
    
    def _check_dangerous_patterns(self, module_name: str) -> Dict[str, Any] | None:
        """检查危险的包名模式或命名约定。"""
        # 检查可疑的包名模式
        suspicious_patterns = [
            (r'^admin', 'admin类包名可能被滥用'),
            (r'^root', 'root类包名可能被滥用'),
            (r'^crypto.*steal', '包名包含可疑词汇'),
            (r'^payload', '包名包含恶意关键词'),
            (r'^backdoor', '包名包含恶意关键词'),
        ]
        
        for pattern, reason in suspicious_patterns:
            if re.search(pattern, module_name.lower()):
                return {
                    'type': 'suspicious_package_name',
                    'package': module_name,
                    'level': 'medium',
                    'reason': reason
                }
        
        return None
    
    def _parse_dependency_file(
        self,
        file_path: str,
        filename: str,
        content: str
    ) -> List[Dict[str, Any]]:
        """解析依赖文件。"""
        dependencies = []
        
        try:
            file_info = self.DEPENDENCY_FILES.get(filename, {})
            file_type = file_info.get('type', '')
            
            if file_type == 'python':
                dependencies = self._parse_python_deps(content)
            elif file_type == 'nodejs':
                dependencies = self._parse_nodejs_deps(content)
            elif file_type == 'ruby':
                dependencies = self._parse_ruby_deps(content)
            elif file_type == 'golang':
                dependencies = self._parse_golang_deps(content)
            elif file_type == 'java':
                dependencies = self._parse_java_deps(content)
            
            # 添加文件来源信息
            for dep in dependencies:
                dep['source_file'] = file_path
            
            logger.debug(f"Parsed {len(dependencies)} dependencies from {filename}")
        
        except Exception as e:
            logger.warning(f"Error parsing dependency file {filename}: {str(e)}")
        
        return dependencies
    
    def _parse_python_deps(self, content: str) -> List[Dict[str, Any]]:
        """解析Python依赖。"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 移除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            
            # 解析包名和版本
            if line:
                # 处理URL格式
                if line.startswith('git+') or line.startswith('http'):
                    dependencies.append({
                        'package': line,
                        'type': 'url',
                        'language': 'python'
                    })
                else:
                    # 标准格式：package==version, package>=version 等
                    match = re.match(r'([a-zA-Z0-9_\-]+)', line)
                    if match:
                        package_name = match.group(1)
                        dependencies.append({
                            'package': package_name,
                            'spec': line,
                            'type': 'package',
                            'language': 'python'
                        })
        
        return dependencies
    
    def _parse_nodejs_deps(self, content: str) -> List[Dict[str, Any]]:
        """解析Node.js依赖。"""
        dependencies = []
        
        try:
            import json
            data = json.loads(content)
            
            # 处理 package.json
            if 'dependencies' in data:
                for pkg_name, version in data['dependencies'].items():
                    dependencies.append({
                        'package': pkg_name,
                        'version': version,
                        'type': 'dependency',
                        'language': 'nodejs'
                    })
            
            if 'devDependencies' in data:
                for pkg_name, version in data['devDependencies'].items():
                    dependencies.append({
                        'package': pkg_name,
                        'version': version,
                        'type': 'dev',
                        'language': 'nodejs'
                    })
        
        except Exception:
            # 对于lock文件，进行简单的模式匹配
            matches = re.findall(r'"([a-zA-Z0-9_@\-/]+)":\s*{', content)
            for match in matches:
                dependencies.append({
                    'package': match,
                    'type': 'package',
                    'language': 'nodejs'
                })
        
        return dependencies
    
    def _parse_ruby_deps(self, content: str) -> List[Dict[str, Any]]:
        """解析Ruby依赖。"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # gem "package_name" 格式
            match = re.match(r'gem\s+[\'"]([a-zA-Z0-9_\-]+)[\'"]', line)
            if match:
                dependencies.append({
                    'package': match.group(1),
                    'type': 'gem',
                    'language': 'ruby'
                })
        
        return dependencies
    
    def _parse_golang_deps(self, content: str) -> List[Dict[str, Any]]:
        """解析Go依赖。"""
        dependencies = []
        lines = content.split('\n')
        
        in_require = False
        for line in lines:
            line = line.strip()
            
            if line == 'require (':
                in_require = True
                continue
            elif in_require and line == ')':
                in_require = False
                continue
            
            if in_require or line.startswith('require '):
                # 解析require行
                match = re.match(r'require\s+([^\s]+)\s+([^\s]+)', line)
                if match:
                    dependencies.append({
                        'package': match.group(1),
                        'version': match.group(2),
                        'type': 'module',
                        'language': 'golang'
                    })
        
        return dependencies
    
    def _parse_java_deps(self, content: str) -> List[Dict[str, Any]]:
        """解析Java依赖。"""
        dependencies = []
        
        # 简单的XML/Gradle 解析
        # groupId:artifactId:version 格式
        matches = re.findall(
            r'<artifactId>([^<]+)</artifactId>\s*(?:<version>([^<]+)</version>)?',
            content
        )
        
        for match in matches:
            dependencies.append({
                'package': match[0],
                'version': match[1] if match[1] else 'unknown',
                'type': 'artifact',
                'language': 'java'
            })
        
        return dependencies
    
    def _extract_urls(self, content: str) -> Set[str]:
        """提取所有URL。"""
        urls = set()
        
        matches = re.findall(self.URL_PATTERN, content)
        for url in matches:
            # 过滤掉过长的URL（可能是false positive）
            if len(url) < 500:
                urls.add(url)
        
        return urls
    
    def _detect_suspicious_items(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """检测可疑项。"""
        suspicious = []
        
        # 检测可疑源
        for url in re.findall(self.URL_PATTERN, content):
            for pattern, metadata in self.SUSPICIOUS_SOURCES.items():
                if pattern in url:
                    suspicious.append({
                        'file': file_path,
                        'item': url,
                        'type': 'suspicious_source',
                        'level': metadata['level'],
                        'reason': metadata['reason']
                    })
                    logger.debug(f"Found suspicious source: {url}")
        
        # 检测可疑包名（名称相似度攻击）
        for pattern in self.SUSPICIOUS_PACKAGE_NAMES:
            if re.search(pattern, content, re.IGNORECASE):
                suspicious.append({
                    'file': file_path,
                    'pattern': pattern,
                    'type': 'suspicious_package',
                    'level': 'medium',
                    'reason': '可能的包名相似度攻击'
                })
                logger.debug(f"Found suspicious package pattern: {pattern}")
        
        return suspicious
    
    def _build_result(
        self,
        dependencies: List[Dict[str, Any]],
        external_urls: Set[str],
        suspicious_items: List[Dict[str, Any]],
        code_references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建分析结果。"""
        # 确定风险等级
        severity_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_severity = 0
        
        for item in suspicious_items:
            max_severity = max(
                max_severity,
                severity_levels.get(item.get('level', 'low'), 0)
            )
        
        severity_map = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low', 0: 'low'}
        level = severity_map.get(max_severity, 'low')
        
        # 如果没有依赖和URL，返回低风险
        if not dependencies and not external_urls and not code_references:
            level = 'low'
        
        return {
            "title": "dependency and supply chain analysis",
            "level": level,
            "dependencies": dependencies,
            "external_urls": list(external_urls),
            "code_references": code_references,
            "suspicious": suspicious_items,
            "summary": {
                "total_dependencies": len(dependencies),
                "unique_urls": len(external_urls),
                "code_reference_count": len(code_references),
                "suspicious_items": len(suspicious_items),
                "high_risk_items": len([x for x in suspicious_items if x.get('level') in ['high', 'critical']])
            }
        }
