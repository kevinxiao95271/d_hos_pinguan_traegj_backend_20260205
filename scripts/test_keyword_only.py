# -*- coding: utf-8 -*-
"""
测试纯关键词搜索（不加城市筛选）
"""
import requests
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

api_url = "http://localhost:6031/api/institutions/search"

test_cases = [
    {"keyword": "浙二", "expected": "浙江大学医学院附属第二医院"},
    {"keyword": "邵逸夫", "expected": "浙江大学医学院附属邵逸夫医院"},
    {"keyword": "浙江医院", "expected": "浙江医院"},
    {"keyword": "浙江省肿瘤", "expected": "浙江省肿瘤医院"},
    {"keyword": "李惠利", "expected": "宁波市医疗中心李惠利医院"},
    {"keyword": "省人民", "expected": "浙江省人民医院"},
]

print("=" * 100)
print("纯关键词搜索测试（不加城市筛选）")
print("=" * 100)

for test in test_cases:
    keyword = test['keyword']
    expected = test['expected']
    
    print(f"\n[测试] 关键词: {keyword}")
    print("-" * 100)
    
    try:
        # 只用关键词，不用region
        response = requests.post(api_url, json={
            "keyword": keyword,
            "page": 0,
            "size": 10
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()['data']
            content = data.get('content', [])
            
            print(f"  总数: {data['totalElements']} | 返回: {len(content)} 条\n")
            
            # 查找目标医院
            position = -1
            for idx, item in enumerate(content):
                if expected in item['name']:
                    position = idx + 1
                    icon = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else "📍"
                    print(f"  {icon} 目标医院排名: #{position}")
                    print(f"     {item['name']}")
                    print(f"     等级: {item.get('level', '[空]')}")
                    break
            
            if position == -1:
                print(f"  ✗ 未找到目标医院: {expected}")
            
            # 显示前3条
            print(f"\n  前3条结果:")
            for idx, item in enumerate(content[:3], 1):
                level = item.get('level', '[空]')
                name = item['name'][:55]
                print(f"    {idx}. {name:<57} | {level}")
                
        else:
            print(f"  ✗ API错误: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ 异常: {e}")

print("\n" + "=" * 100)
