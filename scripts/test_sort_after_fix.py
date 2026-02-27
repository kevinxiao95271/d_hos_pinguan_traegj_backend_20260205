# -*- coding: utf-8 -*-
"""
测试修复后的排序功能
"""
import requests
import json
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

base_url = "http://localhost:6031"

print("=" * 80)
print("测试排序修复 - 杭州 + 人民")
print("=" * 80)

# 测试GET接口
print("\n[测试1] GET /api/institutions/search?keyword=杭州 人民")
print("-" * 80)

try:
    response = requests.get(f"{base_url}/api/institutions/search", params={
        "keyword": "杭州 人民",
        "page": 0,
        "size": 15
    })
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"状态: 200 OK")
        print(f"总数: {data['totalElements']}")
        print(f"返回: {len(data['content'])} 条\n")
        
        print("前15条结果:")
        for i, item in enumerate(data['content'], 1):
            level = item.get('level', '[空]')
            name = item['name'][:50]
            region = item.get('region', '[空]')
            print(f"{i:2}. {name:<52} | {region:<10} | {level}")
        
        # 统计等级分布
        level_count = {}
        for item in data['content']:
            level = item.get('level', '[空]')
            level_count[level] = level_count.get(level, 0) + 1
        
        print(f"\n等级分布:")
        for level, count in sorted(level_count.items()):
            print(f"  {level:<15}: {count} 条")
            
    else:
        print(f"[FAIL] HTTP {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"[ERROR] {e}")

# 测试POST接口
print("\n\n[测试2] POST /api/institutions/search")
print("-" * 80)

try:
    response = requests.post(f"{base_url}/api/institutions/search", json={
        "keyword": "人民",
        "region": "杭州市",
        "page": 0,
        "size": 15
    })
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"状态: 200 OK")
        print(f"总数: {data['totalElements']}")
        print(f"返回: {len(data['content'])} 条\n")
        
        print("前15条结果:")
        for i, item in enumerate(data['content'], 1):
            level = item.get('level', '[空]')
            name = item['name'][:50]
            region = item.get('region', '[空]')
            print(f"{i:2}. {name:<52} | {region:<10} | {level}")
        
        # 统计等级分布
        level_count = {}
        for item in data['content']:
            level = item.get('level', '[空]')
            level_count[level] = level_count.get(level, 0) + 1
        
        print(f"\n等级分布:")
        for level, count in sorted(level_count.items()):
            print(f"  {level:<15}: {count} 条")
            
    else:
        print(f"[FAIL] HTTP {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
