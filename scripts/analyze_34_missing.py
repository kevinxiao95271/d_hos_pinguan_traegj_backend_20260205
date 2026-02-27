# -*- coding: utf-8 -*-
"""
分析最终验证中显示的34条未导入记录
"""
import pandas as pd
import pymysql
import os

# 数据库配置
DB_CONFIG = {
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
print("分析未导入的34条记录")
print("=" * 100)

# 1. 读取Excel
print("\n[1/3] 读取Excel数据...")
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_level = 4
col_uscc = 6

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()

def process_level(level):
    if pd.isna(level):
        return '无等级'
    level_str = str(level).strip()
    if level_str == '' or level_str == 'nan':
        return '无等级'
    return level_str

df_excel['等级'] = df_excel.iloc[:, col_level].apply(process_level)
df_excel['地区'] = df_excel.iloc[:, col_region]
df_excel['匹配键'] = df_excel['名字'] + '|||' + df_excel['USCC']

print(f"   Excel总记录: {len(df_excel)}")

# 2. 读取DB
print("\n[2/3] 读取数据库数据...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = "SELECT name, uscc FROM const_init_institutions WHERE name IS NOT NULL AND uscc IS NOT NULL AND uscc != ''"
    df_db = pd.read_sql(query, conn)
    df_db['匹配键'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip()
    db_keys = set(df_db['匹配键'])
    print(f"   DB总记录: {len(df_db)}")
finally:
    conn.close()

# 3. 找出Excel中有但DB中没有的记录
print("\n[3/3] 查找未导入的记录...")

excel_keys = df_excel['匹配键'].unique()
missing_keys = [k for k in excel_keys if k not in db_keys]

print(f"   Excel中不同的(名字+USCC)组合: {len(excel_keys)}")
print(f"   DB中存在的组合: {len(db_keys)}")
print(f"   未导入的组合: {len(missing_keys)}")

# 找出所有未导入的记录
df_missing = df_excel[df_excel['匹配键'].isin(missing_keys)].copy()

print(f"   涉及的Excel记录数: {len(df_missing)}")

# 显示详细信息
print(f"\n" + "=" * 100)
print("未导入记录详细清单")
print("=" * 100)

print(f"\n{'序号':<5} {'机构名称':<45} {'USCC':<22} {'等级':<12} {'地区':<15}")
print("-" * 100)

for idx, row in df_missing.iterrows():
    name = row['名字'][:43] if len(row['名字']) > 43 else row['名字']
    uscc = str(row['USCC'])[:20]
    level = row['等级']
    region = str(row['地区'])[:13] if pd.notna(row['地区']) else '[空]'
    
    print(f"{idx+1:<5} {name:<45} {uscc:<22} {level:<12} {region:<15}")

# 等级统计
print(f"\n" + "=" * 100)
print("未导入记录等级统计")
print("=" * 100)

level_counts = df_missing['等级'].value_counts()
print(f"\n等级分布:")
for level, count in level_counts.items():
    print(f"   {level}: {count} 条")

# 检查这些记录是否在Excel中重复
print(f"\n" + "=" * 100)
print("重复性分析")
print("=" * 100)

missing_key_counts = df_missing['匹配键'].value_counts()
missing_duplicates = missing_key_counts[missing_key_counts > 1]

print(f"\n在未导入记录中:")
print(f"   不同的(名字+USCC)组合: {len(missing_key_counts)}")
print(f"   重复的组合: {len(missing_duplicates)}")
print(f"   涉及的记录数: {missing_duplicates.sum() if len(missing_duplicates) > 0 else 0}")

if len(missing_duplicates) > 0:
    print(f"\n重复的组合详情:")
    for combo, count in missing_duplicates.items():
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            matched = df_missing[df_missing['匹配键'] == combo]
            print(f"\n   {name}")
            print(f"   USCC: {uscc}")
            print(f"   重复{count}次:")
            for idx, row in matched.iterrows():
                print(f"      - 等级: {row['等级']}, 地区: {row['地区']}")

# 导出
output_file = os.path.join(project_root, 'Excel中未导入的34条记录详细.xlsx')
df_export = df_missing[['名字', '地区', '等级', 'USCC']].copy()
df_export.columns = ['机构名称', '地区', '等级', '统一社会信用代码']
df_export.to_excel(output_file, index=False, engine='openpyxl')

print(f"\n已导出详细清单到: {output_file}")

output_csv = os.path.join(project_root, 'Excel中未导入的34条记录详细.csv')
df_export.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"已导出详细清单到: {output_csv}")

print(f"\n检查完成！")
