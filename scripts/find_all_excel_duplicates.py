# -*- coding: utf-8 -*-
"""
找出Excel中所有的(名字+USCC)重复记录
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("查找Excel中所有重复记录")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_region = 1
col_level = 4
col_uscc = 6

df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

print(f"\nExcel总记录数: {len(df_excel)}")

# 统计重复
key_counts = df_excel['组合键'].value_counts()
print(f"不同的(名字+USCC)组合: {len(key_counts)}")
print(f"计算: 总记录 - 不同组合 = {len(df_excel)} - {len(key_counts)} = {len(df_excel) - len(key_counts)} 条重复记录")

# 找出所有重复的组合
duplicates = key_counts[key_counts > 1]

print(f"\n重复统计:")
print(f"   重复的组合数: {len(duplicates)}")
print(f"   涉及的总记录数: {duplicates.sum()}")
print(f"   重复的记录数: {duplicates.sum() - len(duplicates)}")

if len(duplicates) > 0:
    print(f"\n" + "=" * 100)
    print("所有重复记录详细清单")
    print("=" * 100)
    
    for i, (combo, count) in enumerate(duplicates.items(), 1):
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            
            # 找到所有匹配的记录
            mask = (df_excel['名字'] == name) & (df_excel['USCC'] == uscc)
            matched = df_excel[mask]
            
            print(f"\n{i}. 机构名称: {name}")
            print(f"   USCC: {uscc}")
            print(f"   在Excel中出现{count}次:")
            
            for seq, (idx, row) in enumerate(matched.iterrows(), 1):
                region = row.iloc[col_region] if pd.notna(row.iloc[col_region]) else '[空]'
                level = row.iloc[col_level]
                level_display = level if pd.notna(level) and str(level).strip() != '' else '[空值]'
                
                print(f"      记录{seq} (Excel行号{idx+2}):")
                print(f"         地区: {region}")
                print(f"         等级: {level_display}")
    
    # 导出
    duplicate_records = df_excel[df_excel['组合键'].isin(duplicates.index)].copy()
    duplicate_records = duplicate_records.sort_values('组合键')
    
    output_file = os.path.join(project_root, 'Excel中所有重复记录.xlsx')
    output_data = duplicate_records.iloc[:, [col_name, col_region, col_level, col_uscc]]
    output_data.columns = ['机构名称', '地区', '等级', '统一社会信用代码']
    output_data.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"\n已导出所有重复记录到: {output_file}")

print(f"\n检查完成！")
