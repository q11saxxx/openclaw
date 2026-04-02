"""Skill 解析代理。

规则描述：
- 只负责 skill 基础结构、SKILL.md、manifest 等解析。
- 不在本 agent 内做风险评分。
"""
import logging
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.core.context import AuditContext
from app.analyzers.skill_parser import SkillParser
from app.analyzers.manifest_parser import ManifestParser

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    """Skill 解析代理。

    职责：
    - 解析 skill 的目录结构、SKILL.md 文件、清单元数据
    - 提取基础信息供后续分析使用
    - 只做事实提取，不做风险判断
    
    规则描述：
    - 只负责 skill 基础结构、SKILL.md、manifest 等解析。
    - 不在本 agent 内做风险评分。
    """
    name = "parser"

    def __init__(self) -> None:
        """初始化解析代理，创建必要的解析器实例。"""
        self.skill_parser = SkillParser()
        self.manifest_parser = ManifestParser()

    def run(self, context: AuditContext) -> None:
        """
        执行 skill 解析。
        
        Args:
            context: 审计上下文，包含 skill_path
            
        说明：
        - 将解析结果存入 context.parsed
        - 包括结构信息和清单信息
        - 如果解析出错，会记录错误但不中断流程
        """
        logger.info(f"Parser agent starting for: {context.skill_path}")
        
        try:
            # 第一阶段：解析目录结构
            structure = self._parse_structure(context.skill_path)
            context.parsed["structure"] = structure
            
            # 第二阶段：解析清单信息
            manifest = self._parse_manifest(context.skill_path)
            context.parsed["manifest"] = manifest
            
            # 第三阶段：验证解析结果
            validation = self._validate_parsed_data(structure, manifest)
            context.parsed["validation"] = validation
            
            logger.info(f"Parser agent completed successfully for: {context.skill_path}")
            
        except Exception as e:
            logger.error(f"Error in parser agent: {str(e)}", exc_info=True)
            context.parsed["parser_error"] = str(e)
            # 不抛出异常，允许流程继续

    def _parse_structure(self, skill_path: str) -> dict:
        """
        解析 skill 的目录结构。
        
        Args:
            skill_path: skill 目录路径
            
        Returns:
            包含文件列表、结构信息等的字典
        """
        logger.debug(f"Parsing structure for: {skill_path}")
        
        try:
            structure = self.skill_parser.parse(skill_path)
            
            # 记录解析统计
            if "structure" in structure:
                logger.debug(
                    f"Found {structure['structure'].get('total_files', 0)} files, "
                    f"SKILL.md: {structure.get('skill_md_found', False)}"
                )
            
            return structure
            
        except Exception as e:
            logger.error(f"Failed to parse structure: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "path": skill_path,
                "files": [],
                "skill_md_found": False
            }

    def _parse_manifest(self, skill_path: str) -> dict:
        """
        解析 skill 的清单信息。
        
        Args:
            skill_path: skill 目录路径
            
        Returns:
            包含标准化清单字段的字典
        """
        logger.debug(f"Parsing manifest for: {skill_path}")
        
        try:
            manifest = self.manifest_parser.parse(skill_path)
            
            # 记录提取的关键信息
            logger.debug(
                f"Manifest: name={manifest.get('name')}, "
                f"version={manifest.get('version')}, "
                f"has_frontmatter={manifest.get('frontmatter_found', False)}"
            )
            
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to parse manifest: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "path": skill_path,
                "name": "unknown",
                "version": "0.1.0"
            }

    def _validate_parsed_data(self, structure: dict, manifest: dict) -> dict:
        """
        验证解析的数据完整性和合理性。
        
        Args:
            structure: 目录结构解析结果
            manifest: 清单解析结果
            
        Returns:
            包含验证结果的字典，列出警告和错误
        """
        validation = {
            "warnings": [],
            "errors": [],
            "checks": {}
        }
        
        # 检查是否找到 SKILL.md
        if not structure.get("skill_md_found", False):
            validation["warnings"].append("SKILL.md not found")
        else:
            validation["checks"]["skill_md_found"] = True
        
        # 检查是否找到清单文件
        if not manifest.get("manifest_files") and not manifest.get("frontmatter_found"):
            validation["warnings"].append("No manifest files found")
        else:
            validation["checks"]["manifest_found"] = True
        
        # 检查 skill 名称
        if not manifest.get("name") or manifest.get("name") == "unknown":
            validation["warnings"].append("Skill name could not be determined")
        else:
            validation["checks"]["name_available"] = True
        
        # 检查版本格式
        version = manifest.get("version", "0.1.0")
        if not self._is_valid_version(version):
            validation["warnings"].append(f"Invalid version format: {version}")
        else:
            validation["checks"]["version_valid"] = True
        
        # 检查文件数量
        file_count = structure.get("structure", {}).get("total_files", 0)
        if file_count == 0:
            validation["errors"].append("No files found in skill directory")
        elif file_count < 2:
            validation["warnings"].append("Very few files in skill directory")
        else:
            validation["checks"]["file_count_reasonable"] = True
        
        # 检查是否有任何解析错误
        if structure.get("error"):
            validation["errors"].append(f"Structure parse error: {structure['error']}")
        if manifest.get("error"):
            validation["errors"].append(f"Manifest parse error: {manifest['error']}")
        
        return validation

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """
        验证版本号格式（简单的 semver 检查）。
        
        Args:
            version: 版本字符串
            
        Returns:
            版本格式是否有效
        """
        import re
        # 允许 1.0.0, 1.0, v1.0.0, 1.0.0-alpha, 1.0.0-beta.1 等格式
        pattern = r"^v?\d+(\.\d+)?(\.\d+)?(\-[a-zA-Z0-9\.]+)?$"
        return bool(re.match(pattern, str(version)))

