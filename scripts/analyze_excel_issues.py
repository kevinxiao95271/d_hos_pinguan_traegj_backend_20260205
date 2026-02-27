# -*- coding: utf-8 -*-
"""
分析Excel数据质量问题：
1. Excel中存在2次的重复记录
2. Excel中USCC为空值的记录
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("Excel数据质量分析")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_type = 2
col_nature = 3
col_level = 4
col_business = 5
col_uscc = 6

print(f"\nExcel总记录数: {len(df_excel)}")

# ===========================================
# 问题1：Excel中(名字+USCC)重复的记录
# ===========================================
print(f"\n" + "=" * 100)
print("问题1：Excel中(名字+USCC)重复的记录")
print("=" * 100)

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

# 统计组合键的重复情况
key_counts = df_excel['组合键'].value_counts()
duplicates = key_counts[key_counts > 1]

print(f"\n[统计]")
print(f"   不同的(名字+USCC)组合: {len(key_counts)}")
print(f"   重复的组合数: {len(duplicates)}")
print(f"   涉及的记录数: {duplicates.sum()}")

if len(duplicates) > 0:
    print(f"\n[详细清单]")
    
    for i, (combo, count) in enumerate(duplicates.items(), 1):
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            
            # 找到所有匹配的记录
            mask = (df_excel['名字'] == name) & (df_excel['USCC'] == uscc)
            matched = df_excel[mask]
            
            print(f"\n{i}. 机构名称: {name}")
            print(f"   USCC: {uscc}")
            print(f"   重复次数: {count}")
            
            for seq, (idx, row) in enumerate(matched.iterrows(), 1):
                region = row.iloc[col_region] if pd.notna(row.iloc[col_region]) else '[空]'
                level = row.iloc[col_level] if pd.notna(row.iloc[col_level]) and str(row.iloc[col_level]).strip() != '' else '[空值]'
                type_ = row.iloc[col_type] if pd.notna(row.iloc[col_type]) else '[空]'
                
                print(f"      记录{seq} (行号{idx+2}):")
                print(f"         地区: {region}")
                print(f"         等级: {level}")
                print(f"         类别: {type_}")
    
    # 导出重复记录
    duplicate_records = df_excel[df_excel['组合键'].isin(duplicates.index)].copy()
    
    output_file = os.path.join(project_root, 'Excel中完全重复的记录.xlsx')
    output_data = duplicate_records.iloc[:, [col_name, col_region, col_type, col_level, col_uscc]]
    output_data.columns = ['机构名称', '地区', '机构类别', '等级', '统一社会信用代码']
    output_data = output_data.sort_values(['机构名称', '统一社会信用代码'])
    output_data.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n   已导出到: {output_file}")

# ===========================================
# 问题2：Excel中USCC为空值的记录
# ===========================================
print(f"\n" + "=" * 100)
print("问题2：Excel中USCC为空值的记录")
print("=" * 100)

# 检查USCC为空的记录
uscc_empty_mask = df_excel.iloc[:, col_uscc].isna() | (df_excel.iloc[:, col_uscc].astype(str).str.strip() == '') | (df_excel.iloc[:, col_uscc].astype(str).str.strip() == 'nan')
df_empty_uscc = df_excel[uscc_empty_mask].copy()

print(f"\n[统计]")
print(f"   USCC为空的记录数: {len(df_empty_uscc)}")
print(f"   占比: {len(df_empty_uscc)/len(df_excel)*100:.2f}%")

if len(df_empty_uscc) > 0:
    # 按等级分类
    print(f"\n[按等级分类]")
    for col_idx in range(len(df_empty_uscc.columns)):
        if col_idx == col_level:
            level_counts = df_empty_uscc.iloc[:, col_level].apply(
                lambda x: x if pd.notna(x) and str(x).strip() != '' else '[空值]'
            ).value_counts()
            for level, count in level_counts.items():
                print(f"   {level}: {count} 条")
    
    # 按地区分类
    print(f"\n[按地区分类]")
    region_counts = df_empty_uscc.iloc[:, col_region].value_counts().head(10)
    for region, count in region_counts.items():
        print(f"   {region}: {count} 条")
    
    # 按机构类别分类
    print(f"\n[按机构类别分类]")
    type_counts = df_empty_uscc.iloc[:, col_type].value_counts().head(10)
    for type_, count in type_counts.items():
        print(f"   {type_}: {count} 条")
    
    # 显示详细记录
    print(f"\n[详细清单前30条]")
    print(f"{'序号':<5} {'机构名称':<45} {'等级':<12} {'地区':<12} {'类别':<15}")
    print("-" * 100)
    
    for idx, (i, row) in enumerate(df_empty_uscc.head(30).iterrows(), 1):
        name = row.iloc[col_name][:43] if len(str(row.iloc[col_name])) > 43 else str(row.iloc[col_name])
        level = row.iloc[col_level] if pd.notna(row.iloc[col_level]) and str(row.iloc[col_level]).strip() != '' else '[空值]'
        region = str(row.iloc[col_region])[:10] if pd.notna(row.iloc[col_region]) else '[空]'
        type_ = str(row.iloc[col_type])[:13] if pd.notna(row.iloc[col_type]) else '[空]'
        
        print(f"{idx:<5} {name:<45} {level:<12} {region:<12} {type_:<15}")
    
    if len(df_empty_uscc) > 30:
        print(f"\n... 还有 {len(df_empty_uscc) - 30} 条记录 ...")
    
    # 导出空USCC记录
    output_empty = os.path.join(project_root, 'Excel中USCC为空的记录.xlsx')
    output_empty_data = df_empty_uscc.iloc[:, [col_name, col_region, col_type, col_level, col_business, col_nature]]
    output_empty_data.columns = ['机构名称', '地区', '机构类别', '等级', '经营性质', '机构性质']
    output_empty_data.to_excel(output_empty, index=False, engine='openpyxl')
    print(f"\n   已导出到: {output_empty}")
    
    output_empty_csv = os.path.join(project_root, 'Excel中USCC为空的记录.csv')
    output_empty_data.to_csv(output_empty_csv, index=False, encoding='utf-8-sig')
    print(f"   已导出到: {output_empty_csv}")

# ===========================================
# 汇总报告
# ===========================================
print(f"\n" + "=" * 100)
print("汇总报告")
print("=" * 100)

print(f"\n[Excel数据质量问题]")
print(f"   1. (名字+USCC)重复的记录: {duplicates.sum() if len(duplicates) > 0 else 0} 条")
print(f"      涉及组合数: {len(duplicates)}")
print(f"   2. USCC为空值的记录: {len(df_empty_uscc)} 条")
print(f"      占总记录比例: {len(df_empty_uscc)/len(df_excel)*100:.2f}%")

print(f"\n[影响]")
if len(duplicates) > 0:
    print(f"   - {duplicates.sum()}条重复记录中，只能导入{len(duplicates)}条（每个组合保留第一条）")
if len(df_empty_uscc) > 0:
    print(f"   - {len(df_empty_uscc)}条USCC为空的记录无法作为唯一标识")

print(f"\n检查完成！")
