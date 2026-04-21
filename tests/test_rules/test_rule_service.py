"""规则服务单元测试。

测试范围：
- 规则加载（内置、自定义）
- 规则列表查询和过滤
- 规则获取
- 规则创建和验证
- 规则更新和内置规则保护
- 规则删除和内置规则保护
"""
import pytest
from pathlib import Path
import yaml
from app.services.rule_service import RuleService


@pytest.fixture
def rule_service():
    """创建规则服务实例。"""
    service = RuleService()
    return service


@pytest.fixture
def cleanup_custom_rules(rule_service):
    """清理测试创建的自定义规则。"""
    yield
    # 清理所有测试创建的规则文件
    test_rule_ids = [
        'unit-test-rule-1', 'unit-test-rule-2', 'unit-test-rule-3',
        'test-create', 'test-update', 'test-delete', 'test-duplicate'
    ]
    for rule_id in test_rule_ids:
        rule_path = rule_service.custom_dir / f"{rule_id}.yaml"
        if rule_path.exists():
            rule_path.unlink()


class TestRuleServiceList:
    """测试规则列表功能。"""
    
    def test_list_all_rules(self, rule_service):
        """测试列出所有规则。"""
        rules = rule_service.list_rules()
        assert isinstance(rules, list)
        assert len(rules) >= 4  # 至少有 4 条内置规则
        
        # 验证规则结构
        for rule in rules:
            assert "id" in rule
            assert "title" in rule
            assert "pattern" in rule
            assert "level" in rule
            assert "_source" in rule
    
    def test_list_builtin_rules(self, rule_service):
        """测试列出内置规则。"""
        rules = rule_service.list_rules(rule_type='builtin')
        assert isinstance(rules, list)
        assert len(rules) >= 4
        
        # 验证所有规则都来自内置目录
        for rule in rules:
            assert rule["_source"].startswith("builtin")
    
    def test_list_custom_rules(self, rule_service, cleanup_custom_rules):
        """测试列出自定义规则。"""
        rules = rule_service.list_rules(rule_type='custom')
        assert isinstance(rules, list)
        
        # 初始状态可能为空或有之前的规则
        for rule in rules:
            assert rule["_source"].startswith("custom")
    
    def test_list_invalid_rule_type(self, rule_service):
        """测试使用无效的规则类型过滤。"""
        # 应该返回空列表或忽略无效类型
        rules = rule_service.list_rules(rule_type='invalid')
        # 根据实现，可能返回空或所有规则
        assert isinstance(rules, list)


class TestRuleServiceGet:
    """测试规则获取功能。"""
    
    def test_get_builtin_rule(self, rule_service):
        """测试获取内置规则。"""
        rules = rule_service.list_rules(rule_type='builtin')
        assert len(rules) > 0
        
        rule_id = rules[0]["id"]
        rule = rule_service.get_rule(rule_id)
        assert rule is not None
        assert rule["id"] == rule_id
    
    def test_get_nonexistent_rule(self, rule_service):
        """测试获取不存在的规则。"""
        rule = rule_service.get_rule("nonexistent-rule-id")
        assert rule is None
    
    def test_get_custom_rule(self, rule_service, cleanup_custom_rules):
        """测试获取自定义规则。"""
        # 首先创建一个规则
        rule_data = {
            "id": "unit-test-rule-1",
            "title": "Unit Test Rule 1",
            "pattern": "test_pattern",
            "level": "high"
        }
        rule_service.create_rule(rule_data)
        
        # 然后获取它
        rule = rule_service.get_rule("unit-test-rule-1")
        assert rule is not None
        assert rule["id"] == "unit-test-rule-1"
        assert rule["title"] == "Unit Test Rule 1"


