"""加载测试样本脚本。

规则描述：
- 放置开发调试用样本导入逻辑。
"""
import sys
from pathlib import Path
import json
import datetime
import uuid

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_sample_data():
    """加载示例数据到JSON文件"""
    db_path = Path("data/skills.json")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已有数据
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('items') and len(data['items']) > 0:
            print("Sample data already exists, skipping...")
            return
    
    print("Loading sample data...")
    
    # 创建示例Skill
    skills = [
        {
            "id": uuid.uuid4().hex,
            "name": "example-skill-1.zip",
            "filename": "example1.zip",
            "path": "./data/uploads/example1.zip",
            "size": 10240,
            "risk_level": "low",
            "status": "uploaded",
            "created_at": datetime.datetime.utcnow().isoformat()
        },
        {
            "id": uuid.uuid4().hex,
            "name": "example-skill-2.tar.gz",
            "filename": "example2.tar.gz",
            "path": "./data/uploads/example2.tar.gz",
            "size": 20480,
            "risk_level": "medium",
            "status": "uploaded",
            "created_at": datetime.datetime.utcnow().isoformat()
        },
    ]
    
    data = {"items": skills}
    db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"✓ Created {len(skills)} sample skills")
    print("Sample data loaded successfully!")

if __name__ == "__main__":
    load_sample_data()