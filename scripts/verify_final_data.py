# -*- coding: utf-8 -*-
"""
最终验证：Excel与DB数据对比
验证规则：
1. 以(名字+USCC)作为唯一key
2. Excel空值 -> DB应该是"无等级"
3. Excel有值 -> DB应该原样保持Excel的值
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

print("=" * 100, flush=True)
print("最终验证：Excel vs DB 数据对比", flush=True)
print("=" * 100, flush=True)

# 1. 读取Excel数据
print("\n[1/4] 读取Excel数据...", flush=True)
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_level = 4
col_uscc = 6

print(f"   Excel总记录数: {len(df_excel)}", flush=True)

# 处理Excel数据
df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['等级_原始'] = df_excel.iloc[:, col_level]

# Excel等级处理：空值标准化为"无等级"，有值保持原样
def process_excel_level(level):
    if pd.isna(level):
        return '无等级'
    level_str = str(level).strip()
    if level_str == '' or level_str == 'nan':
        return '无等级'
    return level_str

df_excel['等级_期望'] = df_excel['等级_原始'].apply(process_excel_level)

print(f"\n   Excel等级分布:", flush=True)
level_counts = df_excel['等级_期望'].value_counts()
for level, count in level_counts.items():
    print(f"      {level}: {count}", flush=True)

# 2. 读取DB数据
print(f"\n[2/4] 读取数据库数据...", flush=True)
conn = pymysql.connect(**DB_CONFIG)
try:
    query = """
        SELECT 
            id,
            name,
            uscc,
            level,
            region,
            code
        FROM const_init_institutions
        WHERE name IS NOT NULL 
          AND uscc IS NOT NULL
          AND uscc != ''
    """
    df_db = pd.read_sql(query, conn)
    print(f"   DB总记录数: {len(df_db)}", flush=True)
    
    # DB等级处理：空值转为空字符串便于对比
    def process_db_level(level):
        if pd.isna(level):
            return ''
        return str(level).strip()
    
    df_db['等级_实际'] = df_db['level'].apply(process_db_level)
    
    print(f"\n   DB等级分布:", flush=True)
    db_level_counts = df_db['等级_实际'].value_counts()
    for level, count in db_level_counts.head(20).items():
        display_level = level if level != '' else '[空值]'
        print(f"      {display_level}: {count}", flush=True)
    
finally:
    conn.close()

# 3. 按 (名字+USCC) 匹配对比
print(f"\n[3/4] 按 (名字+USCC) 匹配对比...", flush=True)

df_excel['匹配键'] = df_excel['名字'] + '|||' + df_excel['USCC']
df_db['匹配键'] = df_db['name'] + '|||' + df_db['uscc']

# 合并数据
df_merged = pd.merge(
    df_excel[['匹配键', '名字', 'USCC', '等级_原始', '等级_期望']],
    df_db[['匹配键', 'id', '等级_实际', 'code']],
    on='匹配键',
    how='outer',
    indicator=True
)

print(f"\n   匹配统计:", flush=True)
both_count = len(df_merged[df_merged['_merge'] == 'both'])
left_only_count = len(df_merged[df_merged['_merge'] == 'left_only'])
right_only_count = len(df_merged[df_merged['_merge'] == 'right_only'])

print(f"      Excel和DB都有: {both_count}", flush=True)
print(f"      仅在Excel: {left_only_count}", flush=True)
print(f"      仅在DB: {right_only_count}", flush=True)

# 只分析Excel和DB都有的记录
df_both = df_merged[df_merged['_merge'] == 'both'].copy()

# 判断等级是否一致
df_both['等级一致'] = df_both['等级_期望'] == df_both['等级_实际']

consistent_count = df_both['等级一致'].sum()
inconsistent_count = len(df_both) - consistent_count

print(f"\n   等级一致性:", flush=True)
print(f"      一致: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)", flush=True)
print(f"      不一致: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)", flush=True)

# 4. 生成详细报告
print(f"\n[4/4] 生成验证报告...", flush=True)

# 如果有不一致的记录
if inconsistent_count > 0:
    df_diff = df_both[~df_both['等级一致']].copy()
    
    print(f"\n" + "=" * 100, flush=True)
    print("发现不一致记录！", flush=True)
    print("=" * 100, flush=True)
    
    # 统计不一致类型
    diff_types = df_diff.groupby(['等级_期望', '等级_实际']).size().sort_values(ascending=False)
    
    print(f"\n不一致类型统计:", flush=True)
    for (excel_level, db_level), count in diff_types.head(20).items():
        excel_display = excel_level if excel_level != '' else '[空]'
        db_display = db_level if db_level != '' else '[空]'
        print(f"   Excel期望: [{excel_display}] -> DB实际: [{db_display}]: {count} 条", flush=True)
    
    # 显示详细记录
    print(f"\n前30条不一致记录:", flush=True)
    print(f"   {'ID':<10} {'机构名称':<40} {'Excel原始':<12} {'Excel期望':<12} {'DB实际':<12}", flush=True)
    print("   " + "-" * 95, flush=True)
    
    for idx, (i, row) in enumerate(df_diff.head(30).iterrows(), 1):
        db_id = int(row['id']) if pd.notna(row['id']) else 0
        name = row['名字'][:38] if len(row['名字']) > 38 else row['名字']
        excel_raw = str(row['等级_原始']) if pd.notna(row['等级_原始']) else '[空]'
        excel_expect = str(row['等级_期望'])
        db_actual = str(row['等级_实际']) if row['等级_实际'] != '' else '[空]'
        
        print(f"   {db_id:<10} {name:<40} {excel_raw:<12} {excel_expect:<12} {db_actual:<12}", flush=True)
    
    # 导出不一致记录
    output_file = os.path.join(project_root, '最终验证-仍存在差异.xlsx')
    df_export = df_diff[['名字', 'USCC', '等级_原始', '等级_期望', '等级_实际', 'id', 'code']].copy()
    df_export.columns = ['机构名称', '统一社会信用代码', 'Excel等级(原始)', 'Excel等级(期望)', 'DB等级(实际)', 'DB记录ID', '机构编码']
    df_export.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n   已导出不一致记录到: {output_file}", flush=True)

else:
    print(f"\n" + "=" * 100, flush=True)
    print("[OK] 所有记录等级完全一致！", flush=True)
    print("=" * 100, flush=True)

# Excel中未导入DB的记录
df_only_excel = df_merged[df_merged['_merge'] == 'left_only']
if left_only_count > 0:
    print(f"\n" + "-" * 100, flush=True)
    print(f"Excel中有但DB中没有的记录: {left_only_count} 条", flush=True)
    print("-" * 100, flush=True)
    
    print(f"\n未导入记录的等级分布:", flush=True)
    missing_level_counts = df_only_excel['等级_期望'].value_counts()
    for level, count in missing_level_counts.items():
        print(f"   {level}: {count}", flush=True)
    
    # 导出未导入的记录
    output_missing = os.path.join(project_root, '最终验证-未导入记录.xlsx')
    df_export_missing = df_only_excel[['名字', 'USCC', '等级_原始', '等级_期望']].copy()
    df_export_missing.columns = ['机构名称', '统一社会信用代码', 'Excel等级(原始)', 'Excel等级(标准)']
    df_export_missing.to_excel(output_missing, index=False, engine='openpyxl')
    print(f"\n   已导出未导入记录到: {output_missing}", flush=True)

# 生成汇总报告
print(f"\n" + "=" * 100, flush=True)
print("验证汇总", flush=True)
print("=" * 100, flush=True)

print(f"\n[数据量统计]", flush=True)
print(f"   Excel总记录: {len(df_excel)}", flush=True)
print(f"   DB总记录: {len(df_db)}", flush=True)
print(f"   成功匹配: {both_count}", flush=True)
print(f"   Excel独有(未导入): {left_only_count}", flush=True)
print(f"   DB独有: {right_only_count}", flush=True)

if both_count > 0:
    print(f"\n[等级一致性]", flush=True)
    print(f"   一致记录: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)", flush=True)
    print(f"   不一致记录: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)", flush=True)

print(f"\n[最终结论]", flush=True)
if inconsistent_count == 0 and left_only_count == 0:
    print(f"   [PERFECT] 完美！所有Excel记录已导入且等级完全一致！", flush=True)
elif inconsistent_count == 0:
    print(f"   [GOOD] 已导入记录的等级完全一致！", flush=True)
    print(f"   [INFO] 有{left_only_count}条Excel记录未导入DB（可能因uk_uscc约束）", flush=True)
else:
    print(f"   [WARN] 仍有{inconsistent_count}条记录等级不一致，需要进一步检查！", flush=True)

# 生成文本报告
report = f"""
最终验证报告
{'=' * 100}

