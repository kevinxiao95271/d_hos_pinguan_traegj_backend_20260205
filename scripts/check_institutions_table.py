# -*- coding: utf-8 -*-
"""
检查institutions表的数据情况
"""
import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

print("=" * 100)
print("检查institutions表")
print("=" * 100)

# 1. 查看表结构
print("\n[1] 表结构:")
cursor.execute("DESCRIBE institutions")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]:<20} {col[1]:<20} {col[2]}")

# 2. 统计总数
cursor.execute("SELECT COUNT(*) FROM institutions")
total = cursor.fetchone()[0]
print(f"\n[2] 机构总数: {total}")

# 3. 查看level分布
print(f"\n[3] Level分布:")
cursor.execute("""
    SELECT level, COUNT(*) as count 
    FROM institutions 
    GROUP BY level 
    ORDER BY count DESC
""")
levels = cursor.fetchall()
for level, count in levels:
    level_str = level if level else "NULL"
    print(f"  {level_str:<40} {count:>5} 家")

# 4. 查看所有机构
print(f"\n[4] 所有机构:")
cursor.execute("""
    SELECT id, name, level, region, city 
    FROM institutions 
    ORDER BY id
""")
samples = cursor.fetchall()
for id, name, level, region, city in samples:
    print(f"  [{id:>3}] {name[:50]:<50} | {level or 'NULL':<10} | {region or 'NULL':<15} | {city or 'NULL'}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
