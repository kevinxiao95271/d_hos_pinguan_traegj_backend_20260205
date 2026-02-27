# -*- coding: utf-8 -*-
"""
测试GET接口的排序
"""
import requests
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

print("=" * 80)
print("测试GET接口排序")
print("=" * 80)

try:
    response = requests.get("http://localhost:6031/api/institutions/search", params={
        "keyword": "人民",
        "page": 0,
        "size": 20
    })
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"\n状态: 200 OK")
        print(f"总数: {data['totalElements']}")
        print(f"返回: {len(data['content'])} 条\n")
        
        if data['content']:
            print("前20条结果:")
            print("-" * 80)
            for i, item in enumerate(data['content'], 1):
                level = item.get('level') or '[空]'
                name = item['name'][:45]
                print(f"{i:2}. {name:<47} | {level}")
            
            # 统计等级分布
            level_count = {}
            for item in data['content']:
                level = item.get('level') or '[空]'
                level_count[level] = level_count.get(level, 0) + 1
            
            print(f"\n等级分布:")
            for level, count in sorted(level_count.items()):
                print(f"  {level:<15}: {count} 条")
        else:
            print("没有返回数据")
            
    else:
        print(f"[FAIL] HTTP {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