验证时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
验证规则: (名字+USCC)作为唯一key，Excel空值->DB填"无等级"，Excel有值->DB原样保持

[数据量统计]
  Excel总记录: {len(df_excel)}
  DB总记录: {len(df_db)}
  成功匹配: {both_count}
  Excel独有(未导入): {left_only_count}
  DB独有: {right_only_count}

[等级一致性]
  一致记录: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)
  不一致记录: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)

[最终结论]
"""

if inconsistent_count == 0 and left_only_count == 0:
    report += "  [PERFECT] 完美！所有Excel记录已导入且等级完全一致！\n"
elif inconsistent_count == 0:
    report += "  [GOOD] 已导入记录的等级完全一致！\n"
    report += f"  [INFO] 有{left_only_count}条Excel记录未导入DB（可能因uk_uscc约束）\n"
else:
    report += f"  [WARN] 仍有{inconsistent_count}条记录等级不一致！\n"

if inconsistent_count > 0:
    report += "\n[不一致类型]\n"
    for (excel_level, db_level), count in diff_types.head(10).items():
        excel_display = excel_level if excel_level != '' else '[空]'
        db_display = db_level if db_level != '' else '[空]'
        report += f"  Excel: {excel_display} -> DB: {db_display} = {count}条\n"

report += f"\n{'=' * 100}\n"

report_file = os.path.join(project_root, '最终验证报告.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n已生成验证报告: {report_file}", flush=True)
print(f"\n验证完成！", flush=True)
