"""规则管理 API 路由集成测试。

测试范围：
- 规则列表查询（全部、内置、自定义过滤）
- 规则创建（成功、字段验证、重复 ID）
- 规则获取（存在、不存在）
- 规则更新（自定义规则、内置规则保护）
- 规则删除（自定义规则、内置规则保护）
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.rule_service import RuleService
from pathlib import Path


@pytest.fixture
def client():
    """创建测试客户端。"""
    return TestClient(app)


@pytest.fixture
def cleanup_custom_rules():
    """清理测试创建的自定义规则。"""
    yield
    # 清理所有测试创建的规则文件
    service = RuleService()
    test_rule_ids = ['test-rule-1', 'test-rule-2', 'api-test-rule', 'test-create-rule', 'test-update-rule', 'test-delete-rule']
    for rule_id in test_rule_ids:
        rule_path = service.custom_dir / f"{rule_id}.yaml"
        if rule_path.exists():
            rule_path.unlink()


class TestRuleListEndpoint:
    """测试规则列表端点。"""
    
    def test_list_all_rules(self, client):
        """测试获取所有规则。"""
        response = client.get("/rules")
        assert response.status_code == 200
        data = response.json()
        assert "rules" in data
        assert "total" in data
        assert data["total"] >= 4  # 至少有 4 条内置规则
        
        # 验证规则格式
        for rule in data["rules"]:
            assert "id" in rule
            assert "title" in rule
            assert "pattern" in rule
            assert "level" in rule
            assert "_source" in rule
    
    def test_list_builtin_rules(self, client):
        """测试过滤内置规则。"""
        response = client.get("/rules?rule_type=builtin")
        assert response.status_code == 200
        data = response.json()
        
        # 验证所有规则都来自内置目录
        for rule in data["rules"]:
            assert rule["_source"].startswith("builtin")
    
    def test_list_custom_rules_empty(self, client):
        """测试自定义规则列表（初始为空）。"""
        response = client.get("/rules?rule_type=custom")
        assert response.status_code == 200
        data = response.json()
        # 初始状态应该没有自定义规则或有之前创建的
        assert isinstance(data["rules"], list)


class TestRuleGetEndpoint:
    """测试规则获取端点。"""
    
    def test_get_existing_rule(self, client):
        """测试获取存在的规则。"""
        # 先列出规则，获取第一条规则的 ID
        list_response = client.get("/rules")
        rules = list_response.json()["rules"]
        assert len(rules) > 0
        
        rule_id = rules[0]["id"]
        response = client.get(f"/rules/{rule_id}")
        assert response.status_code == 200
        rule = response.json()
        assert rule["id"] == rule_id
    
    def test_get_nonexistent_rule(self, client):
        """测试获取不存在的规则。"""
        response = client.get("/rules/nonexistent-rule-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRuleCreateEndpoint:
    """测试规则创建端点。"""
    
    def test_create_rule_success(self, client, cleanup_custom_rules):
        """测试成功创建规则。"""
        rule_data = {
            "id": "test-create-rule",
            "title": "Test Create Rule",
            "pattern": "test_pattern",
            "level": "high",
            "description": "Test rule description"
        }
        
        response = client.post("/rules", json=rule_data)
        assert response.status_code == 201
        created_rule = response.json()
        assert created_rule["id"] == "test-create-rule"
        assert created_rule["title"] == "Test Create Rule"
        assert created_rule["level"] == "high"
        assert "_source" in created_rule
        assert created_rule["_source"].startswith("custom")
    
    def test_create_rule_missing_required_field(self, client):
        """测试创建规则缺少必要字段。"""
        rule_data = {
            "id": "test-rule",
            "title": "Test Rule"
            # 缺少 pattern 和 level
        }
        
        response = client.post("/rules", json=rule_data)
        assert response.status_code == 400
        assert "必要字段" in response.json()["detail"] or "required" in response.json()["detail"].lower()
    
    def test_create_rule_invalid_level(self, client):
        """测试创建规则风险等级无效。"""
        rule_data = {
            "id": "test-rule",
            "title": "Test Rule",
            "pattern": "test_pattern",
            "level": "invalid_level"
        }
        
        response = client.post("/rules", json=rule_data)
        assert response.status_code == 400
        assert "等级" in response.json()["detail"] or "level" in response.json()["detail"].lower()
    
    def test_create_duplicate_rule(self, client, cleanup_custom_rules):
        """测试创建重复 ID 的规则。"""
        rule_data = {
            "id": "test-rule-1",
            "title": "Test Rule 1",
            "pattern": "test_pattern",
            "level": "high"
        }
        
        # 第一次创建成功
        response1 = client.post("/rules", json=rule_data)
        assert response1.status_code == 201
        
        # 第二次创建应该失败
        response2 = client.post("/rules", json=rule_data)
        assert response2.status_code == 400
        assert "已存在" in response2.json()["detail"] or "already" in response2.json()["detail"].lower()


class TestRuleUpdateEndpoint:
    """测试规则更新端点。"""
    
    def test_update_custom_rule(self, client, cleanup_custom_rules):
        """测试更新自定义规则。"""
        # 首先创建一个规则
        rule_data = {
            "id": "test-update-rule",
            "title": "Original Title",
            "pattern": "original_pattern",
            "level": "high"
        }
        create_response = client.post("/rules", json=rule_data)
        assert create_response.status_code == 201
        
        # 更新规则
        update_data = {
            "title": "Updated Title",
            "level": "critical"
        }
        response = client.put("/rules/test-update-rule", json=update_data)
        assert response.status_code == 200
        updated_rule = response.json()
        assert updated_rule["title"] == "Updated Title"
        assert updated_rule["level"] == "critical"
        assert updated_rule["pattern"] == "original_pattern"  # 未修改的字段应保留
    
    def test_update_nonexistent_rule(self, client):
        """测试更新不存在的规则。"""
        update_data = {"title": "Updated"}
        response = client.put("/rules/nonexistent-rule", json=update_data)
        assert response.status_code == 400
        assert "不存在" in response.json()["detail"] or "not" in response.json()["detail"].lower()
    
    def test_update_builtin_rule_protected(self, client):
        """测试不能更新内置规则。"""
        # 获取一个内置规则
        list_response = client.get("/rules?rule_type=builtin")
        builtin_rules = list_response.json()["rules"]
        assert len(builtin_rules) > 0
        
        builtin_rule_id = builtin_rules[0]["id"]
        
        # 尝试更新内置规则
        update_data = {"title": "Hacked Title"}
        response = client.put(f"/rules/{builtin_rule_id}", json=update_data)
        assert response.status_code == 400
        assert "内置规则" in response.json()["detail"] or "builtin" in response.json()["detail"].lower()


class TestRuleDeleteEndpoint:
    """测试规则删除端点。"""
    
    def test_delete_custom_rule(self, client, cleanup_custom_rules):
        """测试删除自定义规则。"""
        # 首先创建一个规则
        rule_data = {
            "id": "test-delete-rule",
            "title": "Rule to Delete",
            "pattern": "delete_pattern",
            "level": "medium"
        }
        create_response = client.post("/rules", json=rule_data)
        assert create_response.status_code == 201
        
        # 删除规则
        response = client.delete("/rules/test-delete-rule")
        assert response.status_code == 200
        assert "message" in response.json()
        
        # 验证规则已删除
        get_response = client.get("/rules/test-delete-rule")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_rule(self, client):
        """测试删除不存在的规则。"""
        response = client.delete("/rules/nonexistent-rule")
        assert response.status_code == 400
        assert "不存在" in response.json()["detail"] or "not" in response.json()["detail"].lower()
    
    def test_delete_builtin_rule_protected(self, client):
        """测试不能删除内置规则。"""
        # 获取一个内置规则
        list_response = client.get("/rules?rule_type=builtin")
        builtin_rules = list_response.json()["rules"]
        assert len(builtin_rules) > 0
        
        builtin_rule_id = builtin_rules[0]["id"]
        
        # 尝试删除内置规则
        response = client.delete(f"/rules/{builtin_rule_id}")
        assert response.status_code == 400
        assert "内置规则" in response.json()["detail"] or "builtin" in response.json()["detail"].lower()


class TestRuleIntegration:
    """规则管理集成测试。"""
    
    def test_full_crud_workflow(self, client, cleanup_custom_rules):
        """测试完整的创建、读取、更新、删除工作流。"""
        rule_id = "test-rule-2"
        
        # 1. 创建规则
        create_data = {
            "id": rule_id,
            "title": "Integration Test Rule",
            "pattern": "integration_test",
            "level": "medium"
        }
        response = client.post("/rules", json=create_data)
        assert response.status_code == 201
        
        # 2. 读取规则
        response = client.get(f"/rules/{rule_id}")
        assert response.status_code == 200
        rule = response.json()
        assert rule["title"] == "Integration Test Rule"
        
        # 3. 更新规则
        update_data = {
            "title": "Updated Integration Test Rule",
            "level": "high"
        }
        response = client.put(f"/rules/{rule_id}", json=update_data)
        assert response.status_code == 200
        rule = response.json()
        assert rule["title"] == "Updated Integration Test Rule"
        assert rule["level"] == "high"
        
        # 4. 验证列表中能看到更新后的规则
        response = client.get("/rules")
        rules = response.json()["rules"]
        updated_rule = next((r for r in rules if r["id"] == rule_id), None)
        assert updated_rule is not None
        assert updated_rule["title"] == "Updated Integration Test Rule"
        
        # 5. 删除规则
        response = client.delete(f"/rules/{rule_id}")
        assert response.status_code == 200
        
        # 6. 验证规则已删除
        response = client.get(f"/rules/{rule_id}")
        assert response.status_code == 404
