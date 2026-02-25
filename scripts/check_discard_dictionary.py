# -*- coding: utf-8 -*-
"""
检查dictionary_items_discard表的数据
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
print("检查dictionary_items_discard表")
print("=" * 100)

# 查看表结构
cursor.execute("DESC dictionary_items_discard")
columns = cursor.fetchall()

print("\n表结构:")
for col in columns:
    print(f"  {col[0]:<30} {col[1]:<20} {col[2]}")

# 按类型统计
cursor.execute("SELECT type, COUNT(*) FROM dictionary_items_discard GROUP BY type ORDER BY type")
types = cursor.fetchall()

print("\n按类型统计:")
print("-" * 100)
for t in types:
    print(f"  {t[0]:<30} {t[1]:>3} 条")

print(f"\n总计: {sum(t[1] for t in types)} 条")

# 查看每个类型的数据
print("\n" + "=" * 100)
print("详细数据")
print("=" * 100)

for type_name, count in types:
    print(f"\n[{type_name}] ({count}条)")
    print("-" * 100)
    
    cursor.execute("""
        SELECT code, label, active 
        FROM dictionary_items_discard 
        WHERE type = %s 
        ORDER BY id
    """, (type_name,))
    
    items = cursor.fetchall()
    for item in items:
        status = "启用" if item[2] else "禁用"
        print(f"  {item[0]:<30} {item[1]:<40} [{status}]")

cursor.close()
conn.close()
