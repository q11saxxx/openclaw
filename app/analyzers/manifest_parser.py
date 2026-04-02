"""清单解析器。

规则描述：
- 负责解析 YAML/frontmatter/自定义元数据。
- 元数据提取应保持字段稳定，便于后续评分模块使用。
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import logging
from copy import deepcopy

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ManifestParser:
    """解析 skill 的清单文件（SKILL.md frontmatter、manifest.yaml 等）。
    
    确保字段稳定性和数据一致性，为评分模块提供规范化的元数据。
    """
    
    MANIFEST_FILES = ["SKILL.md", ".instructions.md", ".prompt.md", ".agent.md"]
    YAML_FILES = ["manifest.yaml", "manifest.yml"]
    
    # 标准化的输出字段（定义了评分模块需要的所有字段）
    STANDARD_FIELDS = {
        "name": None,                      # 必需：skill名称
        "version": "0.1.0",               # 版本号
        "description": "",                 # 描述
        "author": "",                      # 作者
        "license": "",                     # 许可证
        "compatible_versions": [],         # 兼容的版本号列表
        "dependencies": [],                # 依赖列表
        "tags": [],                        # 标签列表
        "custom_fields": {},               # 自定义字段容器
    }
    
    # 字段类型验证规则
    FIELD_VALIDATORS = {
        "name": (str, lambda x: len(x) > 0 and len(x) <= 100),
        "version": (str, lambda x: _is_valid_version(x)),
        "description": (str, lambda x: len(x) <= 500),
        "author": (str, lambda x: len(x) <= 100),
        "license": (str, lambda x: len(x) <= 50),
        "compatible_versions": (list, lambda x: all(isinstance(v, (str, float, int)) for v in x)),
        "dependencies": (list, lambda x: all(isinstance(d, (str, dict)) for d in x)),
        "tags": (list, lambda x: all(isinstance(t, str) for t in x)),
        "custom_fields": (dict, lambda x: isinstance(x, dict)),
    }
    
    def parse(self, path: str) -> dict:
        """
        解析 skill 清单信息。
        
        Args:
            path: skill 目录路径
            
        Returns:
            包含标准化清单字段的字典，所有字段都经过验证和规范化
        """
        result = deepcopy(self.STANDARD_FIELDS)
        result["path"] = path
        result["parse_errors"] = []
        result["is_valid"] = True
        
        try:
            skill_path = Path(path)
            
            if not skill_path.exists():
                result["parse_errors"].append(f"Path does not exist: {path}")
                result["is_valid"] = False
                return result
            
            if not skill_path.is_dir():
                result["parse_errors"].append(f"Path is not a directory: {path}")
                result["is_valid"] = False
                return result
            
            # 优先级 1: 从 SKILL.md frontmatter 解析
            skill_md = skill_path / "SKILL.md"
            if skill_md.exists():
                fm_result = self._parse_frontmatter(skill_md)
                self._merge_result(result, fm_result)
            
            # 优先级 2: 从 manifest.yaml 解析（覆盖）
            for yaml_name in self.YAML_FILES:
                yaml_file = skill_path / yaml_name
                if yaml_file.exists():
                    yaml_result = self._parse_yaml(yaml_file)
                    self._merge_result(result, yaml_result)
                    break
            
            # 优先级 3: 从 .instructions.md 等补充
            for md_name in [".instructions.md", ".prompt.md", ".agent.md"]:
                md_file = skill_path / md_name
                if md_file.exists() and md_name not in result.get("custom_fields", {}):
                    result["custom_fields"][md_name] = self._extract_metadata(md_file)
            
            # 从目录名推断 name（如果仍未定义）
            if not result.get("name"):
                result["name"] = skill_path.name
            
            # 验证和规范化字段
            result = self._validate_and_normalize(result)
            
        except Exception as e:
            logger.error(f"Error parsing manifest from {path}: {str(e)}")
            result["parse_errors"].append(str(e))
            result["is_valid"] = False
        
        return result
    
    def _merge_result(self, target: dict, source: dict) -> None:
        """合并解析结果到目标字典，仅合并标准字段。"""
        for key in self.STANDARD_FIELDS.keys():
            if key in source and source[key]:
                if isinstance(self.STANDARD_FIELDS[key], list):
                    # 列表字段合并而非覆盖
                    if isinstance(source[key], list):
                        if key in target and isinstance(target[key], list):
                            target[key].extend(source[key])
                        else:
                            target[key] = source[key]
                else:
                    target[key] = source[key]
    
    def _validate_and_normalize(self, data: dict) -> dict:
        """验证和规范化所有字段。"""
        result = deepcopy(data)
        errors = result.get("parse_errors", [])
        
        for field_name, validator_tuple in self.FIELD_VALIDATORS.items():
            if field_name in result:
                field_value = result[field_name]
                expected_type, validator_func = validator_tuple
                
                # 类型检查
                if field_value is not None and not isinstance(field_value, expected_type):
                    try:
                        # 尝试类型转换
                        if expected_type == list and not isinstance(field_value, list):
                            result[field_name] = [field_value] if field_value else []
                        elif expected_type == str:
                            result[field_name] = str(field_value)
                        else:
                            result[field_name] = expected_type(field_value)
                    except Exception as e:
                        errors.append(f"Type conversion failed for '{field_name}': {str(e)}")
                        result["is_valid"] = False
                
                # 值验证
                if result[field_name] is not None:
                    try:
                        if not validator_func(result[field_name]):
                            errors.append(f"Validation failed for '{field_name}': value={result[field_name]}")
                            result["is_valid"] = False
                    except Exception as e:
                        errors.append(f"Validation error for '{field_name}': {str(e)}")
                        result["is_valid"] = False
        
        result["parse_errors"] = errors
        return result
    
    def is_score_ready(self, manifest: dict) -> tuple[bool, List[str]]:
        """
        检查清单是否准备好进行评分。
        返回 (是否就绪, 缺失字段清单)
        """
        missing_fields = []
        
        if not manifest.get("is_valid", False):
            return False, manifest.get("parse_errors", ["Unknown validation error"])
        
        # 检查必需字段
        required_fields = ["name", "version"]
        for field in required_fields:
            if not manifest.get(field):
                missing_fields.append(field)
        
        # 检查字段不为None
        if manifest.get("name") is None:
            missing_fields.append("name is None")
        
        return len(missing_fields) == 0, missing_fields
    
    def get_score_payload(self, manifest: dict) -> Dict[str, Any]:
        """
        生成供评分模块使用的规范化数据。
        返回一个只包含标准字段的字典，便于评分计算。
        """
        payload = {}
        for field_name in self.STANDARD_FIELDS.keys():
            if field_name in manifest:
                payload[field_name] = manifest[field_name]
        
        payload["metadata"] = {
            "path": manifest.get("path", ""),
            "parse_errors": manifest.get("parse_errors", []),
            "is_valid": manifest.get("is_valid", False),
        }
        
        return payload
    
    def _parse_frontmatter(self, file_path: Path) -> dict:
        """
        从 Markdown 文件中提取 YAML frontmatter。
        
        格式:
        ---
        name: my-skill
        version: 1.0.0
        ---
        """
        result = {}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # 查找 frontmatter 块 (--- ... ---)
            match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            if match:
                fm_text = match.group(1)
                result = self._parse_yaml_text(fm_text)
                result["frontmatter_found"] = True
            else:
                # 尝试在第三行前查找 (保留一些灵活性)
                lines = content.split("\n")
                if lines and lines[0].strip() == "---":
                    fm_lines = []
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == "---":
                            fm_text = "\n".join(fm_lines)
                            result = self._parse_yaml_text(fm_text)
                            result["frontmatter_found"] = True
                            break
                        fm_lines.append(line)
        
        except Exception as e:
            logger.warning(f"Failed to parse frontmatter from {file_path}: {str(e)}")
        
        return result
    
    def _parse_yaml(self, file_path: Path) -> dict:
        """
        解析 YAML 格式的清单文件。
        优先使用 PyYAML 库，降级到手动解析。
        """
        result = {}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # 方案 1: 使用 PyYAML 库（如果可用）
            if YAML_AVAILABLE:
                try:
                    result = yaml.safe_load(content) or {}
                    logger.debug(f"Parsed YAML using PyYAML from {file_path}")
                except yaml.YAMLError as e:
                    logger.warning(f"PyYAML parsing failed for {file_path}: {str(e)}")
                    # 降级到手动解析
                    result = self._parse_yaml_text(content)
            else:
                # 方案 2: 手动解析（降级方案）
                result = self._parse_yaml_text(content)
                logger.debug(f"Parsed YAML manually from {file_path}")
        
        except Exception as e:
            logger.warning(f"Failed to parse YAML from {file_path}: {str(e)}")
        
        return result
    
    def _parse_yaml_text(self, text: str) -> dict:
        """
        手动解析简单的 YAML 格式（降级方案）。
        
        支持以下格式:
        name: value
        version: 1.0.0
        dependencies: [dep1, dep2]
        compatible_versions: [1.0, 2.0]
        tags: [tag1, tag2]
        """
        result = {}
        
        lines = text.strip().split("\n")
        current_key = None
        current_value_lines = []
        
        for line in lines:
            # 保留原始行以检测缩进
            if not line.strip() or line.strip().startswith("#"):
                continue
            
            # 检查是否是新的键值对（行的开始不是空格）
            if line and line[0] not in (' ', '\t'):
                # 保存之前的键值对
                if current_key:
                    result[current_key] = self._parse_yaml_value("\n".join(current_value_lines))
                
                # 解析新的键值对
                if ":" in line:
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    current_value_lines = [value]
                else:
                    current_key = None
            else:
                # 续行
                if current_key:
                    current_value_lines.append(line)
        
        # 保存最后的键值对
        if current_key:
            result[current_key] = self._parse_yaml_value("\n".join(current_value_lines))
        
        return result
    
    def _parse_yaml_value(self, value_str: str) -> Any:
        """
        解析 YAML 值。
        支持：字符串、数字、布尔值、列表、null等。
        """
        value = value_str.strip()
        
        # 空值
        if not value or value.lower() in ("null", "~"):
            return None
        
        # 布尔值
        if value.lower() in ("true", "yes"):
            return True
        if value.lower() in ("false", "no"):
            return False
        
        # 列表 [item1, item2]
        if value.startswith("[") and value.endswith("]"):
            items_str = value[1:-1]
            if not items_str.strip():
                return []
            items = [self._parse_yaml_value(item.strip()) for item in items_str.split(",")]
            return items
        
        # 引号字符串 "string" 或 'string'
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        # 数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 默认返回字符串
        return value
    
    def _extract_metadata(self, file_path: Path) -> dict:
        """从任意 Markdown 文件提取基础元数据。"""
        metadata = {
            "file": str(file_path.name),
            "size": 0,
            "first_line": "",
            "lines_count": 0,
        }
        
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            metadata["lines_count"] = len(lines)
            
            try:
                metadata["size"] = file_path.stat().st_size
            except Exception:
                pass
            
            if lines:
                # 提取第一个非空非注释行
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        metadata["first_line"] = stripped[:100]
                        break
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {str(e)}")
        
        return metadata


def _is_valid_version(version_str: str) -> bool:
    """验证版本号格式 (semver)."""
    if not isinstance(version_str, str):
        return False
    
    # 支持格式: 1.0.0, 1.0.0-alpha, 1.0.0+build等
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
    return bool(re.match(pattern, version_str))
