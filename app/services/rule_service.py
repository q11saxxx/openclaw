"""规则服务。

提供规则加载、列表、创建、更新、删除等管理能力。
"""
import logging
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


class RuleService:
    """规则管理服务。"""
    
    def __init__(self):
        """初始化规则服务。"""
        self.rules_dir = Path(__file__).parent.parent / "rules"
        self.builtin_dir = self.rules_dir / "builtin"
        self.custom_dir = self.rules_dir / "custom"
        
        # 确保自定义规则目录存在
        self.custom_dir.mkdir(parents=True, exist_ok=True)
    
    def list_rules(self, rule_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有规则。
        
        Args:
            rule_type: 规则类型过滤（'builtin' 或 'custom'，None 为全部）
            
        Returns:
            规则列表
        """
        rules = []
        
        if rule_type in [None, 'builtin']:
            rules.extend(self._load_rules_from_dir(self.builtin_dir, 'builtin'))
        
        if rule_type in [None, 'custom']:
            rules.extend(self._load_rules_from_dir(self.custom_dir, 'custom'))
        
        return rules
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """获取指定规则。
        
        Args:
            rule_id: 规则 ID
            
        Returns:
            规则字典或 None
        """
        for rule in self.list_rules():
            if rule.get('id') == rule_id:
                return rule
        return None
    
    def create_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新规则。
        
        Args:
            rule_data: 规则数据，包含 id, title, pattern, level 等字段
            
        Returns:
            创建成功的规则（含元数据）
        """
        # 验证规则格式
        required_fields = {'id', 'title', 'pattern', 'level'}
        if not all(field in rule_data for field in required_fields):
            raise ValueError(f"规则缺少必要字段: {required_fields}")
        
        valid_levels = {'low', 'medium', 'high', 'critical'}
        if rule_data.get('level') not in valid_levels:
            raise ValueError(f"规则等级不合法: {rule_data.get('level')}")
        
        # 检查规则 ID 是否已存在
        if self.get_rule(rule_data['id']):
            raise ValueError(f"规则 ID 已存在: {rule_data['id']}")
        
        # 生成规则文件名
        filename = f"{rule_data['id']}.yaml"
        rule_path = self.custom_dir / filename
        
        # 将规则保存为 YAML
        rule_content = {
            'rules': [rule_data]
        }
        
        try:
            with open(rule_path, 'w', encoding='utf-8') as f:
                yaml.dump(rule_content, f, allow_unicode=True)
            
            logger.info(f"Created rule: {rule_data['id']}")
            
            # 返回完整规则信息
            result = rule_data.copy()
            result['_source'] = f"custom/{filename}"
            return result
        
        except Exception as e:
            logger.error(f"Failed to create rule: {str(e)}")
            raise
    
    def update_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新规则。
        
        Args:
            rule_id: 规则 ID
            rule_data: 新的规则数据
            
        Returns:
            更新后的规则
        """
        # 获取原有规则
        existing_rule = self.get_rule(rule_id)
        if not existing_rule:
            raise ValueError(f"规则不存在: {rule_id}")
        
        # 检查是否为内置规则
        if existing_rule.get('_source', '').startswith('builtin'):
            raise ValueError(f"不能修改内置规则: {rule_id}")
        
        # 验证新数据
        valid_levels = {'low', 'medium', 'high', 'critical'}
        if 'level' in rule_data and rule_data['level'] not in valid_levels:
            raise ValueError(f"规则等级不合法: {rule_data.get('level')}")
        
        # 合并原有数据和新数据
        updated_rule = existing_rule.copy()
        updated_rule.update(rule_data)
        
        # 保持规则 ID 不变
        updated_rule['id'] = rule_id
        
        # 获取规则文件路径
        source = existing_rule.get('_source', '')
        if source.startswith('custom/'):
            filename = source.split('/', 1)[1]
        else:
            # 如果是内置规则复制到自定义目录
            filename = f"{rule_id}.yaml"
        
        rule_path = self.custom_dir / filename
        
        try:
            rule_content = {'rules': [updated_rule]}
            with open(rule_path, 'w', encoding='utf-8') as f:
                yaml.dump(rule_content, f, allow_unicode=True)
            
            logger.info(f"Updated rule: {rule_id}")
            
            updated_rule['_source'] = f"custom/{filename}"
            return updated_rule
        
        except Exception as e:
            logger.error(f"Failed to update rule: {str(e)}")
            raise
    
    def delete_rule(self, rule_id: str) -> bool:
        """删除规则。
        
        Args:
            rule_id: 规则 ID
            
        Returns:
            删除成功返回 True
        """
        existing_rule = self.get_rule(rule_id)
        if not existing_rule:
            raise ValueError(f"规则不存在: {rule_id}")
        
        # 检查是否为内置规则
        if existing_rule.get('_source', '').startswith('builtin'):
            raise ValueError(f"不能删除内置规则: {rule_id}")
        
        # 获取规则文件路径
        source = existing_rule.get('_source', '')
        if source.startswith('custom/'):
            filename = source.split('/', 1)[1]
            rule_path = self.custom_dir / filename
            
            try:
                if rule_path.exists():
                    rule_path.unlink()
                    logger.info(f"Deleted rule: {rule_id}")
                    return True
            except Exception as e:
                logger.error(f"Failed to delete rule: {str(e)}")
                raise
        
        raise ValueError(f"无法确定规则文件位置: {rule_id}")
    
    def _load_rules_from_dir(self, directory: Path, rule_type: str) -> List[Dict[str, Any]]:
        """从目录加载规则。
        
        Args:
            directory: 规则目录
            rule_type: 规则类型标识
            
        Returns:
            规则列表
        """
        rules = []
        
        if not directory.exists():
            return rules
        
        for yaml_file in directory.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if content and 'rules' in content:
                    for rule in content['rules']:
                        rule['_source'] = f"{rule_type}/{yaml_file.name}"
                        rules.append(rule)
            
            except Exception as e:
                logger.warning(f"Failed to load rule from {yaml_file}: {str(e)}")
        
        return rules
