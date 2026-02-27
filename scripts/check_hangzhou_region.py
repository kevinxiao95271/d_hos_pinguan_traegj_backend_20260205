# -*- coding: utf-8 -*-
"""
检查杭州相关的region数据
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

print("=" * 80)
print("检查杭州相关region数据")
print("=" * 80)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 1. 查看所有包含"杭州"的region
print("\n[1] 包含'杭州'的region值:")
cursor.execute("""
    SELECT DISTINCT region, COUNT(*) as count
    FROM const_init_institutions
    WHERE region LIKE '%杭州%'
    GROUP BY region
    ORDER BY count DESC
""")
results = cursor.fetchall()
for row in results:
    print(f"  {row['region']:<20}: {row['count']:>5} 个")

# 2. 查看所有包含"建德"的region
print("\n[2] 包含'建德'的region值:")
cursor.execute("""
    SELECT DISTINCT region, COUNT(*) as count
    FROM const_init_institutions
    WHERE region LIKE '%建德%'
    GROUP BY region
    ORDER BY count DESC
""")
results = cursor.fetchall()
for row in results:
    print(f"  {row['region']:<20}: {row['count']:>5} 个")

# 3. 查看city字段
print("\n[3] 检查city字段...")
cursor.execute("""
    SELECT DISTINCT city, COUNT(*) as count
    FROM const_init_institutions
    WHERE city IS NOT NULL AND city != ''
    GROUP BY city
    ORDER BY count DESC
    LIMIT 20
""")
results = cursor.fetchall()
if results:
    print("  city字段Top 20:")
    for row in results:
        print(f"    {row['city']:<20}: {row['count']:>5} 个")
else:
    print("  city字段都为空")

# 4. 查看建德的示例数据
print("\n[4] 建德医院示例（前5条）:")
cursor.execute("""
    SELECT name, region, city, level
    FROM const_init_institutions
    WHERE region LIKE '%建德%' OR name LIKE '%建德%'
    LIMIT 5
""")
results = cursor.fetchall()
for i, row in enumerate(results, 1):
    print(f"  {i}. {row['name'][:50]}")
    print(f"     region: {row['region']}")
    print(f"     city: {row['city']}")
    print(f"     level: {row['level']}")

# 5. 搜索包含"人民"的建德医院
print("\n[5] 建德+人民的医院:")
cursor.execute("""
    SELECT name, region, city
    FROM const_init_institutions
    WHERE (region LIKE '%建德%' OR name LIKE '%建德%') 
    AND name LIKE '%人民%'
    LIMIT 10
""")
results = cursor.fetchall()
for i, row in enumerate(results, 1):
    print(f"  {i}. {row['name']}")
    print(f"     region: {row['region']}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
