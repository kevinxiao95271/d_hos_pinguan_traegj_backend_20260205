#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行所有入围管理测试"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import time
import subprocess
import requests

BASE = "http://localhost:6031"

print("="*80)
print("入围管理API完整测试")
print("="*80)

# 等待服务器启动
print("\n等待服务器启动...")
max_wait = 60  # 最多等待60秒
wait_time = 0

while wait_time < max_wait:
    try:
        resp = requests.get(f"{BASE}/actuator/health", timeout=2)
        if resp.status_code == 200:
            print(f"✅ 服务器已启动（耗时{wait_time}秒）")
            break
    except:
        pass
    
    time.sleep(2)
    wait_time += 2
    print(f"  等待中... ({wait_time}s/{max_wait}s)")

if wait_time >= max_wait:
    print("❌ 服务器启动超时")
    exit(1)

# 运行测试
tests = [
    ("步骤1: 书审排名", "scripts/test_step1_book_rankings.py"),
    ("步骤2: 面谈排名", "scripts/test_step2_interview_rankings.py"),
    ("步骤3: 数据合并和综合排名", "scripts/test_step3_merge_and_rank.py"),
    ("步骤4: 项目详细评分", "scripts/test_step4_project_details.py"),
]

for name, script in tests:
    print(f"\n\n{'='*80}")
    print(f"运行: {name}")
    print(f"{'='*80}\n")
    
    result = subprocess.run([sys.executable, script], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {name} 失败")
        exit(1)
    
    print(f"\n✅ {name} 完成")
    time.sleep(1)

print(f"\n\n{'='*80}")
print("✅ 所有测试完成！")
print(f"{'='*80}")
