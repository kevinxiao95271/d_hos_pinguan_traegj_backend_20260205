# -*- coding: utf-8 -*-
"""
分析导入失败的记录（排除Excel重复和USCC为空）
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
print("分析导入失败的记录")
print("=" * 100)

# 1. 读取Excel
print("\n[1/4] 读取Excel数据...")
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_type = 2
col_nature = 3
col_level = 4
col_business = 5
col_uscc = 6

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

print(f"   Excel总记录: {len(df_excel)}")

# 2. 找出Excel中重复的组合
print("\n[2/4] 识别Excel中的重复记录...")
key_counts = df_excel['组合键'].value_counts()
excel_duplicates = key_counts[key_counts > 1]

# 标记Excel中重复的记录
df_excel['Excel中重复'] = df_excel['组合键'].isin(excel_duplicates.index)

# 标记USCC为空的记录
df_excel['USCC为空'] = df_excel.iloc[:, col_uscc].isna() | \
                      (df_excel.iloc[:, col_uscc].astype(str).str.strip() == '') | \
                      (df_excel.iloc[:, col_uscc].astype(str).str.strip() == 'nan')

print(f"   Excel中重复记录: {df_excel['Excel中重复'].sum()} 条")
print(f"   USCC为空记录: {df_excel['USCC为空'].sum()} 条")

# 3. 读取DB数据
print("\n[3/4] 读取数据库数据...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = "SELECT name, uscc FROM const_init_institutions WHERE name IS NOT NULL AND uscc IS NOT NULL AND uscc != ''"
    df_db = pd.read_sql(query, conn)
    df_db['组合键'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip()
    db_keys = set(df_db['组合键'])
    print(f"   DB总记录: {len(df_db)}")
    print(f"   DB中不同的(名字+USCC)组合: {len(db_keys)}")
finally:
    conn.close()

# 4. 找出导入失败的记录（排除Excel重复和USCC为空）
print("\n[4/4] 分析导入失败的记录...")

# 未导入的记录 = Excel中有但DB中没有的
df_excel['已导入'] = df_excel['组合键'].isin(db_keys)
df_not_imported = df_excel[~df_excel['已导入']].copy()

print(f"\n   Excel中未导入的总记录: {len(df_not_imported)}")

# 排除Excel重复和USCC为空
df_import_failures = df_not_imported[
    ~df_not_imported['Excel中重复'] & 
    ~df_not_imported['USCC为空']
].copy()

print(f"   排除Excel重复: {df_not_imported['Excel中重复'].sum()} 条")
print(f"   排除USCC为空: {df_not_imported['USCC为空'].sum()} 条")
print(f"   剩余（其他原因失败）: {len(df_import_failures)} 条")

# 显示详细清单
print(f"\n" + "=" * 100)
print("导入失败记录详细清单（排除Excel重复和USCC为空）")
print("=" * 100)

print(f"\n{'序号':<5} {'机构名称':<45} {'USCC':<22} {'等级':<12} {'地区':<10}")
print("-" * 100)

for idx, (i, row) in enumerate(df_import_failures.iterrows(), 1):
    name = row['名字'][:43] if len(row['名字']) > 43 else row['名字']
    uscc = row['USCC'][:20]
    level_raw = row.iloc[col_level]
    level = level_raw if pd.notna(level_raw) and str(level_raw).strip() != '' else '[空值]'
    region = str(row.iloc[col_region])[:8] if pd.notna(row.iloc[col_region]) else '[空]'
    
    print(f"{idx:<5} {name:<45} {uscc:<22} {level:<12} {region:<10}")

# 按等级统计
print(f"\n" + "=" * 100)
print("失败记录等级统计")
print("=" * 100)

def process_level_for_stats(level):
    if pd.isna(level):
        return '[空值]'
    level_str = str(level).strip()
    if level_str == '' or level_str == 'nan':
        return '[空值]'
    return level_str

level_stats = df_import_failures.iloc[:, col_level].apply(process_level_for_stats).value_counts()
print(f"\n等级分布:")
for level, count in level_stats.items():
    print(f"   {level}: {count} 条")

# 检查这些记录的USCC在DB中的使用情况
print(f"\n" + "=" * 100)
print("失败原因分析")
print("=" * 100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    # 检查每个失败记录的USCC在DB中被谁占用
    print(f"\n详细分析（前20条）:")
    
    for idx, (i, row) in enumerate(df_import_failures.head(20).iterrows(), 1):
        name = row['名字']
        uscc = row['USCC']
        
        print(f"\n{idx}. {name}")
        print(f"   USCC: {uscc}")
        
        # 查询DB中是否有相同USCC
        cursor.execute("""
            SELECT name, level, region 
            FROM const_init_institutions 
            WHERE uscc = %s
            LIMIT 5
        """, (uscc,))
        
        db_records = cursor.fetchall()
        if db_records:
            print(f"   DB中使用此USCC的记录: {len(db_records)}个")
            for db_name, db_level, db_region in db_records[:3]:
                db_level_display = db_level if db_level else '[空]'
                db_region_display = db_region if db_region else '[空]'
                print(f"      - {db_name} ({db_level_display}, {db_region_display})")
            
            # 检查是否存在相同的(名字+USCC)
            cursor.execute("""
                SELECT id 
                FROM const_init_institutions 
                WHERE name = %s AND uscc = %s
            """, (name, uscc))
            
            same_key = cursor.fetchone()
            if same_key:
                print(f"   [DUPLICATE] DB中已存在完全相同的(名字+USCC)组合！")
            else:
                print(f"   [CONFLICT] USCC被其他机构占用，但(名字+USCC)组合不同")
        else:
            print(f"   [UNKNOWN] DB中未找到此USCC")
    
finally:
    cursor.close()
    conn.close()

# 导出
output_file = os.path.join(project_root, '导入失败的记录（其他原因）.xlsx')
output_data = df_import_failures.iloc[:, [col_name, col_region, col_type, col_level, col_uscc, col_nature, col_business]]
output_data.columns = ['机构名称', '地区', '机构类别', '等级', '统一社会信用代码', '机构性质', '经营性质']
output_data.to_excel(output_file, index=False, engine='openpyxl')

print(f"\n\n已导出失败记录到: {output_file}")

output_csv = os.path.join(project_root, '导入失败的记录（其他原因）.csv')
output_data.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"已导出失败记录到: {output_csv}")

print(f"\n检查完成！")
