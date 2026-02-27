# -*- coding: utf-8 -*-
"""
精确计算Excel与DB的差距
"""
import pandas as pd
import pymysql
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("精确差距分析")
print("=" * 100)

# 1. 读取Excel
print("\n[1/3] 读取Excel数据...")
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_level = 4
col_uscc = 6

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

print(f"   Excel总记录数: {len(df_excel)}")

# 统计Excel中不同的组合
excel_unique_keys = df_excel['组合键'].unique()
print(f"   Excel不同的(名字+USCC)组合数: {len(excel_unique_keys)}")

# Excel中重复的组合
key_counts = df_excel['组合键'].value_counts()
excel_duplicates = key_counts[key_counts > 1]
print(f"   Excel中重复的组合数: {len(excel_duplicates)}")
print(f"   Excel中重复涉及的记录数: {excel_duplicates.sum()}")

# 2. 读取DB
print("\n[2/3] 读取数据库数据...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = "SELECT name, uscc, level FROM const_init_institutions WHERE name IS NOT NULL AND uscc IS NOT NULL AND uscc != ''"
    df_db = pd.read_sql(query, conn)
    df_db['组合键'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip()
    
    print(f"   DB总记录数: {len(df_db)}")
    
    db_unique_keys = df_db['组合键'].unique()
    print(f"   DB不同的(名字+USCC)组合数: {len(db_unique_keys)}")
    
    # DB中是否有重复
    db_key_counts = df_db['组合键'].value_counts()
    db_duplicates = db_key_counts[db_key_counts > 1]
    print(f"   DB中重复的组合数: {len(db_duplicates)}")
    if len(db_duplicates) > 0:
        print(f"   DB中重复涉及的记录数: {db_duplicates.sum()}")
    
finally:
    conn.close()

# 3. 计算差距
print("\n[3/3] 计算差距...")

excel_keys_set = set(excel_unique_keys)
db_keys_set = set(db_unique_keys)

# Excel有但DB没有的
missing_keys = excel_keys_set - db_keys_set
# DB有但Excel没有的
extra_keys = db_keys_set - excel_keys_set

print(f"\n   Excel独有的组合: {len(missing_keys)}")
print(f"   DB独有的组合: {len(extra_keys)}")
print(f"   共同拥有的组合: {len(excel_keys_set & db_keys_set)}")

print(f"\n" + "=" * 100)
print("差距详细分析")
print("=" * 100)

print(f"\n[Excel -> DB 的差距]")
print(f"   Excel不同组合: {len(excel_keys_set)}")
print(f"   DB不同组合: {len(db_keys_set)}")
print(f"   差距: {len(excel_keys_set)} - {len(db_keys_set)} = {len(excel_keys_set) - len(db_keys_set)}")

# 找出Excel中有但DB中没有的记录
df_missing = df_excel[df_excel['组合键'].isin(missing_keys)].copy()

print(f"\n[Excel中有但DB中没有的记录]")
print(f"   涉及的Excel记录数: {len(df_missing)}")
print(f"   不同的组合数: {len(missing_keys)}")

# 分类统计
# 1. USCC为空的
uscc_empty = df_missing[
    df_missing.iloc[:, col_uscc].isna() | 
    (df_missing.iloc[:, col_uscc].astype(str).str.strip() == '') | 
    (df_missing.iloc[:, col_uscc].astype(str).str.strip() == 'nan')
]

# 2. USCC不为空的
uscc_not_empty = df_missing[
    ~(df_missing.iloc[:, col_uscc].isna() | 
      (df_missing.iloc[:, col_uscc].astype(str).str.strip() == '') | 
      (df_missing.iloc[:, col_uscc].astype(str).str.strip() == 'nan'))
]

print(f"\n   分类:")
print(f"      USCC为空: {len(uscc_empty)} 条")
print(f"      USCC不为空: {len(uscc_not_empty)} 条")

if len(uscc_not_empty) > 0:
    print(f"\n   USCC不为空但未导入的记录详情:")
    print(f"   {'序号':<5} {'机构名称':<45} {'USCC':<22} {'等级':<12}")
    print("   " + "-" * 95)
    
    for idx, (i, row) in enumerate(uscc_not_empty.iterrows(), 1):
        name = row['名字'][:43] if len(row['名字']) > 43 else row['名字']
        uscc = row['USCC'][:20]
        level_raw = row.iloc[col_level]
        level = level_raw if pd.notna(level_raw) and str(level_raw).strip() != '' else '[空值]'
        
        print(f"   {idx:<5} {name:<45} {uscc:<22} {level:<12}")

print(f"\n" + "=" * 100)
print("最终答案")
print("=" * 100)

print(f"\n[Excel总情况]")
print(f"   总记录数: {len(df_excel)}")
print(f"   不同的(名字+USCC)组合: {len(excel_keys_set)}")
print(f"   重复的记录数: {len(df_excel) - len(excel_keys_set)}")

print(f"\n[DB总情况]")
print(f"   总记录数: {len(df_db)}")
print(f"   不同的(名字+USCC)组合: {len(db_keys_set)}")

print(f"\n[差距明细]")
total_gap = len(excel_keys_set) - len(db_keys_set)
print(f"   Excel组合 - DB组合 = {len(excel_keys_set)} - {len(db_keys_set)} = {total_gap}")

print(f"\n   差距组成:")
print(f"      USCC为空: {len(uscc_empty)} 条")
print(f"      USCC不为空但未导入: {len(uscc_not_empty)} 条")
print(f"      合计: {len(uscc_empty)} + {len(uscc_not_empty)} = {len(missing_keys)}")

if total_gap == len(missing_keys):
    print(f"\n   [OK] 计算一致！差距{total_gap}条全部找到。")
else:
    print(f"\n   [WARN] 计算不一致！差距{total_gap}但只找到{len(missing_keys)}条。")

print(f"\n检查完成！")
