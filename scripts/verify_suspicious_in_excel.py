# -*- coding: utf-8 -*-
"""
在Excel中验证可疑三级医院的真实等级
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
print("验证可疑三级医院的真实等级")
print("=" * 100)

# 1. 读取Excel
print("\n[1] 读取Excel...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]
col_level = df.columns[4]
col_uscc = df.columns[6]

# 构建映射
excel_map = {}
for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    name = str(row[col_name]).strip() if pd.notna(row[col_name]) else ''
    level = str(row[col_level]).strip() if pd.notna(row[col_level]) else None
    
    if uscc:
        excel_map[uscc] = {
            'name': name,
            'level': level
        }

print(f"Excel映射构建完成")

# 2. 查询数据库中的可疑三级医院
print("\n[2] 查询可疑三级医院...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

suspicious_keywords = ['医务室', '卫生站', '卫生室', '诊所', '卫生所', '门诊部']

cursor.execute("""
    SELECT id, uscc, name, level
    FROM const_init_institutions
    WHERE level = '三级'
""")

level3_hospitals = cursor.fetchall()

suspicious_list = []
for hospital in level3_hospitals:
    name = hospital['name']
    for keyword in suspicious_keywords:
        if keyword in name:
            suspicious_list.append(hospital)
            break

print(f"找到 {len(suspicious_list)} 家可疑的三级医院")

# 3. 对比Excel中的等级
print("\n[3] 对比Excel中的真实等级...")
print("-" * 100)
print(f"{'医院名称':<50} {'数据库等级':<10} {'Excel等级':<10} {'状态'}")
print("-" * 100)

wrong_count = 0
correct_count = 0
not_in_excel = 0

wrong_list = []

for hospital in suspicious_list:
    uscc = hospital['uscc']
    db_name = hospital['name'][:48]
    db_level = hospital['level']
    
    if uscc in excel_map:
        excel_level = excel_map[uscc]['level'] or '[NULL]'
        
        if excel_level == db_level:
            status = "[一致]"
            correct_count += 1
        else:
            status = "[不一致]"
            wrong_count += 1
            wrong_list.append({
                'id': hospital['id'],
                'uscc': uscc,
                'name': hospital['name'],
                'db_level': db_level,
                'excel_level': excel_level
            })
        
        print(f"{db_name:<50} {db_level:<10} {excel_level:<10} {status}")
    else:
        print(f"{db_name:<50} {db_level:<10} {'[不在Excel]':<10} [缺失]")
        not_in_excel += 1

# 4. 统计
print("\n" + "=" * 100)
print("验证结果")
print("=" * 100)

print(f"\n可疑三级医院总数: {len(suspicious_list)} 家")
print(f"  Excel等级也是三级: {correct_count} 家 (数据一致)")
print(f"  Excel等级不是三级: {wrong_count} 家 (数据错误!)")
print(f"  不在Excel中: {not_in_excel} 家")

if wrong_list:
    print(f"\n[数据错误] {len(wrong_list)} 家医院的等级需要修正:")
    print("-" * 100)
    for item in wrong_list:
        print(f"\n{item['name']}")
        print(f"  数据库: {item['db_level']}")
        print(f"  Excel: {item['excel_level']}")
        print(f"  应修正为: {item['excel_level']}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
