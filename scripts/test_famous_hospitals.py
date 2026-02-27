# -*- coding: utf-8 -*-
"""
测试知名医院的简称搜索效果
"""
import pymysql
import requests
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

api_url = "http://localhost:6031/api/institutions/search"

# 测试医院列表（简称 -> 关键词映射）
test_hospitals = {
    "浙二医院": {"keywords": ["浙二", "浙江大学医学院附属第二医院"], "city": "杭州市"},
    "浙江省中医院": {"keywords": ["省中医", "浙江省中医"], "city": "杭州市"},
    "杭州市中医院": {"keywords": ["杭州市中医"], "city": "杭州市"},
    "邵逸夫医院": {"keywords": ["邵逸夫"], "city": "杭州市"},
    "浙江省妇保医院": {"keywords": ["省妇保", "妇女保健"], "city": "杭州市"},
    "浙江省立同德医院": {"keywords": ["同德"], "city": "杭州市"},
    "浙江医院": {"keywords": ["浙江医院"], "city": "杭州市"},
    "浙一医院": {"keywords": ["浙一", "浙江大学医学院附属第一医院"], "city": "杭州市"},
    "浙江省人民医院": {"keywords": ["省人民", "浙江省人民"], "city": "杭州市"},
    "杭州市第一人民医院": {"keywords": ["杭州市第一", "杭州第一"], "city": "杭州市"},
    "浙江省儿童医院": {"keywords": ["儿童医院", "省儿童"], "city": "杭州市"},
    "浙江省中西医结合医院": {"keywords": ["中西医结合"], "city": "杭州市"},
    "浙江省肿瘤医院": {"keywords": ["肿瘤医院", "省肿瘤"], "city": "杭州市"},
    "浙江省口腔医院": {"keywords": ["口腔医院", "省口腔"], "city": "杭州市"},
    "杭州市肝病研究所": {"keywords": ["肝病研究"], "city": "杭州市"},
    "宁波第一医院": {"keywords": ["宁波第一", "宁波市第一"], "city": "宁波市"},
    "宁波第二医院": {"keywords": ["宁波第二", "宁波市第二"], "city": "宁波市"},
    "113医院": {"keywords": ["113", "一一三"], "city": "宁波市"},
    "李惠利医院": {"keywords": ["李惠利"], "city": "宁波市"},
    "温医二院": {"keywords": ["温州医科大学", "附属第二"], "city": "温州市"},
    "浙江省立温州第一医院": {"keywords": ["温州第一", "省立温州"], "city": "温州市"},
}

print("=" * 100)
print("知名医院简称搜索测试")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

results = []

for short_name, config in test_hospitals.items():
    keywords = config['keywords']
    city = config['city']
    
    print(f"\n[测试] {short_name} ({city})")
    print("-" * 100)
    
    # 1. 先在数据库中查找该医院
    found_hospital = None
    for keyword in keywords:
        cursor.execute("""
            SELECT name, region, city, level
            FROM const_init_institutions
            WHERE name LIKE %s
            LIMIT 1
        """, (f"%{keyword}%",))
        
        hospital = cursor.fetchone()
        if hospital:
            found_hospital = hospital
            print(f"  ✓ 找到医院: {hospital['name']}")
            print(f"    等级: {hospital['level'] or '[空]'}")
            print(f"    地区: {hospital['region'] or hospital['city']}")
            break
    
    if not found_hospital:
        print(f"  ✗ 数据库中未找到匹配的医院，跳过")
        results.append({
            'short_name': short_name,
            'status': '未找到',
            'position': '-',
            'level': '-'
        })
        continue
    
    # 2. 用城市+主关键词搜索
    search_keyword = keywords[0]
    
    try:
        response = requests.post(api_url, json={
            "keyword": search_keyword,
            "region": city,
            "page": 0,
            "size": 20
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()['data']
            content = data.get('content', [])
            
            # 查找该医院的排名
            position = -1
            for idx, item in enumerate(content):
                if item['name'] == found_hospital['name']:
                    position = idx + 1
                    break
            
            if position > 0:
                if position <= 3:
                    status_icon = "🥇" if position == 1 else "🥈" if position == 2 else "🥉"
                    print(f"  {status_icon} 排名: #{position} / {data['totalElements']}")
                else:
                    print(f"  📍 排名: #{position} / {data['totalElements']}")
                
                results.append({
                    'short_name': short_name,
                    'full_name': found_hospital['name'][:40],
                    'status': '找到',
                    'position': position,
                    'level': found_hospital['level'] or '[空]',
                    'search': f"{city} + {search_keyword}"
                })
            else:
                print(f"  ✗ 搜索结果中未找到该医院")
                results.append({
                    'short_name': short_name,
                    'status': '搜索未找到',
                    'position': '-',
                    'level': found_hospital['level'] or '[空]'
                })
        else:
            print(f"  ✗ API请求失败: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 错误: {e}")

cursor.close()
conn.close()

# 汇总结果
print("\n" + "=" * 100)
print("测试结果汇总")
print("=" * 100)

found_count = len([r for r in results if r['status'] == '找到'])
not_in_db = len([r for r in results if r['status'] == '未找到'])
not_in_search = len([r for r in results if r['status'] == '搜索未找到'])

print(f"\n总测试数: {len(test_hospitals)} 家知名医院")
print(f"  数据库中找到: {found_count} 家")
print(f"  数据库中未找到: {not_in_db} 家")
print(f"  搜索未找到: {not_in_search} 家")

if found_count > 0:
    top1 = len([r for r in results if r.get('position') == 1])
    top3 = len([r for r in results if isinstance(r.get('position'), int) and r['position'] <= 3])
    top5 = len([r for r in results if isinstance(r.get('position'), int) and r['position'] <= 5])
    top10 = len([r for r in results if isinstance(r.get('position'), int) and r['position'] <= 10])
    
    print(f"\n排名分布 (基于{found_count}家找到的医院):")
    print(f"  排第1名: {top1} 家 ({top1/found_count*100:.1f}%)")
    print(f"  排前3名: {top3} 家 ({top3/found_count*100:.1f}%)")
    print(f"  排前5名: {top5} 家 ({top5/found_count*100:.1f}%)")
    print(f"  排前10名: {top10} 家 ({top10/found_count*100:.1f}%)")

# 详细列表
print("\n" + "=" * 100)
print("详细结果")
print("=" * 100)
print(f"{'简称':<20} {'排名':<8} {'等级':<8} {'搜索条件':<25} {'状态'}")
print("-" * 100)

for r in results:
    short_name = r['short_name'][:18]
    position = f"#{r['position']}" if isinstance(r['position'], int) else r['position']
    level = r.get('level', '-')
    search = r.get('search', '-')[:23]
    status = r['status']
    
    print(f"{short_name:<20} {position:<8} {level:<8} {search:<25} {status}")

print("\n" + "=" * 100)
