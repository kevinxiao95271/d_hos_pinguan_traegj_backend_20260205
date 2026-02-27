# -*- coding: utf-8 -*-
"""
清晰的最终分析：到底差了多少，为什么
"""
import pandas as pd
import pymysql
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("清晰的最终分析")
print("=" * 100)

# 读取Excel
print("\n[步骤1] 读取Excel...")
df_excel = pd.read_excel(os.path.join(project_root, excel_file))

col_name = 0
col_region = 1
col_level = 4
col_uscc = 6

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

excel_total = len(df_excel)
excel_unique = df_excel['组合键'].nunique()

print(f"   Excel总记录数: {excel_total}")
print(f"   Excel不同组合数: {excel_unique}")
print(f"   Excel中重复的记录: {excel_total - excel_unique} 条")

# 读取DB
print("\n[步骤2] 读取数据库...")
conn = pymysql.connect(**DB_CONFIG)
try:
    df_db = pd.read_sql("SELECT name, uscc FROM const_init_institutions WHERE name IS NOT NULL AND uscc IS NOT NULL AND uscc != ''", conn)
    df_db['组合键'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip()
    
    db_total = len(df_db)
    db_unique = df_db['组合键'].nunique()
    
    print(f"   DB总记录数: {db_total}")
    print(f"   DB不同组合数: {db_unique}")
    
finally:
    conn.close()

# 对比
print("\n[步骤3] 对比分析...")

excel_keys = set(df_excel['组合键'].unique())
db_keys = set(df_db['组合键'].unique())

excel_only = excel_keys - db_keys
db_only = db_keys - excel_keys
common = excel_keys & db_keys

print(f"\n   Excel独有组合: {len(excel_only)}")
print(f"   DB独有组合: {len(db_only)}")
print(f"   共同组合: {len(common)}")

# 计算差距
gap = excel_unique - db_unique
print(f"\n   差距: Excel组合 - DB组合 = {excel_unique} - {db_unique} = {gap}")

# Excel独有的记录详细分析
print("\n" + "=" * 100)
print(f"Excel独有的{len(excel_only)}个组合详细分析")
print("=" * 100)

df_excel_only = df_excel[df_excel['组合键'].isin(excel_only)].copy()
print(f"\n涉及的Excel记录数: {len(df_excel_only)}")

# 按USCC是否为空分类
uscc_empty_mask = df_excel_only.iloc[:, col_uscc].isna() | \
                  (df_excel_only.iloc[:, col_uscc].astype(str).str.strip() == '') | \
                  (df_excel_only.iloc[:, col_uscc].astype(str).str.strip() == 'nan')

df_uscc_empty = df_excel_only[uscc_empty_mask]
df_uscc_valid = df_excel_only[~uscc_empty_mask]

print(f"\n分类:")
print(f"   1. USCC为空: {len(df_uscc_empty)} 条")
print(f"   2. USCC不为空: {len(df_uscc_valid)} 条")
print(f"   合计: {len(df_uscc_empty)} + {len(df_uscc_valid)} = {len(df_excel_only)}")

# 显示USCC不为空但未导入的记录
print(f"\n" + "=" * 100)
print(f"USCC不为空但未在DB中的{len(df_uscc_valid)}条记录")
print("=" * 100)

print(f"\n{'序号':<5} {'机构名称':<45} {'USCC':<22} {'等级':<12} {'地区':<12}")
print("-" * 100)

for idx, (i, row) in enumerate(df_uscc_valid.iterrows(), 1):
    name = row['名字'][:43] if len(row['名字']) > 43 else row['名字']
    uscc = row['USCC'][:20]
    level = row.iloc[col_level]
    level_display = level if pd.notna(level) and str(level).strip() != '' else '[空值]'
    region = str(row.iloc[col_region])[:10] if pd.notna(row.iloc[col_region]) else '[空]'
    
    print(f"{idx:<5} {name:<45} {uscc:<22} {level_display:<12} {region:<12}")

# 等级统计
print(f"\n等级分布:")
level_counts = df_uscc_valid.iloc[:, col_level].apply(
    lambda x: x if pd.notna(x) and str(x).strip() != '' else '[空值]'
).value_counts()
for level, count in level_counts.items():
    print(f"   {level}: {count} 条")

# DB独有的记录
print(f"\n" + "=" * 100)
print(f"DB独有的{len(db_only)}个组合（Excel中没有）")
print("=" * 100)

df_db_only = df_db[df_db['组合键'].isin(db_only)]
print(f"\n这些可能是:")
print(f"   - 历史数据（不在当前Excel中）")
print(f"   - 手动添加的数据")
print(f"   - 测试数据")

print(f"\n前20条示例:")
for idx, (i, row) in enumerate(df_db_only.head(20).iterrows(), 1):
    print(f"   {idx}. {row['name']}")

# 最终答案
print(f"\n" + "=" * 100)
print("最终答案")
print("=" * 100)

print(f"\n[数据对比]")
print(f"   Excel总记录: {excel_total}")
print(f"   Excel不同组合: {excel_unique}")
print(f"   DB总记录: {db_total}")
print(f"   DB不同组合: {db_unique}")

print(f"\n[差距分析]")
print(f"   Excel比DB少: {gap} 个组合")
if gap < 0:
    print(f"   （即：DB比Excel多 {abs(gap)} 个组合）")

print(f"\n[Excel中有但DB中没有的]")
print(f"   总计: {len(excel_only)} 个不同组合")
print(f"   涉及Excel记录: {len(df_excel_only)} 条")
print(f"   其中:")
print(f"      - USCC为空: {len(df_uscc_empty)} 条（无法导入）")
print(f"      - USCC不为空: {len(df_uscc_valid)} 条（应该能导入但未导入）")

print(f"\n[DB中有但Excel中没有的]")
print(f"   总计: {len(db_only)} 个组合（可能是历史数据）")

print(f"\n检查完成！")
