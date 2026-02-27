# -*- coding: utf-8 -*-
"""
检查可疑的三级医院数据
"""
import pymysql
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

print("=" * 100)
print("检查可疑的三级医院")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 1. 查询所有三级医院
cursor.execute("""
    SELECT id, name, region, city, level
    FROM const_init_institutions
    WHERE level = '三级'
    ORDER BY name
""")

level3_hospitals = cursor.fetchall()

print(f"\n数据库中三级医院总数: {len(level3_hospitals)} 家\n")

# 2. 识别可疑的医务室/卫生站/诊所
suspicious_keywords = ['医务室', '卫生站', '卫生室', '诊所', '卫生所', '门诊部']

suspicious_list = []

for hospital in level3_hospitals:
    name = hospital['name']
    
    for keyword in suspicious_keywords:
        if keyword in name:
            suspicious_list.append(hospital)
            break

print(f"[可疑三级医院] 包含医务室/卫生站等关键词的: {len(suspicious_list)} 家")
print("-" * 100)

if suspicious_list:
    print(f"{'医院名称':<70} {'region':<12} {'city':<12}")
    print("-" * 100)
    
    for item in suspicious_list:
        name = item['name'][:68]
        region = item['region'] or '[NULL]'
        city = item['city'] or '[NULL]'
        print(f"{name:<70} {region:<12} {city:<12}")

# 3. 统计关键词分布
print(f"\n" + "=" * 100)
print("关键词分布统计")
print("=" * 100)

keyword_stats = {}
for keyword in suspicious_keywords:
    count = len([h for h in suspicious_list if keyword in h['name']])
    if count > 0:
        keyword_stats[keyword] = count

for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {keyword:<10}: {count:>3} 家")

# 4. 检查那个具体的医院
print(f"\n" + "=" * 100)
print("检查：丽水市人民医院老干部活动中心医务室")
print("=" * 100)

cursor.execute("""
    SELECT *
    FROM const_init_institutions
    WHERE name LIKE '%丽水市人民医院老干部活动中心医务室%'
""")

specific = cursor.fetchall()
if specific:
    for s in specific:
        print(f"\nID: {s['id']}")
        print(f"名称: {s['name']}")
        print(f"USCC: {s['uscc']}")
        print(f"Region: {s['region']}")
        print(f"City: {s['city']}")
        print(f"Level: {s['level']}")
else:
    print("未找到该医院")

cursor.close()
conn.close()

print("\n" + "=" * 100)
