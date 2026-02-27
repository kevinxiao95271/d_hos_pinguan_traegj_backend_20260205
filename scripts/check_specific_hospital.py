# -*- coding: utf-8 -*-
"""
检查平阳县人民医院的数据
"""
import os
import pandas as pd
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

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("检查平阳县人民医院数据")
print("=" * 100)

# 1. 读取Excel
print("\n[1] 读取Excel文件...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

print(f"Excel总行数: {len(df)}")
print(f"Excel列数: {len(df.columns)}")
print(f"\n列名列表:")
for i, col in enumerate(df.columns):
    print(f"  [{i}] {col}")

# 查找平阳县人民医院
print(f"\n[2] 在Excel中查找'平阳县人民医院'...")

mask = df[df.columns[0]].str.contains('平阳县人民医院', na=False)
results = df[mask]

print(f"找到 {len(results)} 条记录\n")

for idx, row in results.iterrows():
    print(f"记录 #{idx+1}:")
    for i, col in enumerate(df.columns):
        value = row[col]
        print(f"  [{i}] {col}: {value}")
    print()

# 2. 查询数据库
print("\n[3] 在数据库中查找'平阳县人民医院'...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

cursor.execute("""
    SELECT *
    FROM const_init_institutions
    WHERE name LIKE '%平阳县人民医院%'
""")

db_results = cursor.fetchall()

print(f"找到 {len(db_results)} 条记录\n")

for i, record in enumerate(db_results, 1):
    print(f"记录 #{i}:")
    print(f"  ID: {record['id']}")
    print(f"  名称: {record['name']}")
    print(f"  USCC: {record['uscc']}")
    print(f"  Region: {record['region']}")
    print(f"  City: {record['city']}")
    print(f"  Level: {record['level']}")
    print()

cursor.close()
conn.close()

print("=" * 100)
