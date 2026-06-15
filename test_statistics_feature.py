#!/usr/bin/env python3
"""
统计分析功能测试脚本
验证新增的审计统计分析API是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_statistics_service():
    """测试统计服务基础功能"""
    print("=" * 60)
    print("测试1: AuditStatisticsService 基础功能")
    print("=" * 60)
    
    from app.services.audit_statistics_service import AuditStatisticsService
    
    service = AuditStatisticsService()
    
    # 测试获取趋势数据
    print("\n1.1 获取审计趋势 (7天):")
    trends = service.get_audit_trends(days=7)
    assert "trend_data" in trends, "缺少 trend_data 字段"
    assert "severity_distribution" in trends, "缺少 severity_distribution 字段"
    assert "total_audits" in trends, "缺少 total_audits 字段"
    
    print(f"   ✓ 趋势数据点数: {len(trends['trend_data'])}")
    print(f"   ✓ 总审计数: {trends['total_audits']}")
    print(f"   ✓ 风险分布: {trends['severity_distribution']}")
    
    # 测试获取洞察
    print("\n1.2 获取智能洞察:")
    insights = service.get_insights()
    assert "insights" in insights, "缺少 insights 字段"
    assert "generated_at" in insights, "缺少 generated_at 字段"
    
    print(f"   ✓ 洞察数量: {len(insights['insights'])}")
    for insight in insights['insights']:
        print(f"   ✓ - [{insight['type']}] {insight['title']}")
    
    print("\n✅ 测试1通过: 统计服务基础功能正常\n")
    return True


def test_skill_comparison():
    """测试Skill对比功能"""
    print("=" * 60)
    print("测试2: Skill版本对比功能")
    print("=" * 60)
    
    from app.services.audit_statistics_service import AuditStatisticsService
    
    service = AuditStatisticsService()
    
    # 测试一个可能存在的Skill名称
    print("\n2.1 查询Skill对比 (使用示例名称):")
    comparison = service.get_skill_comparison("test-skill-demo")
    
    assert "skill_name" in comparison, "缺少 skill_name 字段"
    assert "versions" in comparison, "缺少 versions 字段"
    assert "trend" in comparison, "缺少 trend 字段"
    
    print(f"   ✓ Skill名称: {comparison['skill_name']}")
    print(f"   ✓ 审计次数: {comparison['total_audits']}")
    print(f"   ✓ 风险趋势: {comparison['trend']}")
    
    if comparison['versions']:
        print(f"   ✓ 最新版本风险等级: {comparison['versions'][0]['risk_level']}")
    
    print("\n✅ 测试2通过: Skill对比功能正常\n")
    return True


def test_api_routes():
    """测试API路由"""
    print("=" * 60)
    print("测试3: API路由注册")
    print("=" * 60)
    
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # 测试趋势接口
    print("\n3.1 测试 GET /api/statistics/trends:")
    response = client.get("/api/statistics/trends?days=7")
    assert response.status_code == 200, f"状态码错误: {response.status_code}"
    data = response.json()
    assert data.get("success") == True, "返回success不为True"
    print(f"   ✓ 状态码: {response.status_code}")
    print(f"   ✓ 响应成功: {data['success']}")
    
    # 测试洞察接口
    print("\n3.2 测试 GET /api/statistics/insights:")
    response = client.get("/api/statistics/insights")
    assert response.status_code == 200, f"状态码错误: {response.status_code}"
    data = response.json()
    assert data.get("success") == True, "返回success不为True"
    print(f"   ✓ 状态码: {response.status_code}")
    print(f"   ✓ 响应成功: {data['success']}")
    
    # 测试Skill对比接口（使用示例名称）
    print("\n3.3 测试 GET /api/statistics/skill-comparison/test-skill-demo:")
    response = client.get("/api/statistics/skill-comparison/test-skill-demo")
    assert response.status_code == 200, f"状态码错误: {response.status_code}"
    data = response.json()
    assert data.get("success") == True, "返回success不为True"
    print(f"   ✓ 状态码: {response.status_code}")
    print(f"   ✓ 响应成功: {data['success']}")
    
    print("\n✅ 测试3通过: API路由正常工作\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("OpenClaw 审计统计分析功能 - 测试套件")
    print("=" * 60 + "\n")
    
    tests = [
        ("统计服务基础功能", test_statistics_service),
        ("Skill版本对比功能", test_skill_comparison),
        ("API路由注册", test_api_routes),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ 测试失败: {test_name}")
            print(f"   错误: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ 测试异常: {test_name}")
            print(f"   错误: {str(e)}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！统计分析功能完全正常！\n")
        print("💡 提示:")
        print("   1. 启动后端: uvicorn app.main:app --reload")
        print("   2. 启动前端: cd frontend && npm run dev")
        print("   3. 访问: http://localhost:3000/statistics")
        print()
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查错误信息\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
