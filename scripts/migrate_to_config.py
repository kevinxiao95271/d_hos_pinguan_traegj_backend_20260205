#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将所有脚本迁移到使用配置文件"""

import os
import re
import glob

# 旧的硬编码配置模式
OLD_DB_CONFIG = """DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}"""

OLD_DB_CONFIG_DICT = """{
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}"""

OLD_DB_CONFIG_KWARGS = """host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'"""

# 新的配置导入
NEW_IMPORT = "from db_config import DB_CONFIG"

# 服务器配置
OLD_SERVER_CONFIG = '''SERVER = "81.71.44.180"
USER = "root"
PASSWORD = "Yiguo9527_"'''

NEW_SERVER_IMPORT = "from db_config import SERVER_CONFIG"

def migrate_file(filepath):
    """迁移单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # 检查是否包含敏感信息
        if 'Yiguo9527_' not in content:
            return False
        
        # 替换数据库配置
        if 'DB_CONFIG = {' in content and 'Yiguo9527_' in content:
            # 添加导入
            if 'from db_config import DB_CONFIG' not in content:
                # 在第一个import后添加
                import_match = re.search(r'(import \w+\n)', content)
                if import_match:
                    pos = import_match.end()
                    content = content[:pos] + NEW_IMPORT + '\n' + content[pos:]
                else:
                    # 在文件开头添加
                    content = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n' + NEW_IMPORT + '\n\n' + content
            
            # 删除旧的DB_CONFIG定义
            content = re.sub(
                r'DB_CONFIG = \{[^}]+\}',
                '# DB_CONFIG imported from db_config.py',
                content,
                flags=re.DOTALL
            )
            modified = True
        
        # 替换pymysql.connect参数
        if 'pymysql.connect(' in content and 'Yiguo9527_' in content:
            if 'from db_config import DB_CONFIG' not in content:
                import_match = re.search(r'(import \w+\n)', content)
                if import_match:
                    pos = import_match.end()
                    content = content[:pos] + NEW_IMPORT + '\n' + content[pos:]
            
            # 替换connect调用
            content = re.sub(
                r'pymysql\.connect\([^)]+\)',
                'pymysql.connect(**DB_CONFIG)',
                content
            )
            modified = True
        
        # 替换服务器配置
        if 'SERVER = "81.71.44.180"' in content:
            if 'from db_config import SERVER_CONFIG' not in content:
                import_match = re.search(r'(import \w+\n)', content)
                if import_match:
                    pos = import_match.end()
                    content = content[:pos] + NEW_SERVER_IMPORT + '\n' + content[pos:]
            
            content = content.replace(OLD_SERVER_CONFIG, '# SERVER_CONFIG imported from db_config.py')
            content = content.replace('SERVER', 'SERVER_CONFIG["host"]')
            content = content.replace('USER', 'SERVER_CONFIG["user"]')
            content = content.replace('PASSWORD', 'SERVER_CONFIG["password"]')
            modified = True
        
        if modified and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"错误处理 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("开始迁移脚本...")
    print("=" * 60)
    
    # 获取所有Python脚本
    script_files = glob.glob('scripts/*.py')
    
    migrated = []
    skipped = []
    
    for filepath in script_files:
        filename = os.path.basename(filepath)
        
        # 跳过配置文件本身
        if filename in ['db_config.py', 'db_config.example.py', 'migrate_to_config.py']:
            continue
        
        if migrate_file(filepath):
            migrated.append(filename)
            print(f"✓ {filename}")
        else:
            skipped.append(filename)
    
    print("=" * 60)
    print(f"\n迁移完成！")
    print(f"已迁移: {len(migrated)} 个文件")
    print(f"跳过: {len(skipped)} 个文件")
    
    if migrated:
        print("\n已迁移的文件:")
        for f in migrated:
            print(f"  - {f}")
    
    print("\n注意事项:")
    print("1. 请手动检查迁移后的文件")
    print("2. 确保 db_config.py 已正确配置")
    print("3. 测试所有脚本是否正常工作")

if __name__ == '__main__':
    main()
