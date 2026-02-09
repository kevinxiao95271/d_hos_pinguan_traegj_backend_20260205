#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量清理所有文件中的密码"""

import os
import re

# 需要清理的文件列表
files_to_clean = [
    'scripts/cleanup_singular_tables.py',
    'scripts/check_data.py',
    'scripts/explore_plural_tables.py',
    'scripts/explore_existing_data.py',
    'scripts/full_data_report.py',
    'scripts/init_tables.py',
    'scripts/utf8_helper.py',
    'deploy_to_server.ps1',
    'deploy_manual_steps.txt',
    'docs/历史数据功能开发总结.md',
]

def clean_file(filepath):
    """清理单个文件"""
    if not os.path.exists(filepath):
        print(f"跳过: {filepath} (不存在)")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 替换数据库配置
        content = re.sub(
            r"'password':\s*'Yiguo9527_'",
            "'password': 'your-password'",
            content
        )
        content = re.sub(
            r'"password":\s*"Yiguo9527_"',
            '"password": "your-password"',
            content
        )
        content = re.sub(
            r'password=\'Yiguo9527_\'',
            "password='your-password'",
            content
        )
        content = re.sub(
            r'password="Yiguo9527_"',
            'password="your-password"',
            content
        )
        content = re.sub(
            r'PINGUAN_DS1_PASSWORD=Yiguo9527_',
            'PINGUAN_DS1_PASSWORD=your-password',
            content
        )
        content = re.sub(
            r'\$PASSWORD\s*=\s*"Yiguo9527_"',
            '$PASSWORD = "your-password"',
            content
        )
        content = re.sub(
            r'密码:\s*Yiguo9527_',
            '密码: your-password',
            content
        )
        
        # 替换服务器IP
        content = re.sub(
            r'81\.71\.44\.180',
            'your-server-ip',
            content
        )
        
        # 替换数据库主机
        content = re.sub(
            r'gz-cdb-bq7gk3k5\.sql\.tencentcdb\.com',
            'your-db-host',
            content
        )
        content = re.sub(
            r':63606',
            ':3306',
            content
        )
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}")
            return True
        else:
            print(f"- {filepath} (无需修改)")
            return False
            
    except Exception as e:
        print(f"✗ {filepath}: {e}")
        return False

def main():
    print("开始批量清理密码...")
    print("=" * 60)
    
    cleaned = 0
    for filepath in files_to_clean:
        if clean_file(filepath):
            cleaned += 1
    
    print("=" * 60)
    print(f"完成！已清理 {cleaned} 个文件")

if __name__ == '__main__':
    main()
