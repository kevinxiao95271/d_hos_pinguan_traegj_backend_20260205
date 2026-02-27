# -*- coding: utf-8 -*-
"""
测试：选择杭州+关键词"人民"的搜索结果
"""
import requests
import json

base_url = "http://localhost:8080/api/institutions"

print("=" * 80)
print("测试：杭州 + 人民")
print("=" * 80)

# 测试1: 只选杭州，关键词"人民"
print("\n[测试1] region=杭州市, keyword=人民")
print("-" * 80)

response = requests.get(f"{base_url}/search-v2", params={
    "region": "杭州市",
    "keyword": "人民",
    "page": 0,
    "size": 20
})

if response.status_code == 200:
    data = response.json()['data']
    print(f"总数: {data['totalElements']}")
    print(f"返回: {len(data['content'])} 条\n")
    
    # 统计region分布
    region_count = {}
    for item in data['content']:
        region = item.get('region', '[空]')
        region_count[region] = region_count.get(region, 0) + 1
    
    print("Region分布:")
    for region, count in sorted(region_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {region:<15}: {count} 个")
    
    # 显示前10条
    print(f"\n前10条医院:")
    for i, item in enumerate(data['content'][:10], 1):
        print(f"  {i}. {item['name'][:50]}")
        print(f"     region: {item.get('region', '[空]')}")
        print(f"     level: {item.get('level', '[空]')}")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)

# 测试2: 直接搜索建德
print("\n\n[测试2] region=建德市, keyword=人民")
print("-" * 80)

response = requests.get(f"{base_url}/search-v2", params={
    "region": "建德市",
    "keyword": "人民",
    "page": 0,
    "size": 20
})

if response.status_code == 200:
    data = response.json()['data']
    print(f"总数: {data['totalElements']}")
    print(f"\n建德的人民医院:")
    for i, item in enumerate(data['content'], 1):
        print(f"  {i}. {item['name']}")
        print(f"     region: {item.get('region')}")

print("\n" + "=" * 80)
