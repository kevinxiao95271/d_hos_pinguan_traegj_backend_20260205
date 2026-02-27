# -*- coding: utf-8 -*-
"""
测试所有三级医院是否能排在前面
"""
import pymysql
import requests
import re
import sys
from collections import defaultdict

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

api_url = "http://localhost:6031/api/institutions/search"

print("=" * 100)
print("三级医院排序测试")
print("=" * 100)

# 1. 从数据库获取所有三级医院
print("\n[1] 从数据库获取所有三级医院...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

cursor.execute("""
    SELECT id, name, region, city, level
    FROM const_init_institutions
    WHERE level = '三级'
    ORDER BY name
""")

level3_hospitals = cursor.fetchall()
print(f"找到 {len(level3_hospitals)} 家三级医院")

cursor.close()
conn.close()

# 2. 提取有意义的关键词（排除太宽泛的词）
keywords = ['第一', '第二', '第三', '中心', '人民', '浙江', '附属', '妇幼', '儿童', '肿瘤', '传染', '精神', '康复']

print(f"\n[2] 有意义的关键词列表: {keywords}")

# 3. 为每家医院提取关键词和城市
test_cases = []

for hospital in level3_hospitals:
    name = hospital['name']
    city = hospital.get('city') or hospital.get('region') or ''
    
    # 提取名称中的关键词
    found_keywords = []
    for kw in keywords:
        if kw in name:
            found_keywords.append(kw)
    
    if found_keywords and city:
        # 使用第一个关键词作为搜索词
        search_keyword = found_keywords[0]
        test_cases.append({
            'hospital': hospital,
            'city': city,
            'keyword': search_keyword,
            'full_name': name
        })

print(f"\n[3] 生成 {len(test_cases)} 个测试用例")

# 4. 执行搜索测试
print(f"\n[4] 开始测试...")
print("-" * 100)

results = {
    'top1': 0,      # 排第1
    'top3': 0,      # 排前3
    'top5': 0,      # 排前5
    'top10': 0,     # 排前10
    'not_top10': 0, # 不在前10
    'not_found': 0  # 未找到
}

failed_cases = []
sample_success = []
sample_failed = []

for i, test_case in enumerate(test_cases, 1):  # 测试全部
    hospital = test_case['hospital']
    city = test_case['city']
    keyword = test_case['keyword']
    full_name = test_case['full_name']
    
    # 构造搜索参数
    params = {
        "keyword": keyword,
        "region": city,
        "page": 0,
        "size": 20
    }
    
    try:
        response = requests.post(api_url, json=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()['data']
            content = data.get('content', [])
            
            # 查找该医院的排名
            position = -1
            for idx, item in enumerate(content):
                if item['name'] == full_name:
                    position = idx + 1
                    break
            
            if position == 1:
                results['top1'] += 1
                status = "[Top1]"
            elif position <= 3:
                results['top3'] += 1
                status = f"[Top3-#{position}]"
            elif position <= 5:
                results['top5'] += 1
                status = f"[Top5-#{position}]"
            elif position <= 10:
                results['top10'] += 1
                status = f"[Top10-#{position}]"
            elif position > 10:
                results['not_top10'] += 1
                status = f"[#{position}]"
                failed_cases.append({
                    'name': full_name[:40],
                    'city': city,
                    'keyword': keyword,
                    'position': position
                })
            else:
                results['not_found'] += 1
                status = "[未找到]"
                failed_cases.append({
                    'name': full_name[:40],
                    'city': city,
                    'keyword': keyword,
                    'position': '未找到'
                })
            
            # 收集样本
            if position <= 3 and len(sample_success) < 3:
                sample_success.append({
                    'name': full_name[:40],
                    'city': city,
                    'keyword': keyword,
                    'position': position
                })
            elif position > 10 and len(sample_failed) < 3:
                sample_failed.append({
                    'name': full_name[:40],
                    'city': city,
                    'keyword': keyword,
                    'position': position
                })
            
            # 显示进度
            if i % 10 == 0:
                print(f"  进度: {i}/{len(test_cases)} | {status} {full_name[:40]} | {city} + {keyword}")
        else:
            print(f"  [ERROR] {full_name[:40]} | HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  [ERROR] {full_name[:40]} | {e}")

# 5. 汇总结果
print("\n" + "=" * 100)
print("测试结果汇总")
print("=" * 100)

total = len(test_cases)
print(f"\n测试总数: {total} 家三级医院")
print(f"\n排名分布:")
print(f"  排第1名:          {results['top1']:3} 家 ({results['top1']/total*100:.1f}%)")
print(f"  排前3名(含):      {results['top1'] + results['top3']:3} 家 ({(results['top1'] + results['top3'])/total*100:.1f}%)")
print(f"  排前5名(含):      {results['top1'] + results['top3'] + results['top5']:3} 家 ({(results['top1'] + results['top3'] + results['top5'])/total*100:.1f}%)")
print(f"  排前10名(含):     {results['top1'] + results['top3'] + results['top5'] + results['top10']:3} 家 ({(results['top1'] + results['top3'] + results['top5'] + results['top10'])/total*100:.1f}%)")
print(f"  排10名之后:       {results['not_top10']:3} 家 ({results['not_top10']/total*100:.1f}%)")
print(f"  未找到:           {results['not_found']:3} 家 ({results['not_found']/total*100:.1f}%)")

# 成功样本
if sample_success:
    print(f"\n[成功样本] 排前3的医院:")
    for s in sample_success:
        print(f"  #{s['position']} {s['name']:<42} | {s['city']} + {s['keyword']}")

# 失败样本
if sample_failed:
    print(f"\n[失败样本] 排名靠后的医院:")
    for s in sample_failed:
        print(f"  #{s['position']} {s['name']:<42} | {s['city']} + {s['keyword']}")

# 详细失败列表
if failed_cases:
    print(f"\n[失败详情] 共 {len(failed_cases)} 家医院未排在前10:")
    print("-" * 100)
    print(f"{'医院名称':<45} {'城市':<12} {'关键词':<8} {'排名':<8}")
    print("-" * 100)
    for fc in failed_cases[:20]:
        print(f"{fc['name']:<45} {fc['city']:<12} {fc['keyword']:<8} {fc['position']}")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
