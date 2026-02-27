# -*- coding: utf-8 -*-
"""
对比Excel和DB中的机构等级数据
以 (名字+USCC) 作为唯一标识进行匹配
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
print("对比 Excel vs DB 的机构等级数据")
print("=" * 100)

# 1. 读取Excel数据
print("\n[1/5] 读取Excel数据...")
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_type = 2
col_nature = 3
col_level = 4
col_business = 5
col_uscc = 6

print(f"   Excel总记录数: {len(df_excel)}")

# 标准化Excel数据
df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['等级_原始'] = df_excel.iloc[:, col_level]

# Excel等级标准化（Excel为空 -> "无等级"）
def normalize_excel_level(level):
    if pd.isna(level) or level == '' or level == '未定级':
        return '无等级'
    level_str = str(level).strip()
    if level_str in ['', 'nan', 'None', '未定级']:
        return '无等级'
    return level_str

df_excel['等级_标准'] = df_excel['等级_原始'].apply(normalize_excel_level)

print(f"   Excel等级分布:")
level_counts = df_excel['等级_标准'].value_counts()
for level, count in level_counts.items():
    print(f"      {level}: {count}")

# 2. 读取DB数据
print(f"\n[2/5] 读取数据库数据...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = """
        SELECT 
            id,
            name,
            uscc,
            level,
            region
        FROM const_init_institutions
        WHERE name IS NOT NULL 
          AND uscc IS NOT NULL
          AND uscc != ''
    """
    df_db = pd.read_sql(query, conn)
    print(f"   DB总记录数: {len(df_db)}")
    
    # DB等级标准化
    def normalize_db_level(level):
        if pd.isna(level) or level == '':
            return '无等级'
        level_str = str(level).strip()
        # DB中的"未定等"、"无级别"、"未定级"都应该标准化为"无等级"
        if level_str in ['', 'nan', 'None', '未定等', '无级别', '未定级']:
            return '无等级'
        return level_str
    
    df_db['等级_标准'] = df_db['level'].apply(normalize_db_level)
    
    print(f"   DB等级分布:")
    db_level_counts = df_db['等级_标准'].value_counts()
    for level, count in db_level_counts.items():
        print(f"      {level}: {count}")
    
finally:
    conn.close()

# 3. 按 (名字+USCC) 匹配
print(f"\n[3/5] 按 (名字+USCC) 匹配...")

# 创建匹配键
df_excel['匹配键'] = df_excel['名字'] + '|||' + df_excel['USCC']
df_db['匹配键'] = df_db['name'] + '|||' + df_db['uscc']

# 合并数据
df_merged = pd.merge(
    df_excel[['匹配键', '名字', 'USCC', '等级_原始', '等级_标准']],
    df_db[['匹配键', 'id', '等级_标准']],
    on='匹配键',
    how='outer',
    suffixes=('_excel', '_db'),
    indicator=True
)

print(f"   匹配结果:")
print(f"      Excel和DB都有: {len(df_merged[df_merged['_merge'] == 'both'])}")
print(f"      仅在Excel: {len(df_merged[df_merged['_merge'] == 'left_only'])}")
print(f"      仅在DB: {len(df_merged[df_merged['_merge'] == 'right_only'])}")

# 4. 分析等级差异
print(f"\n[4/5] 分析等级差异...")

# 只看Excel和DB都有的记录
df_both = df_merged[df_merged['_merge'] == 'both'].copy()

# 标记差异
df_both['等级一致'] = df_both['等级_标准_excel'] == df_both['等级_标准_db']

consistent_count = df_both['等级一致'].sum()
inconsistent_count = len(df_both) - consistent_count

print(f"\n   等级一致性:")
print(f"      一致: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)")
print(f"      不一致: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)")

# 5. 详细差异分析
print(f"\n[5/5] 生成详细报告...")

if inconsistent_count > 0:
    df_diff = df_both[~df_both['等级一致']].copy()
    
    print(f"\n" + "=" * 100)
    print("等级不一致的记录详情")
    print("=" * 100)
    
    # 按差异类型分组
    diff_types = df_diff.groupby(['等级_标准_excel', '等级_标准_db']).size().sort_values(ascending=False)
    
    print(f"\n差异类型统计:")
    for (excel_level, db_level), count in diff_types.items():
        print(f"   Excel: [{excel_level}] -> DB: [{db_level}]: {count} 条")
    
    # 显示前50条详细记录
    print(f"\n前50条不一致的记录:")
    print(f"{'序号':<5} {'机构名称':<40} {'Excel等级':<10} {'DB等级':<10} {'USCC':<20}")
    print("-" * 100)
    
    for i, row in df_diff.head(50).iterrows():
        name = row['名字'][:38] if len(row['名字']) > 38 else row['名字']
        excel_level = str(row['等级_标准_excel'])
        db_level = str(row['等级_标准_db'])
        uscc = str(row['USCC'])[:18]
        
        print(f"{i+1:<5} {name:<40} {excel_level:<10} {db_level:<10} {uscc:<20}")
    
    if len(df_diff) > 50:
        print(f"\n... 还有 {len(df_diff) - 50} 条不一致记录 ...")
    
    # 导出详细报告
    output_file = os.path.join(project_root, '等级差异报告.xlsx')
    
    # 准备导出数据
    df_export = df_diff[[
        '名字', 'USCC', '等级_原始', '等级_标准_excel', 
        '等级_标准_db', 'id'
    ]].copy()
    df_export.columns = [
        '机构名称', '统一社会信用代码', 'Excel等级(原始)', 
        'Excel等级(标准)', 'DB等级', 'DB记录ID'
    ]
    
    df_export.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n已导出详细差异报告到: {output_file}")
    
    # 也导出CSV
    output_csv = os.path.join(project_root, '等级差异报告.csv')
    df_export.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"已导出详细差异报告到: {output_csv}")

else:
    print(f"\n[OK] 所有记录的等级数据完全一致！")

# 统计Excel中未导入DB的记录
df_only_excel = df_merged[df_merged['_merge'] == 'left_only']
if len(df_only_excel) > 0:
    print(f"\n" + "=" * 100)
    print(f"Excel中有但DB中没有的记录: {len(df_only_excel)} 条")
    print("=" * 100)
    
    # 分析这些记录的等级分布
    print(f"\n这些未导入记录的等级分布:")
    missing_level_counts = df_only_excel['等级_标准_excel'].value_counts()
    for level, count in missing_level_counts.items():
        print(f"   {level}: {count}")
    
    # 导出未导入的记录
    output_missing = os.path.join(project_root, 'Excel中有DB中无的记录.xlsx')
    df_only_excel[[
        '名字', 'USCC', '等级_原始', '等级_标准_excel'
    ]].to_excel(output_missing, index=False, engine='openpyxl')
    print(f"\n已导出未导入记录清单到: {output_missing}")

# 汇总报告
print(f"\n" + "=" * 100)
print("对比汇总")
print("=" * 100)

print(f"\n[数据量]")
print(f"   Excel总记录: {len(df_excel)}")
print(f"   DB总记录: {len(df_db)}")
print(f"   匹配成功: {len(df_both)}")
print(f"   Excel独有: {len(df_only_excel)}")

if len(df_both) > 0:
    print(f"\n[等级一致性]")
    print(f"   一致: {consistent_count} ({consistent_count/len(df_both)*100:.2f}%)")
    print(f"   不一致: {inconsistent_count} ({inconsistent_count/len(df_both)*100:.2f}%)")

print(f"\n[结论]")
if inconsistent_count == 0:
    print(f"   [OK] 所有已导入记录的等级数据与Excel完全一致")
elif inconsistent_count < 100:
    print(f"   [WARN] 有{inconsistent_count}条记录等级不一致，建议检查后修正")
else:
    print(f"   [ERROR] 有{inconsistent_count}条记录等级不一致，需要批量更新")

if len(df_only_excel) > 0:
    print(f"   [WARN] 有{len(df_only_excel)}条Excel记录未导入DB（可能因uk_uscc约束）")

print(f"\n检查完成！")