class TestRuleServiceCreate:
    """测试规则创建功能。"""
    
    def test_create_rule_success(self, rule_service, cleanup_custom_rules):
        """测试成功创建规则。"""
        rule_data = {
            "id": "test-create",
            "title": "Test Create Rule",
            "pattern": "test_pattern",
            "level": "high",
            "description": "Test rule"
        }
        
        result = rule_service.create_rule(rule_data)
        assert result["id"] == "test-create"
        assert result["title"] == "Test Create Rule"
        assert result["level"] == "high"
        assert "_source" in result
        assert "custom" in result["_source"]
        
        # 验证规则文件已创建
        rule_file = rule_service.custom_dir / "test-create.yaml"
        assert rule_file.exists()
    
    def test_create_rule_missing_id(self, rule_service):
        """测试创建规则缺少 ID。"""
        rule_data = {
            "title": "No ID Rule",
            "pattern": "test_pattern",
            "level": "high"
        }
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "必要字段" in str(exc_info.value)
    
    def test_create_rule_missing_title(self, rule_service):
        """测试创建规则缺少标题。"""
        rule_data = {
            "id": "no-title",
            "pattern": "test_pattern",
            "level": "high"
        }
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "必要字段" in str(exc_info.value)
    
    def test_create_rule_missing_pattern(self, rule_service):
        """测试创建规则缺少模式。"""
        rule_data = {
            "id": "no-pattern",
            "title": "No Pattern Rule",
            "level": "high"
        }
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "必要字段" in str(exc_info.value)
    
    def test_create_rule_missing_level(self, rule_service):
        """测试创建规则缺少风险等级。"""
        rule_data = {
            "id": "no-level",
            "title": "No Level Rule",
            "pattern": "test_pattern"
        }
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "必要字段" in str(exc_info.value)
    
    def test_create_rule_invalid_level(self, rule_service):
        """测试创建规则风险等级无效。"""
        rule_data = {
            "id": "invalid-level",
            "title": "Invalid Level Rule",
            "pattern": "test_pattern",
            "level": "super_critical"  # 无效等级
        }
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "等级" in str(exc_info.value) and "不合法" in str(exc_info.value)
    
    def test_create_rule_duplicate_id(self, rule_service, cleanup_custom_rules):
        """测试创建重复 ID 的规则。"""
        rule_data = {
            "id": "test-duplicate",
            "title": "Duplicate Test",
            "pattern": "test_pattern",
            "level": "high"
        }
        
        # 第一次创建成功
        rule_service.create_rule(rule_data)
        
        # 第二次创建应该失败
        with pytest.raises(ValueError) as exc_info:
            rule_service.create_rule(rule_data)
        assert "已存在" in str(exc_info.value)
    
    def test_create_rule_all_valid_levels(self, rule_service, cleanup_custom_rules):
        """测试创建规则支持所有有效的风险等级。"""
        valid_levels = ['low', 'medium', 'high', 'critical']
        
        for idx, level in enumerate(valid_levels):
            rule_data = {
                "id": f"unit-test-rule-{idx}",
                "title": f"Test Level {level}",
                "pattern": "test_pattern",
                "level": level
            }
            result = rule_service.create_rule(rule_data)
            assert result["level"] == level


