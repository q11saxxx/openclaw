"""规则引擎。

规则描述：
- 规则统一从 builtin/ 和 custom/ 目录加载。
- 规则引擎只负责匹配与输出，不直接做最终风险裁决。
- 支持多种规则类型：危险命令、敏感路径、可疑网络、提示词风险等。
- 返回统一格式的发现结果：{title, level, evidence, summary}
"""
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional
import yaml

logger = logging.getLogger(__name__)


class RuleEngine:
    """规则引擎 - 负责规则加载、匹配与输出。
    
    规则加载流程：
    1. 从 builtin/ 和 custom/ 目录加载 YAML 规则文件
    2. 支持规则热加载和动态更新
    
    规则匹配流程：
    1. 遍历目标路径下的所有文件
    2. 读取文件内容，逐行与规则pattern比对
    3. 返回匹配结果，包含规则ID、标题、风险等级、证据
    
    规则格式（YAML）：
    ```yaml
    rules:
      - id: rule-id
        title: 规则标题
        pattern: 匹配模式
        level: high  # low/medium/high/critical
    ```
    """

    def __init__(self):
        """初始化规则引擎，加载所有规则。"""
        self.rules = []
        self._load_rules()
        logger.debug(f"Initialized RuleEngine with {len(self.rules)} rules")

    def _load_rules(self) -> None:
        """从 builtin/ 和 custom/ 目录加载所有规则。
        
        按加载顺序：
        1. builtin/ - 内置规则
        2. custom/ - 自定义规则（优先级更高，可覆盖内置规则）
        """
        rules_dir = Path(__file__).parent
        
        # 加载内置规则
        builtin_rules = self._load_rules_from_directory(
            rules_dir / "builtin",
            "builtin"
        )
        
        # 加载自定义规则
        custom_rules = self._load_rules_from_directory(
            rules_dir / "custom",
            "custom"
        )
        
        # 合并规则，自定义规则优先级更高
        self.rules = builtin_rules + custom_rules
        
        logger.info(
            f"Loaded {len(builtin_rules)} builtin rules "
            f"and {len(custom_rules)} custom rules"
        )

    def _load_rules_from_directory(
        self,
        directory: Path,
        rule_type: str
    ) -> list[dict[str, Any]]:
        """从指定目录加载 YAML 规则文件。
        
        Args:
            directory: 规则目录路径
            rule_type: 规则类型标识（builtin/custom）
            
        Returns:
            规则列表
        """
        rules = []
        
        if not directory.exists():
            logger.warning(f"Rules directory not found: {directory}")
            return rules
        
        # 遍历所有 YAML 文件
        for yaml_file in directory.glob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                
                if content and "rules" in content:
                    for rule in content["rules"]:
                        # 验证规则格式
                        if self._validate_rule(rule):
                            # 添加规则来源信息
                            rule["_source"] = f"{rule_type}/{yaml_file.name}"
                            rules.append(rule)
                        else:
                            logger.warning(
                                f"Invalid rule format in {yaml_file}: {rule}"
                            )
                
            except Exception as e:
                logger.warning(
                    f"Failed to load rules from {yaml_file}: {str(e)}"
                )
        
        return rules

    def _validate_rule(self, rule: dict) -> bool:
        """验证规则格式是否正确。
        
        必要字段：id, title, pattern, level
        
        Args:
            rule: 规则字典
            
        Returns:
            True 如果规则有效，False 否则
        """
        required_fields = {"id", "title", "pattern", "level"}
        if not all(field in rule for field in required_fields):
            return False
        
        # 验证 level 的值
        valid_levels = {"low", "medium", "high", "critical"}
        if rule["level"] not in valid_levels:
            return False
        
        return True

    def scan(self, path: str) -> list[dict[str, Any]]:
        """扫描给定路径，返回所有规则匹配的发现。
        
        扫描流程：
        1. 遍历目标路径下的所有文件
        2. 对每个文件应用所有规则
        3. 返回匹配的规则及其证据
        
        Args:
            path: 要扫描的路径（文件或目录）
            
        Returns:
            发现结果列表，每个发现包含：
            - title: 规则标题
            - level: 风险等级
            - evidence: 匹配证据（文件路径:行号:匹配内容）
            - summary: 简要说明
            - rule_id: 触发的规则ID
        """
        findings = []
        matched_rules = set()  # 避免重复报告相同规则
        
        try:
            # 获取要扫描的文件列表
            files_to_scan = self._get_files_to_scan(path)
            logger.debug(f"Found {len(files_to_scan)} files to scan")
            
            # 对每个文件应用规则
            for file_path in files_to_scan:
                try:
                    file_findings = self._scan_file(file_path)
                    findings.extend(file_findings)
                    
                    # 记录已匹配的规则（避免重复报告）
                    for finding in file_findings:
                        matched_rules.add(finding.get("rule_id"))
                
                except Exception as e:
                    logger.debug(
                        f"Error scanning file {file_path}: {str(e)}"
                    )
        
        except Exception as e:
            logger.error(f"Unexpected error during rule scanning: {str(e)}")
        
        logger.info(
            f"Rule engine scan completed. "
            f"Found {len(findings)} matches from {len(matched_rules)} rules"
        )
        
        return findings

    def _get_files_to_scan(self, path: str) -> list[str]:
        """获取要扫描的文件列表。
        
        扫描范围：
        - 如果是文件，直接扫描该文件
        - 如果是目录，递归扫描所有文件
        - 排除常见的二进制文件和依赖目录
        
        Args:
            path: 扫描路径
            
        Returns:
            文件路径列表
        """
        files = []
        target = Path(path)
        
        if not target.exists():
            logger.warning(f"Path not found: {path}")
            return files
        
        if target.is_file():
            return [str(target)]
        
        # 排除的目录和文件
        exclude_dirs = {
            ".git", ".svn", "__pycache__", "node_modules", ".venv",
            "venv", ".egg-info", "dist", "build"
        }
        exclude_extensions = {
            ".pyc", ".pyo", ".pyd", ".so", ".a", ".lib", ".dll",
            ".exe", ".bin", ".o", ".jpg", ".png", ".gif", ".zip",
            ".tar", ".gz", ".rar", ".iso", ".dmg"
        }
        
        # 递归遍历目录
        for root, dirs, filenames in os.walk(target):
            # 原地修改 dirs 以跳过排除的目录
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and not d.startswith(".")
            ]
            
            for filename in filenames:
                # 跳过排除的扩展名
                if any(filename.endswith(ext) for ext in exclude_extensions):
                    continue
                
                file_path = os.path.join(root, filename)
                files.append(file_path)
        
        return files

    def _scan_file(self, file_path: str) -> list[dict[str, Any]]:
        """对单个文件应用所有规则。
        
        Args:
            file_path: 文件路径
            
        Returns:
            匹配的发现列表
        """
        findings = []
        
        try:
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # 对每条规则进行匹配
            for rule in self.rules:
                matches = self._match_rule(rule, content)
                
                if matches:
                    # 创建发现结果
                    finding = self._create_finding(
                        rule,
                        file_path,
                        matches
                    )
                    findings.append(finding)
        
        except Exception as e:
            logger.debug(f"Error reading file {file_path}: {str(e)}")
        
        return findings

    def _match_rule(
        self,
        rule: dict[str, Any],
        content: str
    ) -> list[tuple[int, str]]:
        """对内容应用单条规则，返回所有匹配。
        
        匹配方式：
        1. 支持简单的字符串匹配（大小写不敏感）
        2. 支持正则表达式匹配（以 'regex:' 前缀标识）
        
        Args:
            rule: 规则字典
            content: 要匹配的内容
            
        Returns:
            匹配列表，每个元素为 (行号, 匹配行内容)
        """
        pattern = rule.get("pattern", "")
        matches = []
        
        try:
            lines = content.split("\n")
            
            # 检查是否为正则表达式模式
            if pattern.startswith("regex:"):
                regex_pattern = pattern[6:]  # 移除 'regex:' 前缀
                try:
                    regex = re.compile(regex_pattern, re.IGNORECASE)
                    for line_no, line in enumerate(lines, 1):
                        if regex.search(line):
                            matches.append((line_no, line.strip()))
                except re.error as e:
                    logger.warning(
                        f"Invalid regex pattern in rule {rule.get('id')}: {str(e)}"
                    )
            else:
                # 简单的字符串匹配（大小写不敏感）
                pattern_lower = pattern.lower()
                for line_no, line in enumerate(lines, 1):
                    if pattern_lower in line.lower():
                        matches.append((line_no, line.strip()))
        
        except Exception as e:
            logger.debug(f"Error matching rule {rule.get('id')}: {str(e)}")
        
        return matches

    def _create_finding(
        self,
        rule: dict[str, Any],
        file_path: str,
        matches: list[tuple[int, str]]
    ) -> dict[str, Any]:
        """从规则和匹配创建发现结果。
        
        返回格式与其他分析器统一：
        {
            "title": "规则标题",
            "level": "风险等级",
            "evidence": ["文件路径:行号:匹配内容", ...],
            "summary": "简要说明",
            "rule_id": "规则ID"
        }
        
        Args:
            rule: 规则字典
            file_path: 文件路径
            matches: 匹配列表
            
        Returns:
            发现字典
        """
        # 构建证据列表
        evidence = [
            f"{file_path}:{line_no}:{match_content}"
            for line_no, match_content in matches[:5]  # 仅保留前5个匹配
        ]
        
        # 如果匹配数超过5个，添加摘要
        summary_suffix = ""
        if len(matches) > 5:
            summary_suffix = f"（共 {len(matches)} 处匹配，仅展示前 5 处）"
        
        finding = {
            "title": rule.get("title", "Unknown rule"),
            "level": rule.get("level", "medium"),
            "evidence": evidence,
            "summary": f"规则引擎检测到: {rule.get('title')}{summary_suffix}",
            "rule_id": rule.get("id"),
            "source": rule.get("_source", "unknown")
        }
        
        return finding
