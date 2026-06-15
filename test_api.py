"""测试后端 API"""
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # 测试健康检查
        res = await client.get('http://localhost:8000/api/v1/health')
        print(f"Health Status: {res.status_code}")
        print(res.text[:200])
        
        # 测试审计列表
        res2 = await client.get('http://localhost:8000/api/v1/audits')
        print(f"\nAudits Status: {res2.status_code}")
        if res2.status_code == 200:
            data = res2.json()
            print(f"Total audits: {data.get('total', 0)}")

if __name__ == '__main__':
    asyncio.run(test_api())
