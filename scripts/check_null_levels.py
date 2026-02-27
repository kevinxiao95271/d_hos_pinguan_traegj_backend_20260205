# -*- coding: utf-8 -*-
"""
检查数据库中没有等级的机构数量
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("检查无等级机构数量")
print("=" * 100)

# 1. 检查总机构数
print("\n[测试1] 无条件搜索 - 查看总机构数")
response = requests.post(
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "",
        "level": "",
        "page": 0,
        "size": 1
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        total = data.get('data', {}).get('totalElements', 0)
        print(f"  总机构数: {total}")

# 2. 检查有等级的机构数
print("\n[测试2] 有等级的机构数")
levels = ['一级', '二级', '三级']
level_count = 0

for level in levels:
    response = requests.post(
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": "",
            "region": "",
            "level": level,
            "page": 0,
            "size": 1
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            count = data.get('data', {}).get('totalElements', 0)
            level_count += count
            print(f"  {level}: {count} 个")

print(f"  有等级机构总计: {level_count} 个")

# 3. 计算无等级机构数
if total > 0 and level_count > 0:
    no_level_count = total - level_count
    print(f"\n[结果] 无等级机构: {no_level_count} 个")
    print(f"  占比: {no_level_count * 100 / total:.2f}%")
    
    print(f"\n[建议] 需要在字典表中添加'无等级'选项，用于筛选这 {no_level_count} 个机构")

print("\n" + "=" * 100)
