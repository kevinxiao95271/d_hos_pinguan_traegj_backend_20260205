# -*- coding: utf-8 -*-
"""
分析共享USCC的挂靠机构特征
"""
import pandas as pd
import os
from collections import Counter

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("分析共享USCC的挂靠机构特征")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

# 列索引
col_name = 0        # 机构名称
col_region = 1      # 地区
col_type = 2        # 机构类别
col_nature = 3      # 机构性质
col_level = 4       # 等级
col_business = 5    # 经营性质
col_uscc = 6        # 统一社会信用代码

print(f"\nExcel总记录数: {len(df)}")
print(f"\n列信息:")
for i in range(7):
    print(f"  [{i}] {df.columns[i] if i < len(df.columns) else '(空列)'}")

# 统计重复USCC
uscc_column = df.iloc[:, col_uscc].astype(str).str.strip()
uscc_counts = uscc_column.value_counts()
duplicates = uscc_counts[uscc_counts > 1]

# 排除特殊值
duplicates_clean = duplicates[~duplicates.index.isin(['nan', '', '000000000000000000'])]

print(f"\n有效重复USCC数量: {len(duplicates_clean)}")
print(f"涉及记录数: {duplicates_clean.sum()}")

# 分析共享USCC的所有机构
print("\n" + "=" * 100)
print("分析共享USCC的机构特征")
print("=" * 100)

shared_uscc_records = []

for uscc, count in duplicates_clean.items():
    mask = df.iloc[:, col_uscc].astype(str).str.strip() == uscc
    records = df[mask]
    
    for idx, row in records.iterrows():
        name = str(row.iloc[col_name]).strip()
        inst_type = str(row.iloc[col_type]).strip() if pd.notna(row.iloc[col_type]) else '未知'
        nature = str(row.iloc[col_nature]).strip() if pd.notna(row.iloc[col_nature]) else '未知'
        level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '未定级'
        business = str(row.iloc[col_business]).strip() if pd.notna(row.iloc[col_business]) else '未知'
        region = str(row.iloc[col_region]).strip() if pd.notna(row.iloc[col_region]) else '未知'
        
        shared_uscc_records.append({
            'uscc': uscc,
            'name': name,
            'type': inst_type,
            'nature': nature,
            'level': level,
            'business': business,
            'region': region
        })

print(f"\n共享USCC的记录总数: {len(shared_uscc_records)}")

# 统计机构类别
print("\n" + "=" * 100)
print("按机构类别统计")
print("=" * 100)

type_counter = Counter([r['type'] for r in shared_uscc_records])
print(f"\n共有 {len(type_counter)} 种机构类别")
print(f"\n机构类别分布（Top 20）:")

for i, (inst_type, count) in enumerate(type_counter.most_common(20), 1):
    percentage = count / len(shared_uscc_records) * 100
    print(f"{i:2d}. {inst_type:<30} {count:>6} 条 ({percentage:>5.1f}%)")

# 统计机构性质
print("\n" + "=" * 100)
print("按机构性质统计")
print("=" * 100)

nature_counter = Counter([r['nature'] for r in shared_uscc_records])
print(f"\n共有 {len(nature_counter)} 种机构性质")
print(f"\n机构性质分布:")

for i, (nature, count) in enumerate(nature_counter.most_common(), 1):
    percentage = count / len(shared_uscc_records) * 100
    print(f"{i:2d}. {nature:<40} {count:>6} 条 ({percentage:>5.1f}%)")

# 统计等级
print("\n" + "=" * 100)
print("按等级统计")
print("=" * 100)

level_counter = Counter([r['level'] for r in shared_uscc_records])
print(f"\n等级分布:")

for i, (level, count) in enumerate(level_counter.most_common(), 1):
    percentage = count / len(shared_uscc_records) * 100
    print(f"{i:2d}. {level:<20} {count:>6} 条 ({percentage:>5.1f}%)")

# 统计经营性质
print("\n" + "=" * 100)
print("按经营性质统计")
print("=" * 100)

