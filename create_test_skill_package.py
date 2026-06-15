#!/usr/bin/env python3
"""
创建一个有效的Skill包用于测试AI预处理功能
"""

import os
import json
import zipfile
from pathlib import Path

def create_test_skill():
    """创建一个包含代码文件的测试Skill包"""
    
    print("=" * 80)
    print(" 创建测试Skill包")
    print("=" * 80)
    print()
    
    # 创建临时目录
    skill_dir = Path("temp_test_skill")
    skill_dir.mkdir(exist_ok=True)
    
    print(" 正在创建Skill包文件...")
    
    # 1. 创建SKILL.md
    skill_md = """# Test Skill for AI Preprocessing

## Description
这是一个用于测试AI预处理功能的示例Skill包。

## Features
- 包含Python代码文件
- 包含大文件（超过50行）
- 用于验证预处理功能

## Usage
使用此Skill包可以测试AI预处理功能的完整流程。
"""
    (skill_dir / "SKILL.md").write_text(skill_md, encoding='utf-8')
    print("   SKILL.md")
    
    # 2. 创建manifest.yaml
    manifest = """name: ai-preprocessing-test-skill
version: "1.0.0"
description: "Test skill for AI preprocessing validation"
author: "OpenClaw Team"
"""
    (skill_dir / "manifest.yaml").write_text(manifest, encoding='utf-8')
    print("   manifest.yaml")
    
    # 3. 创建主代码文件（超过50行）
    main_py = '''#!/usr/bin/env python3
"""
主程序文件 - 包含超过50行的代码
用于测试AI预处理功能
"""

import os
import sys
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理类"""
    
    def __init__(self, config_path: str = None):
        self.config = {}
        self.data = []
        self.processed_count = 0
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Config loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}
    
    def process_data(self, input_data: List[Dict]) -> List[Dict]:
        """处理数据"""
        results = []
        
        for item in input_data:
            try:
                # 数据验证
                if not self.validate_item(item):
                    logger.warning(f"Invalid item: {item}")
                    continue
                
                # 数据处理
                processed = self.transform_item(item)
                results.append(processed)
                self.processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue
        
        return results
    
    def validate_item(self, item: Dict) -> bool:
        """验证数据项"""
        required_fields = ['id', 'name', 'value']
        
        for field in required_fields:
            if field not in item:
                return False
        
        return True
    
    def transform_item(self, item: Dict) -> Dict:
        """转换数据项"""
        transformed = {
            'id': item['id'],
            'name': item['name'].strip().lower(),
            'value': float(item['value']),
            'timestamp': datetime.now().isoformat(),
            'hash': self.compute_hash(item)
        }
        
        return transformed
    
    def compute_hash(self, data: Dict) -> str:
        """计算数据哈希"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'processed_count': self.processed_count,
            'config_loaded': bool(self.config),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """主函数"""
    print("Starting data processing...")
    
    # 创建处理器
    processor = DataProcessor()
    
    # 示例数据
    sample_data = [
        {'id': 1, 'name': 'Item 1', 'value': '100.5'},
        {'id': 2, 'name': 'Item 2', 'value': '200.3'},
        {'id': 3, 'name': 'Item 3', 'value': '300.7'},
    ]
    
    # 处理数据
    results = processor.process_data(sample_data)
    
    # 输出结果
    print(f"Processed {len(results)} items")
    
    stats = processor.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
    
    return results


if __name__ == "__main__":
    main()
'''
    (skill_dir / "main.py").write_text(main_py, encoding='utf-8')
    print("   main.py (156行)")
    
    # 4. 创建utils目录
    utils_dir = skill_dir / "utils"
    utils_dir.mkdir(exist_ok=True)
    
    # 5. 创建工具文件（超过50行）
    helper_py = '''#!/usr/bin/env python3
"""
工具函数库 - 包含超过50行的代码
用于测试AI预处理功能
"""

import os
import re
import json
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta


class FileHandler:
    """文件处理工具类"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.supported_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml'}
    
    def find_files(self, pattern: str = "*") -> List[Path]:
        """查找匹配的文件"""
        files = list(self.base_path.rglob(pattern))
        return [f for f in files if f.suffix in self.supported_extensions]
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def write_file(self, file_path: Path, content: str) -> bool:
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def get_file_stats(self, file_path: Path) -> Dict[str, Any]:
        """获取文件统计信息"""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        
        return {
            'path': str(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'extension': file_path.suffix,
            'name': file_path.name
        }


def format_json(data: Any, indent: int = 2) -> str:
    """格式化JSON输出"""
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def extract_emails(text: str) -> List[str]:
    """从文本中提取邮箱"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_timestamp() -> str:
    """生成时间戳"""
    return datetime.now().isoformat()


def calculate_expiry(days: int = 30) -> str:
    """计算过期时间"""
    expiry = datetime.now() + timedelta(days=days)
    return expiry.isoformat()


if __name__ == "__main__":
    # 测试代码
    handler = FileHandler(".")
    files = handler.find_files("*.py")
    print(f"Found {len(files)} Python files")
    
    for f in files[:3]:
        stats = handler.get_file_stats(f)
        print(f"  - {stats.get('name')} ({stats.get('size')} bytes)")
'''
    (utils_dir / "helper.py").write_text(helper_py, encoding='utf-8')
    print("   utils/helper.py (141行)")
    
    # 6. 创建config目录
    config_dir = skill_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    # 7. 创建配置文件
    config_json = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db"
        },
        "cache": {
            "enabled": True,
            "ttl": 3600
        },
        "logging": {
            "level": "INFO",
            "file": "app.log"
        }
    }
    (config_dir / "config.json").write_text(
        json.dumps(config_json, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print("   config/config.json")
    
    # 8. 创建README
    readme = """# AI Preprocessing Test Skill

这个Skill包用于测试AI预处理功能。

## 文件结构

```
ai-preprocessing-test-skill/
├── SKILL.md              # Skill描述文件
├── manifest.yaml         # 清单文件
├── main.py               # 主程序（156行）
├── utils/
│   └── helper.py         # 工具函数（141行）
└── config/
    └── config.json       # 配置文件
```

## 测试说明

1. 将此目录打包为ZIP文件
2. 上传到OpenClaw平台
3. 勾选"AI预处理"选项
4. 运行审计
5. 查看报告中的预处理信息

## 预期结果

- 分析文件数: 2 (main.py 和 helper.py)
- 预处理文件数: 2 (都超过50行)
- 压缩比: 约30%
"""
    (skill_dir / "README.md").write_text(readme, encoding='utf-8')
    print("   README.md")
    
    # 9. 打包为ZIP
    zip_path = Path("data/uploads/ai-preprocessing-test-skill.zip")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n 正在打包...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)
    
    print(f" 已创建: {zip_path}")
    
    # 统计信息
    print("\n" + "=" * 80)
    print(" Skill包统计")
    print("=" * 80)
    print(f" 总文件数: {sum(1 for _ in skill_dir.rglob('*') if _.is_file())}")
    print(f" 代码文件数: 2 (main.py, utils/helper.py)")
    print(f" 总代码行数: 297")
    print(f" ZIP文件大小: {zip_path.stat().st_size} bytes")
    print()
    print(" 下一步:")
    print(f"  1. 上传文件: {zip_path}")
    print("  2. 访问: http://localhost:5173/audit/new")
    print("  3. 勾选'AI预处理'选项")
    print("  4. 开始审计并查看报告")
    print()
    
    # 清理临时目录
    import shutil
    shutil.rmtree(skill_dir)
    print(" 已清理临时目录")


if __name__ == "__main__":
    create_test_skill()
