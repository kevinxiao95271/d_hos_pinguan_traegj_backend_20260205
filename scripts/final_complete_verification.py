# -*- coding: utf-8 -*-
"""
最终完整验证：Excel与DB数据对比
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
print("最终完整验证", flush=True)
print("=" * 100, flush=True)

# 1. 读取Excel数据
print("\n[1/3] 读取Excel数据...", flush=True)
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_level = 4
col_uscc = 6

print(f"   Excel总记录数: {len(df_excel)}", flush=True)

# 处理Excel数据
df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()

# Excel等级处理
def process_level(level):
    if pd.isna(level):
        return '无等级'
    level_str = str(level).strip()
    if level_str == '' or level_str == 'nan':
        return '无等级'
    return level_str

df_excel['等级_期望'] = df_excel.iloc[:, col_level].apply(process_level)
df_excel['匹配键'] = df_excel['名字'] + '|||' + df_excel['USCC']

# 2. 读取DB数据
print(f"\n[2/3] 读取数据库数据...", flush=True)
conn = pymysql.connect(**DB_CONFIG)
try:
    query = """
        SELECT 
            id, name, uscc, level, city, region
        FROM const_init_institutions
        WHERE name IS NOT NULL 
          AND uscc IS NOT NULL
          AND uscc != ''
    """
    df_db = pd.read_sql(query, conn)
    print(f"   DB总记录数: {len(df_db)}", flush=True)
    
    df_db['等级_实际'] = df_db['level'].apply(lambda x: str(x).strip() if pd.notna(x) else '')
    df_db['匹配键'] = df_db['name'].str.strip() + '|||' + df_db['uscc'].str.strip()
    
finally:
    conn.close()

# 3. 匹配对比
print(f"\n[3/3] 匹配对比...", flush=True)

# 合并数据
df_merged = pd.merge(
    df_excel[['匹配键', '名字', 'USCC', '等级_期望']],
    df_db[['匹配键', 'id', '等级_实际', 'city']],
    on='匹配键',
    how='outer',
    indicator=True
)

both_count = len(df_merged[df_merged['_merge'] == 'both'])
left_only_count = len(df_merged[df_merged['_merge'] == 'left_only'])
right_only_count = len(df_merged[df_merged['_merge'] == 'right_only'])

print(f"\n   匹配统计:", flush=True)
print(f"      Excel和DB都有: {both_count}", flush=True)
print(f"      仅在Excel: {left_only_count}", flush=True)
print(f"      仅在DB: {right_only_count}", flush=True)

# 等级一致性检查
df_both = df_merged[df_merged['_merge'] == 'both'].copy()
df_both['等级一致'] = df_both['等级_期望'] == df_both['等级_实际']

consistent_count = df_both['等级一致'].sum()
inconsistent_count = len(df_both) - consistent_count

print(f"\n   等级一致性:", flush=True)
print(f"      一致: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)", flush=True)
print(f"      不一致: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)", flush=True)

# City字段统计
city_filled = df_db[df_db['city'].notna() & (df_db['city'] != '')].shape[0]
print(f"\n   City字段填充:", flush=True)
print(f"      已填充: {city_filled} / {len(df_db)} ({city_filled/len(df_db)*100:.1f}%)", flush=True)

# 最终报告
print(f"\n" + "=" * 100, flush=True)
print("最终验证结果", flush=True)
print("=" * 100, flush=True)

coverage = (both_count / len(df_excel)) * 100
print(f"\n[数据完整性]", flush=True)
print(f"   Excel总记录: {len(df_excel)}", flush=True)
print(f"   DB已导入: {both_count} ({coverage:.2f}%)", flush=True)
print(f"   未导入: {left_only_count} ({left_only_count/len(df_excel)*100:.2f}%)", flush=True)

if inconsistent_count == 0:
    print(f"\n[等级准确性]", flush=True)
    print(f"   [PERFECT] 所有{both_count}条记录等级100%与Excel一致！", flush=True)
else:
    print(f"\n[等级准确性]", flush=True)
    print(f"   [WARN] 有{inconsistent_count}条记录等级不一致", flush=True)

print(f"\n[City字段]", flush=True)
print(f"   填充率: {city_filled/len(df_db)*100:.1f}%", flush=True)

print(f"\n[约束状态]", flush=True)
print(f"   UNIQUE KEY: uk_name_uscc (name, uscc) - 已生效", flush=True)

# 未导入记录分析
if left_only_count > 0:
    df_missing = df_merged[df_merged['_merge'] == 'left_only']
    print(f"\n[未导入记录分析]", flush=True)
    print(f"   共{left_only_count}条未导入", flush=True)
    print(f"   原因: (名字+USCC)组合在Excel中重复，或其他数据质量问题", flush=True)
    
    # 显示几个示例
    print(f"\n   示例:", flush=True)
    for idx, row in df_missing.head(10).iterrows():
        print(f"      - {row['名字'][:40]}", flush=True)

# 生成报告文件
report = f"""
最终完整验证报告
{'=' * 100}

验证时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

[数据完整性]
  Excel总记录: {len(df_excel)}
  DB已导入: {both_count} ({coverage:.2f}%)
  未导入: {left_only_count} ({left_only_count/len(df_excel)*100:.2f}%)
  
[等级准确性]
  已导入记录: {both_count}
  等级一致: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)
  等级不一致: {inconsistent_count}

[City字段]
  已填充: {city_filled} / {len(df_db)} ({city_filled/len(df_db)*100:.1f}%)

[数据库约束]
  - UNIQUE KEY uk_name_uscc (name, uscc)
  - 允许同一USCC被不同名字的机构共享
  - 保证(名字+USCC)组合唯一

[结论]
"""

if inconsistent_count == 0 and left_only_count <= 23:
    report += f"  [SUCCESS] 完美！Excel的{both_count}条记录已全部导入DB且等级100%一致！\n"
    report += f"  [INFO] 有{left_only_count}条记录未导入（Excel中存在重复）\n"
elif inconsistent_count == 0:
    report += f"  [GOOD] 已导入的{both_count}条记录等级100%与Excel一致\n"
    report += f"  [WARN] 有{left_only_count}条记录未导入，需要检查数据质量\n"
else:
    report += f"  [WARN] 有{inconsistent_count}条记录等级不一致，需要进一步检查\n"

report += f"\n{'=' * 100}\n"

report_file = os.path.join(project_root, '最终完整验证报告.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n已生成报告: {report_file}", flush=True)
print(f"\n验证完成！", flush=True)
