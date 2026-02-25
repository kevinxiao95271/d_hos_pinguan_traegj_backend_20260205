# -*- coding: utf-8 -*-
"""
检查所有表，寻找可能的字典数据源
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
print("数据库所有表列表")
print("=" * 100)

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print(f"\n共 {len(tables)} 个表:\n")
for i, table in enumerate(tables, 1):
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{i:2}. {table_name:<40} ({count:>6} 条记录)")

print("\n" + "=" * 100)
print("检查activity_info表结构")
print("=" * 100)

cursor.execute("DESC activity_info")
columns = cursor.fetchall()

print("\nactivity_info表字段:")
for col in columns:
    print(f"  {col[0]:<30} {col[1]:<20}")

# 检查是否有数据
cursor.execute("SELECT COUNT(*) FROM activity_info")
count = cursor.fetchone()[0]
print(f"\nactivity_info表记录数: {count}")

if count > 0:
    print("\n样例数据:")
    cursor.execute("SELECT * FROM activity_info LIMIT 2")
    rows = cursor.fetchall()
    
    cursor.execute("DESC activity_info")
    col_info = cursor.fetchall()
    col_names = [col[0] for col in col_info]
    
    for row in rows:
        print("\n记录:")
        for i, col_name in enumerate(col_names):
            if row[i] is not None:
                print(f"  {col_name}: {row[i]}")

cursor.close()
conn.close()
