"""重新审计脚本 - 生成包含新分点建议的报告"""
import httpx
import asyncio
import json

async def re_audit():
    skill_id = '4bd162c6c6bf4fdb984ec2d60a15e4b6'  # ai-preprocessing-test-skill
    
    print("开始重新审计 Skill...")
    print(f"Skill ID: {skill_id}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 发起审计 - 使用正确的端点 /api/audits/run (不带 v1)
        res = await client.post(
            'http://localhost:8000/api/audits/run',  # 修正：去掉 v1
            json={
                'skill_id': skill_id,
                'options': {
                    'semantic': True,
                    'static_security': True,
                    'dependency_check': True,
                    'ai_preprocessing': True
                }
            }
        )
        
        if res.status_code == 200:
            data = res.json()
            audit_id = data.get('audit_id') or data.get('report_id') or data.get('id')
            print(f"✅ 审计任务已创建!")
            print(f"审计 ID: {audit_id}")
            print(f"\n等待审计完成...")
            
            # 等待审计完成
            import time
            time.sleep(5)  # 等待几秒
            
            # 检查审计状态
            status_res = await client.get(f'http://localhost:8000/api/audits/{audit_id}')
            if status_res.status_code == 200:
                status_data = status_res.json()
                print(f"\n✅ 审计完成!")
                
                # 获取报告
                report_id = status_data.get('report_id') or audit_id
                if report_id:
                    print(f"📄 报告 ID: {report_id}")
                    print(f"📋 报告链接: http://localhost:3000/report/{report_id}")
                    print(f"\n 请访问上述链接查看更新后的分点建议!")
        else:
            print(f"❌ 审计失败: {res.status_code}")
            print(f"错误信息: {res.text}")

if __name__ == '__main__':
    asyncio.run(re_audit())
