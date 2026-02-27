# -*- coding: utf-8 -*-
"""
补充缺失的region字段
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

print("=" * 80)
print("补充缺失的region字段")
print("=" * 80)

# 1. 读取Excel
print("\n[1] 读取Excel...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]      # 机构名称
col_region = df.columns[2]    # 县（区、市）
col_uscc = df.columns[6]      # 统一社会信用代码

print(f"Excel总行数: {len(df)}")

# 2. 连接数据库
print("\n[2] 连接数据库...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)
print("连接成功")

# 3. 找出所有region为空的记录
print("\n[3] 查询region为空的记录...")
cursor.execute("""
    SELECT id, uscc, name, region 
    FROM const_init_institutions 
    WHERE region IS NULL OR region = ''
""")
empty_region_records = cursor.fetchall()

print(f"数据库中region为空的记录: {len(empty_region_records)}")

# 4. 构建Excel的USCC->Region映射
print("\n[4] 构建Excel数据映射...")
excel_mapping = {}
for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    
    if uscc and region:
        excel_mapping[uscc] = region

print(f"Excel中有region信息的记录: {len(excel_mapping)}")

# 5. 更新缺失的region
print("\n[5] 开始更新region...")

update_count = 0
match_count = 0

for record in empty_region_records:
    uscc = record['uscc']
    
    if uscc in excel_mapping:
        excel_region = excel_mapping[uscc]
        match_count += 1
        
        # 更新region
        sql = "UPDATE const_init_institutions SET region = %s WHERE id = %s"
        cursor.execute(sql, (excel_region, record['id']))
        update_count += 1
        
        if update_count <= 20:
            print(f"  [更新] {record['name'][:40]}")
            print(f"         region: {excel_region}")

conn.commit()

print(f"\n[6] 更新完成!")
print(f"  数据库region为空: {len(empty_region_records)}")
print(f"  Excel中找到匹配: {match_count}")
print(f"  实际更新: {update_count}")

# 7. 验证
print("\n[7] 验证更新结果...")
cursor.execute("""
    SELECT COUNT(*) as count
    FROM const_init_institutions 
    WHERE region IS NULL OR region = ''
""")
result = cursor.fetchone()
print(f"更新后，region仍为空的记录: {result['count']}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
