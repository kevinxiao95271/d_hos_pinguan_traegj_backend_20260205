# -*- coding: utf-8 -*-
"""
检查Excel中 (名字+USCC) 组合的唯一性
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("检查 (名字+USCC) 组合的唯一性")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = 0
col_uscc = 6
col_level = 4
col_region = 1

print(f"\nExcel总记录数: {len(df)}")

# 创建 (名字+USCC) 组合列
df['名字_USCC'] = df.iloc[:, col_name].astype(str).str.strip() + '|||' + df.iloc[:, col_uscc].astype(str).str.strip()

# 统计组合的重复情况
combination_counts = df['名字_USCC'].value_counts()
duplicates = combination_counts[combination_counts > 1]

print(f"\n" + "=" * 100)
print("唯一性检查结果")
print("=" * 100)

print(f"\n[统计结果]")
print(f"  不同的(名字+USCC)组合数: {len(combination_counts)}")
print(f"  总记录数: {len(df)}")
print(f"  重复的组合数量: {len(duplicates)}")
print(f"  涉及的记录数: {duplicates.sum()}")

if len(duplicates) == 0:
    print(f"\n[OK] (名字+USCC) 组合是唯一的！")
    print(f"    可以安全地作为唯一标识使用。")
else:
    print(f"\n[DUPLICATE] 发现重复！(名字+USCC) 组合不唯一！")
    print(f"    有 {len(duplicates)} 个组合重复出现")
    print(f"    涉及 {duplicates.sum()} 条记录")

# 如果有重复，显示详细信息
if len(duplicates) > 0:
    print(f"\n" + "=" * 100)
    print("重复记录详细信息")
    print("=" * 100)
    
    for i, (combo, count) in enumerate(duplicates.head(30).items(), 1):
        # 解析组合
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            
            # 找到所有匹配的记录
            mask = (df.iloc[:, col_name].astype(str).str.strip() == name) & \
                   (df.iloc[:, col_uscc].astype(str).str.strip() == uscc)
            matched = df[mask]
            
            print(f"\n{i}. 名字: {name}")
            print(f"   USCC: {uscc}")
            print(f"   重复次数: {count}")
            print(f"   详细信息:")
            
            for idx, row in matched.iterrows():
                print(f"      - 地区: {row.iloc[col_region]}")
                print(f"        等级: {row.iloc[col_level] if pd.notna(row.iloc[col_level]) else '空值'}")
                print(f"        机构类别: {row.iloc[2] if pd.notna(row.iloc[2]) else '空值'}")
                print(f"        机构性质: {row.iloc[3] if pd.notna(row.iloc[3]) else '空值'}")
                print(f"        经营性质: {row.iloc[5] if pd.notna(row.iloc[5]) else '空值'}")
                print()
    
    # 分析重复的原因
    print(f"\n" + "=" * 100)
    print("重复原因分析")
    print("=" * 100)
    
    # 统计：是否所有字段都相同
    all_same_count = 0
    partial_diff_count = 0
    
    for combo, count in duplicates.items():
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            mask = (df.iloc[:, col_name].astype(str).str.strip() == name) & \
                   (df.iloc[:, col_uscc].astype(str).str.strip() == uscc)
            matched = df[mask]
            
            # 检查其他字段是否完全相同
            regions = matched.iloc[:, col_region].unique()
            levels = matched.iloc[:, col_level].unique()
            
            if len(regions) == 1 and len(levels) == 1:
                all_same_count += 1
            else:
                partial_diff_count += 1
    
    print(f"\n1. 所有字段完全相同（真正的重复数据）: {all_same_count} 个组合")
    print(f"2. 名字+USCC相同，但其他字段不同: {partial_diff_count} 个组合")
    
    # 导出重复记录
    if len(duplicates) > 0:
        duplicate_records = df[df['名字_USCC'].isin(duplicates.index)].copy()
        duplicate_records = duplicate_records.drop('名字_USCC', axis=1)
        duplicate_records = duplicate_records.sort_values(by=[df.columns[col_name], df.columns[col_uscc]])
        
        output_file = os.path.join(project_root, '名字+USCC重复的记录.xlsx')
        duplicate_records.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已导出重复记录到: {output_file}")
        
        output_csv = os.path.join(project_root, '名字+USCC重复的记录.csv')
        duplicate_records.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"已导出重复记录到: {output_csv}")

# 验证：按单独USCC vs 按(名字+USCC)
print(f"\n" + "=" * 100)
print("对比分析")
print("=" * 100)

uscc_only = df.iloc[:, col_uscc].value_counts()
duplicate_uscc = uscc_only[uscc_only > 1]
duplicate_uscc_clean = duplicate_uscc[~duplicate_uscc.index.isin(['nan', '', '000000000000000000'])]

print(f"\n[按单独USCC]")
print(f"  不同的USCC数: {len(uscc_only)}")
print(f"  重复的USCC数: {len(duplicate_uscc_clean)}")
print(f"  涉及记录数: {duplicate_uscc_clean.sum()}")

print(f"\n[按(名字+USCC)组合]")
print(f"  不同的组合数: {len(combination_counts)}")
print(f"  重复的组合数: {len(duplicates)}")
print(f"  涉及记录数: {duplicates.sum() if len(duplicates) > 0 else 0}")

print(f"\n[结论]")
if len(duplicates) == 0:
    print(f"  [OK] (名字+USCC) 可以作为唯一标识")
    print(f"  [OK] 每个(名字+USCC)组合都是唯一的")
    print(f"  [OK] 适合作为数据库的逻辑主键")
elif len(duplicates) < 10:
    print(f"  [WARN] (名字+USCC) 基本唯一")
    print(f"  [WARN] 只有{len(duplicates)}个重复，可能是数据录入错误")
    print(f"  [WARN] 修正后可作为唯一标识")
else:
    print(f"  [ERROR] (名字+USCC) 不适合作为唯一标识")
    print(f"  [ERROR] 有{len(duplicates)}个重复组合")

print(f"\n检查完成！")
