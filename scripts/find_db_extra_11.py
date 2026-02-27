# -*- coding: utf-8 -*-
"""
找出DB比Excel多的11个组合
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
print("查找DB比Excel多的11个组合")
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

# 使用不区分大小写的USCC创建组合键
df_excel['组合键_忽略大小写'] = df_excel['名字'] + '|||' + df_excel['USCC'].str.upper()

excel_keys_ignore_case = set(df_excel['组合键_忽略大小写'].unique())
print(f"   Excel不同组合数（忽略USCC大小写）: {len(excel_keys_ignore_case)}")

# 2. 读取DB
print("\n[2/3] 读取数据库数据...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = """
        SELECT id, name, uscc, level, region, code
        FROM const_init_institutions 
        WHERE name IS NOT NULL 
          AND uscc IS NOT NULL
          AND uscc != ''
    """
    df_db = pd.read_sql(query, conn)
    
    # 使用不区分大小写的USCC创建组合键
    df_db['组合键_忽略大小写'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip().str.upper()
    
    db_keys_ignore_case = set(df_db['组合键_忽略大小写'].unique())
    print(f"   DB不同组合数（忽略USCC大小写）: {len(db_keys_ignore_case)}")
    
finally:
    conn.close()

# 3. 找出DB独有的组合
print("\n[3/3] 对比分析...")

db_only_keys = db_keys_ignore_case - excel_keys_ignore_case
print(f"\n   DB独有的组合数: {len(db_only_keys)}")

if len(db_only_keys) > 0:
    # 找出这些组合对应的DB记录
    df_db_only = df_db[df_db['组合键_忽略大小写'].isin(db_only_keys)].copy()
    
    print(f"\n" + "=" * 100)
    print(f"DB独有的{len(db_only_keys)}个组合详细清单")
    print("=" * 100)
    
    print(f"\n{'序号':<5} {'机构名称':<45} {'USCC':<22} {'等级':<12} {'地区':<12} {'DB ID':<10}")
    print("-" * 110)
    
    for idx, (i, row) in enumerate(df_db_only.iterrows(), 1):
        name = row['name'][:43] if len(row['name']) > 43 else row['name']
        uscc = row['uscc'][:20]
        level = row['level'] if pd.notna(row['level']) and row['level'] != '' else '[空值]'
        region = str(row['region'])[:10] if pd.notna(row['region']) else '[空]'
        db_id = row['id']
        
        print(f"{idx:<5} {name:<45} {uscc:<22} {level:<12} {region:<12} {db_id:<10}")
    
    # 等级统计
    print(f"\n等级分布:")
    level_counts = df_db_only['level'].apply(
        lambda x: x if pd.notna(x) and str(x).strip() != '' else '[空值]'
    ).value_counts()
    for level, count in level_counts.items():
        print(f"   {level}: {count} 条")
    
    # 分析这些记录的特征
    print(f"\n特征分析:")
    
    # 检查是否有特定的名字模式
    names = df_db_only['name'].tolist()
    
    # 导出
    output_file = os.path.join(project_root, 'DB独有的11个组合.xlsx')
    df_export = df_db_only[['id', 'name', 'uscc', 'level', 'region', 'code']].copy()
    df_export.columns = ['DB记录ID', '机构名称', '统一社会信用代码', '等级', '地区', '机构编码']
    df_export.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n   已导出到: {output_file}")
    
    output_csv = os.path.join(project_root, 'DB独有的11个组合.csv')
    df_export.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"   已导出到: {output_csv}")

# 最终验证数字
print(f"\n" + "=" * 100)
print("最终数字验证")
print("=" * 100)

print(f"\n[基础数据]")
print(f"   Excel总记录: {len(df_excel)}")
print(f"   Excel不同组合（忽略USCC大小写）: {len(excel_keys_ignore_case)}")
print(f"   DB总记录: {len(df_db)}")
print(f"   DB不同组合（忽略USCC大小写）: {len(db_keys_ignore_case)}")

print(f"\n[差距]")
print(f"   DB组合 - Excel组合 = {len(db_keys_ignore_case)} - {len(excel_keys_ignore_case)} = {len(db_keys_ignore_case) - len(excel_keys_ignore_case)}")

print(f"\n[组成]")
print(f"   Excel独有: {len(excel_keys_ignore_case - db_keys_ignore_case)}")
print(f"   DB独有: {len(db_only_keys)}")
print(f"   共同: {len(excel_keys_ignore_case & db_keys_ignore_case)}")

print(f"\n检查完成！")