business_counter = Counter([r['business'] for r in shared_uscc_records])
print(f"\n经营性质分布:")

for i, (business, count) in enumerate(business_counter.most_common(), 1):
    percentage = count / len(shared_uscc_records) * 100
    print(f"{i:2d}. {business:<40} {count:>6} 条 ({percentage:>5.1f}%)")

# 名称关键词分析
print("\n" + "=" * 100)
print("按名称关键词统计")
print("=" * 100)

keywords = {
    '村卫生室': 0,
    '卫生室': 0,
    '卫生所': 0,
    '门诊部': 0,
    '医务室': 0,
    '卫生站': 0,
    '社区卫生': 0,
    '诊所': 0,
    '医疗点': 0,
    '分院': 0,
    '分部': 0,
    '院区': 0,
    '驻': 0
}

for record in shared_uscc_records:
    name = record['name']
    for keyword in keywords:
        if keyword in name:
            keywords[keyword] += 1

print(f"\n名称关键词分布:")
for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        percentage = count / len(shared_uscc_records) * 100
        print(f"  {keyword:<15} {count:>6} 条 ({percentage:>5.1f}%)")

# 交叉分析：村卫生室的类别
print("\n" + "=" * 100)
print("村卫生室的机构类别")
print("=" * 100)

village_health = [r for r in shared_uscc_records if '村卫生室' in r['name']]
print(f"\n名称包含'村卫生室'的记录: {len(village_health)} 条")

if village_health:
    village_type_counter = Counter([r['type'] for r in village_health])
    print(f"\n机构类别分布:")
    for i, (inst_type, count) in enumerate(village_type_counter.most_common(10), 1):
        percentage = count / len(village_health) * 100
        print(f"  {i}. {inst_type:<30} {count:>5} 条 ({percentage:>5.1f}%)")

# 示例展示
print("\n" + "=" * 100)
print("典型案例展示")
print("=" * 100)

# 找一个典型的USCC
for uscc, count in duplicates_clean.most_common(3):
    print(f"\nUSCC: {uscc} (共{count}条记录)")
    
    uscc_records = [r for r in shared_uscc_records if r['uscc'] == uscc]
    
    # 统计这个USCC下的机构类别
    type_dist = Counter([r['type'] for r in uscc_records])
    print(f"  机构类别: {dict(type_dist)}")
    
    # 显示前5条
    print(f"  前5条记录:")
    for i, r in enumerate(uscc_records[:5], 1):
        print(f"    {i}. {r['name']}")
        print(f"       类别: {r['type']}, 性质: {r['nature']}")

# 总结
print("\n" + "=" * 100)
print("总结")
print("=" * 100)

print(f"""
共享USCC的机构特征分析：

1. 总数统计:
   - 共享USCC的记录总数: {len(shared_uscc_records)}
   - 占Excel总记录的比例: {len(shared_uscc_records)/len(df)*100:.1f}%

2. 机构类别特征:
   - 主要类别: {type_counter.most_common(1)[0][0]} ({type_counter.most_common(1)[0][1]}条)
   - 类别多样性: {len(type_counter)}种

3. 名称特征:
   - 包含'村卫生室': {keywords['村卫生室']}条 ({keywords['村卫生室']/len(shared_uscc_records)*100:.1f}%)
   - 包含'门诊部': {keywords['门诊部']}条 ({keywords['门诊部']/len(shared_uscc_records)*100:.1f}%)
   - 包含'卫生所': {keywords['卫生所']}条 ({keywords['卫生所']/len(shared_uscc_records)*100:.1f}%)

4. 等级特征:
   - 未定级: {level_counter.get('未定级', 0)}条 ({level_counter.get('未定级', 0)/len(shared_uscc_records)*100:.1f}%)
   - 有等级: {len(shared_uscc_records) - level_counter.get('未定级', 0)}条

5. 结论:
   {'主要是基层医疗机构' if keywords['村卫生室'] > len(shared_uscc_records) * 0.3 else '包含多种类型机构'}
""")

print("\n分析完成！")
