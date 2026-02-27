# -*- coding: utf-8 -*-
"""
只同步等级字段（level）
按USCC匹配，更新level字段
"""
import os
import pandas as pd
import pymysql
from datetime import datetime
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
print("从Excel同步等级数据（只更新level字段）")
print("=" * 80)

# 1. 读取Excel
print("\n[1] 读取Excel...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]      # 机构名称
col_region = df.columns[2]    # 县（区、市）
col_level = df.columns[4]     # 机构级别
col_uscc = df.columns[6]      # 统一社会信用代码

print(f"总行数: {len(df)}")
print(f"等级列: {col_level}")
print(f"代码列: {col_uscc}")

# 统计Excel中的等级分布
print(f"\nExcel等级分布:")
level_counts = df[col_level].value_counts(dropna=False)
null_count = df[col_level].isna().sum()
print(f"  空值: {null_count}")
for level, count in level_counts.items():
    if pd.notna(level):
        print(f"  {level}: {count}")

# 2. 连接数据库
print("\n[2] 连接数据库...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)
print("连接成功")

# 3. 查询现有数据（按USCC索引）
print("\n[3] 查询现有数据...")
cursor.execute("SELECT id, uscc, name, region, level FROM const_init_institutions")
existing_records = cursor.fetchall()

existing_by_uscc = {r['uscc']: r for r in existing_records}
print(f"数据库现有记录: {len(existing_by_uscc)}")

# 4. 同步等级
print("\n[4] 开始同步等级...")

update_count = 0
matched_count = 0
not_found_count = 0
region_diff_list = []

for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    
    if not uscc:
        continue
    
    excel_name = str(row[col_name]).strip() if pd.notna(row[col_name]) else ''
    excel_region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    excel_level = str(row[col_level]).strip() if pd.notna(row[col_level]) else None
    
    if excel_level == '' or excel_level == 'nan':
        excel_level = None
    
    # 按USCC查找
    if uscc in existing_by_uscc:
        db_record = existing_by_uscc[uscc]
        matched_count += 1
        
        # 更新level（只在值不同时）
        if db_record['level'] != excel_level:
            sql = "UPDATE const_init_institutions SET level = %s WHERE uscc = %s"
            cursor.execute(sql, (excel_level, uscc))
            update_count += 1
        
        # 检查region差异
        if excel_region and db_record['region'] != excel_region:
            region_diff_list.append({
                'uscc': uscc,
                'name': excel_name,
                'excel_region': excel_region,
                'db_region': db_record['region']
            })
    else:
        not_found_count += 1
        if not_found_count <= 10:
            print(f"  [未找到] {excel_name[:40]} (USCC: {uscc})")
    
    # 每1000条提交一次
    if (idx + 1) % 1000 == 0:
        conn.commit()
        print(f"  进度: {idx+1}/{len(df)} (匹配:{matched_count}, 更新:{update_count}, 未找到:{not_found_count}, region差异:{len(region_diff_list)})")

conn.commit()

print(f"\n[5] 同步完成!")
print(f"  Excel记录数: {len(df)}")
print(f"  匹配记录: {matched_count}")
print(f"  更新level: {update_count}")
print(f"  未找到: {not_found_count}")
print(f"  region差异: {len(region_diff_list)}")

# 6. 生成region差异报告
if region_diff_list:
    print(f"\n[6] 生成region差异报告...")
    
    report_file = os.path.join(project_root, "region差异报告.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Region差异报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总差异数: {len(region_diff_list)}\n")
        f.write("=" * 100 + "\n\n")
        
        for i, diff in enumerate(region_diff_list, 1):
            f.write(f"{i}. {diff['name']}\n")
            f.write(f"   USCC: {diff['uscc']}\n")
            f.write(f"   Excel: {diff['excel_region'] or '[空]'}\n")
            f.write(f"   数据库: {diff['db_region'] or '[空]'}\n\n")
    
    print(f"差异报告已保存: {report_file}")
    print(f"\n前5条差异:")
    for diff in region_diff_list[:5]:
        print(f"  - {diff['name'][:40]}")
        print(f"    Excel: {diff['excel_region']}  |  DB: {diff['db_region']}")

# 7. 验证等级分布
print(f"\n[7] 验证数据库等级分布...")
cursor.execute("""
    SELECT 
        CASE 
            WHEN level IS NULL OR level = '' THEN '[空值]'
            ELSE level 
        END as level_display,
        COUNT(*) as count
    FROM const_init_institutions
    GROUP BY level_display
    ORDER BY count DESC
    LIMIT 10
""")

results = cursor.fetchall()
print(f"\n数据库等级分布（Top 10）:")
for row in results:
    print(f"  {row['level_display']:<20}: {row['count']:>6} 个")

cursor.close()
conn.close()

print("\n" + "=" * 80)
