# -*- coding: utf-8 -*-
"""
生成region不一致对比报告
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
print("生成Region不一致对比报告")
print("=" * 80)

# 1. 读取Excel
print("\n[1] 读取Excel...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = df.columns[0]      # 机构名称
col_region = df.columns[2]    # 县（区、市）
col_uscc = df.columns[6]      # 统一社会信用代码

# 2. 连接数据库
print("[2] 连接数据库...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 3. 查询所有数据库记录
print("[3] 查询数据库...")
cursor.execute("SELECT id, uscc, name, region FROM const_init_institutions")
db_records = cursor.fetchall()

db_by_uscc = {r['uscc']: r for r in db_records}
print(f"数据库记录: {len(db_by_uscc)}")

# 4. 对比差异
print("[4] 对比差异...")

diff_list = []

for idx, row in df.iterrows():
    uscc = str(row[col_uscc]).strip() if pd.notna(row[col_uscc]) else ''
    excel_name = str(row[col_name]).strip() if pd.notna(row[col_name]) else ''
    excel_region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    
    if not uscc or not excel_region:
        continue
    
    if uscc in db_by_uscc:
        db_record = db_by_uscc[uscc]
        db_region = db_record['region']
        
        # 只关注都有值但不一致的情况
        if db_region and excel_region and db_region != excel_region:
            diff_list.append({
                'uscc': uscc,
                'name': excel_name,
                'excel_region': excel_region,
                'db_region': db_region
            })

print(f"发现不一致的记录: {len(diff_list)}")

# 5. 生成详细报告
print("\n[5] 生成报告...")

report_file = os.path.join(project_root, "Region不一致对比报告.txt")

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("Region 不一致对比报告（数据库和Excel都有值但不同）\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 100 + "\n\n")
    f.write(f"总计: {len(diff_list)} 条不一致\n\n")
    f.write("说明: 以下记录在数据库和Excel中都有region值，但值不相同\n")
    f.write("暂不处理，仅供参考\n")
    f.write("\n" + "=" * 100 + "\n\n")
    
    for i, diff in enumerate(diff_list, 1):
        f.write(f"{i}. {diff['name']}\n")
        f.write(f"   USCC: {diff['uscc']}\n")
        f.write(f"   Excel值: {diff['excel_region']}\n")
        f.write(f"   数据库值: {diff['db_region']}\n")
        f.write("\n")

print(f"报告已保存: {report_file}")

# 6. 统计分析
print("\n[6] 统计分析...")

# 按数据库region分组
from collections import Counter
db_region_counter = Counter([d['db_region'] for d in diff_list])
excel_region_counter = Counter([d['excel_region'] for d in diff_list])

print(f"\n数据库region分布（Top 10）:")
for region, count in db_region_counter.most_common(10):
    print(f"  {region:<15}: {count:>3} 条")

print(f"\nExcel region分布（Top 10）:")
for region, count in excel_region_counter.most_common(10):
    print(f"  {region:<15}: {count:>3} 条")

# 7. 显示前10条示例
print(f"\n[7] 前10条示例:")
print("-" * 100)
print(f"{'序号':<5} {'机构名称':<40} {'Excel':<15} {'数据库':<15}")
print("-" * 100)

for i, diff in enumerate(diff_list[:10], 1):
    name = diff['name'][:38] + '..' if len(diff['name']) > 40 else diff['name']
    print(f"{i:<5} {name:<40} {diff['excel_region']:<15} {diff['db_region']:<15}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print(f"完成! 详细报告: Region不一致对比报告.txt")
print("=" * 80)
