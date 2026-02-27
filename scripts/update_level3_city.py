# -*- coding: utf-8 -*-
"""
补充三级医院的city数据
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
print("补充三级医院的city数据")
print("=" * 100)

# 1. 读取Excel
print("\n[1] 读取Excel文件...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]
col_city = df.columns[1]
col_region = df.columns[2]
col_uscc = df.columns[6]

# 构建映射
excel_map = {}
for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    city = str(row[col_city]).strip() if pd.notna(row[col_city]) else None
    region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    
    if uscc:
        excel_map[uscc] = {
            'city': city,
            'region': region
        }

print(f"Excel映射构建完成: {len(excel_map)} 条")

# 2. 连接数据库
print("\n[2] 连接数据库...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 3. 查询需要更新的三级医院
print("\n[3] 查询需要更新city的三级医院...")
cursor.execute("""
    SELECT id, uscc, name, region, city
    FROM const_init_institutions
    WHERE level = '三级' AND (city IS NULL OR city = '')
""")

hospitals_need_update = cursor.fetchall()
print(f"需要更新city的医院: {len(hospitals_need_update)} 家")

# 4. 执行更新
print("\n[4] 开始更新...")

update_count = 0
excel_also_null_count = 0
excel_also_null_list = []

for hospital in hospitals_need_update:
    uscc = hospital['uscc']
    name = hospital['name']
    
    if uscc in excel_map:
        excel_city = excel_map[uscc]['city']
        excel_region = excel_map[uscc]['region']
        
        if excel_city:
            # 补充city
            sql = "UPDATE const_init_institutions SET city = %s WHERE id = %s"
            cursor.execute(sql, (excel_city, hospital['id']))
            update_count += 1
            
            if update_count <= 10:
                print(f"  [更新] {name[:50]}")
                print(f"         city: {excel_city}")
        else:
            # Excel中也没有city
            excel_also_null_count += 1
            excel_also_null_list.append({
                'name': name,
                'has_region': bool(excel_region)
            })

conn.commit()

# 5. 结果统计
print("\n" + "=" * 100)
print("更新结果")
print("=" * 100)

print(f"\n需要更新的医院: {len(hospitals_need_update)} 家")
print(f"  成功更新city: {update_count} 家")
print(f"  Excel中city也为空: {excel_also_null_count} 家")

if excel_also_null_list:
    print(f"\n[Excel中city也为空的医院] {len(excel_also_null_list)} 家:")
    print("-" * 100)
    for item in excel_also_null_list:
        region_status = "有region" if item['has_region'] else "region也空"
        print(f"  {item['name']:<60} ({region_status})")

# 6. 验证更新结果
print(f"\n[6] 验证更新...")
cursor.execute("""
    SELECT COUNT(*) as count
    FROM const_init_institutions
    WHERE level = '三级' AND (city IS NULL OR city = '')
""")

result = cursor.fetchone()
print(f"更新后，city仍为空的三级医院: {result['count']} 家")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("更新完成")
print("=" * 100)