class TestRuleServiceUpdate:
    """测试规则更新功能。"""
    
    def test_update_custom_rule_success(self, rule_service, cleanup_custom_rules):
        """测试成功更新自定义规则。"""
        # 创建规则
        rule_data = {
            "id": "test-update",
            "title": "Original Title",
            "pattern": "original_pattern",
            "level": "high"
        }
        rule_service.create_rule(rule_data)
        
        # 更新规则
        update_data = {
            "title": "Updated Title",
            "level": "critical"
        }
        result = rule_service.update_rule("test-update", update_data)
        
        assert result["id"] == "test-update"
        assert result["title"] == "Updated Title"
        assert result["level"] == "critical"
        assert result["pattern"] == "original_pattern"  # 未修改的字段应保留
    
    def test_update_nonexistent_rule(self, rule_service):
        """测试更新不存在的规则。"""
        update_data = {"title": "Updated"}
        
        with pytest.raises(ValueError) as exc_info:
            rule_service.update_rule("nonexistent-rule", update_data)
        assert "不存在" in str(exc_info.value)
    
    def test_update_builtin_rule_protected(self, rule_service):
        """测试不能更新内置规则。"""
        # 获取一个内置规则
        builtin_rules = rule_service.list_rules(rule_type='builtin')
        assert len(builtin_rules) > 0
        
        builtin_rule_id = builtin_rules[0]["id"]
        
        # 尝试更新内置规则
        update_data = {"title": "Hacked Title"}
        with pytest.raises(ValueError) as exc_info:
            rule_service.update_rule(builtin_rule_id, update_data)
        assert "不能修改内置规则" in str(exc_info.value)
    
    def test_update_rule_invalid_level(self, rule_service, cleanup_custom_rules):
        """测试更新规则设置无效风险等级。"""
        # 创建规则
        rule_data = {
            "id": "test-invalid-update",
            "title": "Test Rule",
            "pattern": "test_pattern",
            "level": "high"
        }
        rule_service.create_rule(rule_data)
        
        # 尝试更新为无效等级
        update_data = {"level": "invalid_level"}
        with pytest.raises(ValueError) as exc_info:
            rule_service.update_rule("test-invalid-update", update_data)
        assert "等级" in str(exc_info.value) and "不合法" in str(exc_info.value)


class TestRuleServiceDelete:
    """测试规则删除功能。"""
    
    def test_delete_custom_rule_success(self, rule_service, cleanup_custom_rules):
        """测试成功删除自定义规则。"""
        # 创建规则
        rule_data = {
            "id": "test-delete",
            "title": "Rule to Delete",
            "pattern": "delete_pattern",
            "level": "medium"
        }
        rule_service.create_rule(rule_data)
        
        # 删除规则
        result = rule_service.delete_rule("test-delete")
        assert result is True
        
        # 验证规则已删除
        rule = rule_service.get_rule("test-delete")
        assert rule is None
        
        # 验证规则文件已删除
        rule_file = rule_service.custom_dir / "test-delete.yaml"
        assert not rule_file.exists()
    
    def test_delete_nonexistent_rule(self, rule_service):
        """测试删除不存在的规则。"""
        with pytest.raises(ValueError) as exc_info:
            rule_service.delete_rule("nonexistent-rule")
        assert "不存在" in str(exc_info.value)
    
    def test_delete_builtin_rule_protected(self, rule_service):
        """测试不能删除内置规则。"""
        # 获取一个内置规则
        builtin_rules = rule_service.list_rules(rule_type='builtin')
        assert len(builtin_rules) > 0
        
        builtin_rule_id = builtin_rules[0]["id"]
        
        # 尝试删除内置规则
        with pytest.raises(ValueError) as exc_info:
            rule_service.delete_rule(builtin_rule_id)
        assert "不能删除内置规则" in str(exc_info.value)


class TestRuleServiceIntegration:
    """规则服务集成测试。"""
    
    def test_rule_directory_structure(self, rule_service):
        """测试规则目录结构。"""
        assert rule_service.rules_dir.exists()
        assert rule_service.builtin_dir.exists()
        assert rule_service.custom_dir.exists()
    
    def test_builtin_rules_are_readonly(self, rule_service):
        """测试内置规则目录下的所有规则都是只读的。"""
        builtin_rules = rule_service.list_rules(rule_type='builtin')
        
        for rule in builtin_rules:
            # 尝试更新应该失败
            with pytest.raises(ValueError) as exc_info:
                rule_service.update_rule(rule["id"], {"title": "Hacked"})
            assert "不能修改内置规则" in str(exc_info.value)
            
            # 尝试删除应该失败
            with pytest.raises(ValueError) as exc_info:
                rule_service.delete_rule(rule["id"])
            assert "不能删除内置规则" in str(exc_info.value)
    
    def test_custom_rules_directory_created_automatically(self):
        """测试自定义规则目录自动创建。"""
        # 创建新的服务实例（如果自定义目录不存在，应该自动创建）
        service = RuleService()
        assert service.custom_dir.exists()
        assert service.custom_dir.is_dir()
