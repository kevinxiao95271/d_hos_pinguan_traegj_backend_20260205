# -*- coding: utf-8 -*-
"""
分析三级医院的region和city数据完整性
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
print("三级医院 region/city 数据完整性分析")
print("=" * 100)

# 1. 读取Excel
print("\n[1] 读取Excel文件...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]      # 机构名称
col_city = df.columns[1]      # 市
col_region = df.columns[2]    # 县（区、市）
col_level = df.columns[4]     # 机构级别
col_uscc = df.columns[6]      # 统一社会信用代码

print(f"Excel总行数: {len(df)}")
print(f"列映射:")
print(f"  {col_name} -> name")
print(f"  {col_city} -> city")
print(f"  {col_region} -> region")
print(f"  {col_level} -> level")

# 2. 连接数据库
print("\n[2] 连接数据库...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 3. 获取数据库中的所有三级医院
print("\n[3] 查询数据库中的三级医院...")
cursor.execute("""
    SELECT id, uscc, name, region, city, level
    FROM const_init_institutions
    WHERE level = '三级'
    ORDER BY name
""")

db_level3 = cursor.fetchall()
print(f"数据库中三级医院: {len(db_level3)} 家")

# 4. 分析Excel中的三级医院数据
print("\n[4] 分析Excel中三级医院的region/city数据...")

# 构建Excel数据映射 (uscc -> data)
excel_map = {}
for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    name = str(row[col_name]).strip() if pd.notna(row[col_name]) else ''
    city = str(row[col_city]).strip() if pd.notna(row[col_city]) else None
    region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    level = str(row[col_level]).strip() if pd.notna(row[col_level]) else None
    
    if uscc:
        excel_map[uscc] = {
            'name': name,
            'city': city,
            'region': region,
            'level': level
        }

print(f"Excel中有USCC的记录: {len(excel_map)} 条")

# 5. 对比分析
print("\n[5] 对比数据库和Excel...")

need_update = []
excel_also_null = []
not_in_excel = []

for db_hospital in db_level3:
    uscc = db_hospital['uscc']
    db_name = db_hospital['name']
    db_region = db_hospital['region']
    db_city = db_hospital['city']
    
    if uscc in excel_map:
        excel_data = excel_map[uscc]
        excel_region = excel_data['region']
        excel_city = excel_data['city']
        
        # 检查是否需要更新
        region_need_update = (db_region is None or db_region == '') and excel_region
        city_need_update = (db_city is None or db_city == '') and excel_city
        
        if region_need_update or city_need_update:
            need_update.append({
                'id': db_hospital['id'],
                'uscc': uscc,
                'name': db_name,
                'db_region': db_region,
                'excel_region': excel_region,
                'db_city': db_city,
                'excel_city': excel_city,
                'update_region': region_need_update,
                'update_city': city_need_update
            })
        
        # 检查Excel中也是NULL的情况
        if not excel_region and not db_region:
            excel_also_null.append({
                'name': db_name,
                'uscc': uscc
            })
    else:
        not_in_excel.append({
            'name': db_name,
            'uscc': uscc,
            'db_region': db_region,
            'db_city': db_city
        })

# 6. 输出统计
print("\n" + "=" * 100)
print("统计结果")
print("=" * 100)

print(f"\n数据库中三级医院总数: {len(db_level3)} 家")
print(f"  需要补充数据: {len(need_update)} 家")
print(f"  Excel中也没region: {len(excel_also_null)} 家")
print(f"  不在Excel中: {len(not_in_excel)} 家")

# 7. 详细输出需要更新的
if need_update:
    print(f"\n[需要补充] {len(need_update)} 家三级医院缺失region/city:")
    print("-" * 100)
    print(f"{'医院名称':<45} {'补充region':<15} {'补充city':<15}")
    print("-" * 100)
    
    for item in need_update[:30]:  # 显示前30个
        name = item['name'][:43]
        region_info = f"{item['excel_region']}" if item['update_region'] else "不需要"
        city_info = f"{item['excel_city']}" if item['update_city'] else "不需要"
        print(f"{name:<45} {region_info:<15} {city_info:<15}")
    
    if len(need_update) > 30:
        print(f"... 还有 {len(need_update) - 30} 家医院需要更新")

# 8. Excel中也没有region的
if excel_also_null:
    print(f"\n[Excel也没数据] {len(excel_also_null)} 家三级医院Excel中region也是空:")
    print("-" * 100)
    for item in excel_also_null[:20]:
        print(f"  {item['name'][:70]}")
    if len(excel_also_null) > 20:
        print(f"  ... 还有 {len(excel_also_null) - 20} 家")

# 9. 不在Excel中的
if not_in_excel:
    print(f"\n[不在Excel中] {len(not_in_excel)} 家三级医院不在Excel中:")
    print("-" * 100)
    for item in not_in_excel[:10]:
        print(f"  {item['name'][:60]} (USCC: {item['uscc']})")
    if len(not_in_excel) > 10:
        print(f"  ... 还有 {len(not_in_excel) - 10} 家")

# 10. 保存需要更新的列表
if need_update:
    report_file = os.path.join(project_root, "三级医院需要补充的数据.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"三级医院需要补充region/city数据列表\n")
        f.write(f"共 {len(need_update)} 家医院\n")
        f.write("=" * 100 + "\n\n")
        
        for i, item in enumerate(need_update, 1):
            f.write(f"{i}. {item['name']}\n")
            f.write(f"   USCC: {item['uscc']}\n")
            if item['update_region']:
                f.write(f"   补充region: {item['excel_region']}\n")
            if item['update_city']:
                f.write(f"   补充city: {item['excel_city']}\n")
            f.write("\n")
    
    print(f"\n详细清单已保存: {report_file}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("分析完成")
print("=" * 100)
