# -*- coding: utf-8 -*-
"""
导出共享USCC且等级为三级/二级的机构清单
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("导出共享USCC且等级为三级/二级的机构清单")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

print(f"\nExcel总记录数: {len(df)}")
print(f"Excel总列数: {len(df.columns)}")

# 显示所有列名
print(f"\n所有列名:")
for i, col in enumerate(df.columns):
    print(f"  [{i}] {col}")

# 列索引
col_uscc = 6  # 统一社会信用代码
col_level = 4  # 医疗机构等级

# 统计重复USCC
uscc_column = df.iloc[:, col_uscc].astype(str).str.strip()
uscc_counts = uscc_column.value_counts()
duplicates = uscc_counts[uscc_counts > 1]

# 排除特殊值
duplicates_clean = duplicates[~duplicates.index.isin(['nan', '', '000000000000000000'])]

print(f"\n有效重复USCC数量: {len(duplicates_clean)}")

# 找出所有共享USCC的记录
shared_uscc_set = set(duplicates_clean.index)

# 筛选：共享USCC 且 等级为三级或二级
result_df = df[
    (df.iloc[:, col_uscc].astype(str).str.strip().isin(shared_uscc_set)) &
    (df.iloc[:, col_level].isin(['三级', '二级']))
].copy()

print(f"\n筛选结果:")
print(f"  三级: {len(result_df[result_df.iloc[:, col_level] == '三级'])} 条")
print(f"  二级: {len(result_df[result_df.iloc[:, col_level] == '二级'])} 条")
print(f"  总计: {len(result_df)} 条")

# 按USCC分组统计
print(f"\n按USCC分组统计:")
result_uscc_counts = result_df.iloc[:, col_uscc].value_counts()
print(f"  涉及的USCC数量: {len(result_uscc_counts)}")

# 添加额外信息列：该USCC的总记录数
result_df['该USCC总记录数'] = result_df.iloc[:, col_uscc].map(
    df.iloc[:, col_uscc].value_counts()
)

# 排序：按USCC、等级
result_df = result_df.sort_values(
    by=[df.columns[col_uscc], df.columns[col_level]], 
    ascending=[True, False]
)

# 导出到Excel
output_file = os.path.join(project_root, '共享USCC的三级二级机构清单.xlsx')
result_df.to_excel(output_file, index=False, engine='openpyxl')
print(f"\nOK: Exported to Excel: {output_file}")

# 同时导出CSV（如果Excel有问题可以用CSV）
output_csv = os.path.join(project_root, '共享USCC的三级二级机构清单.csv')
result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"OK: Exported to CSV: {output_csv}")

# 显示前20条预览
print(f"\n" + "=" * 100)
print("前20条预览")
print("=" * 100)

for idx, row in result_df.head(20).iterrows():
    print(f"\n{list(result_df.index).index(idx) + 1}. {row[df.columns[0]]}")  # 机构名称
    print(f"   地区: {row[df.columns[1]]}")
    print(f"   机构类别: {row[df.columns[2]]}")
    print(f"   机构性质: {row[df.columns[3]]}")
    print(f"   等级: {row[df.columns[4]]}")
    print(f"   经营性质: {row[df.columns[5]]}")
    print(f"   USCC: {row[df.columns[6]]}")
    print(f"   该USCC总记录数: {row['该USCC总记录数']}")

# 按USCC分组展示
print(f"\n" + "=" * 100)
print("按USCC分组展示（前10组）")
print("=" * 100)

grouped_count = 0
for uscc, group in result_df.groupby(df.columns[col_uscc]):
    grouped_count += 1
    if grouped_count > 10:
        break
    
    print(f"\n【USCC: {uscc}】 (该USCC共{group.iloc[0]['该USCC总记录数']}条记录)")
    
    for idx, row in group.iterrows():
        print(f"  - {row[df.columns[0]]}")
        print(f"    等级: {row[df.columns[4]]}, 地区: {row[df.columns[1]]}")
        print(f"    机构性质: {row[df.columns[3]]}")

# 统计分析
print(f"\n" + "=" * 100)
print("统计分析")
print("=" * 100)

# 1. 按地区统计
region_stats = result_df[df.columns[1]].value_counts()
print(f"\n1. 按地区统计 (Top 10):")
for i, (region, count) in enumerate(region_stats.head(10).items(), 1):
    print(f"  {i:2d}. {region:<15} {count:>3} 条")

# 2. 按机构类别统计
type_stats = result_df[df.columns[2]].value_counts()
print(f"\n2. 按机构类别统计 (Top 10):")
for i, (inst_type, count) in enumerate(type_stats.head(10).items(), 1):
    print(f"  {i:2d}. {inst_type:<30} {count:>3} 条")

# 3. 按机构性质统计
nature_stats = result_df[df.columns[3]].value_counts()
print(f"\n3. 按机构性质统计:")
for i, (nature, count) in enumerate(nature_stats.items(), 1):
    print(f"  {i:2d}. {nature:<40} {count:>3} 条")

# 4. 按等级统计
level_stats = result_df[df.columns[4]].value_counts()
print(f"\n4. 按等级统计:")
for level, count in level_stats.items():
    print(f"  {level}: {count} 条")

# 5. 名称关键词分析
print(f"\n5. 名称关键词分析:")
keywords = ['分院', '分部', '院区', '驻', '门诊部', '医务室', '卫生室']
for keyword in keywords:
    count = result_df[df.columns[0]].str.contains(keyword, na=False).sum()
    if count > 0:
        percentage = count / len(result_df) * 100
        print(f"  {keyword:<10} {count:>3} 条 ({percentage:>5.1f}%)")

# 6. 特殊案例：同一USCC下既有三级又有二级
print(f"\n6. 特殊案例：同一USCC下既有三级又有二级")
for uscc, group in result_df.groupby(df.columns[col_uscc]):
    levels = group[df.columns[col_level]].unique()
    if '三级' in levels and '二级' in levels:
        print(f"\n  USCC: {uscc}")
        for idx, row in group.iterrows():
            print(f"    - {row[df.columns[0]]} [{row[df.columns[4]]}]")

print(f"\n" + "=" * 100)
print("导出完成！")
print("=" * 100)
print(f"\n文件位置:")
print(f"  Excel: {output_file}")
print(f"  CSV: {output_csv}")
