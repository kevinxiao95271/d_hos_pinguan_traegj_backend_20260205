# -*- coding: utf-8 -*-
"""
找出Excel中(名字+USCC)重复的记录
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("查找Excel中(名字+USCC)重复的记录")
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

# 创建(名字+USCC)组合键
df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
df_excel['组合键'] = df_excel['名字'] + '|||' + df_excel['USCC']

# 统计组合键的重复情况
key_counts = df_excel['组合键'].value_counts()
duplicates = key_counts[key_counts > 1]

print(f"\n重复统计:")
print(f"   不同的(名字+USCC)组合数: {len(key_counts)}")
print(f"   重复的组合数: {len(duplicates)}")
print(f"   涉及的记录数: {duplicates.sum()}")

if len(duplicates) > 0:
    print(f"\n" + "=" * 100)
    print("重复记录详细清单")
    print("=" * 100)
    
    # 按重复次数排序
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
            print(f"   详细信息:")
            
            for idx, row in matched.iterrows():
                region = row.iloc[col_region] if pd.notna(row.iloc[col_region]) else '[空]'
                level_raw = row.iloc[col_level]
                level_display = level_raw if pd.notna(level_raw) and str(level_raw).strip() != '' else '[空值]'
                type_ = row.iloc[col_type] if pd.notna(row.iloc[col_type]) else '[空]'
                nature = row.iloc[col_nature] if pd.notna(row.iloc[col_nature]) else '[空]'
                business = row.iloc[col_business] if pd.notna(row.iloc[col_business]) else '[空]'
                
                print(f"      记录{idx+1}:")
                print(f"         地区: {region}")
                print(f"         等级: {level_display}")
                print(f"         机构类别: {type_}")
                print(f"         机构性质: {nature}")
                print(f"         经营性质: {business}")
    
    # 导出重复记录
    duplicate_records = df_excel[df_excel['组合键'].isin(duplicates.index)].copy()
    
    # 准备导出数据
    output_data = []
    for combo in duplicates.index:
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            mask = (df_excel['名字'] == name) & (df_excel['USCC'] == uscc)
            matched = df_excel[mask]
            
            for idx, row in matched.iterrows():
                output_data.append({
                    '机构名称': name,
                    '统一社会信用代码': uscc,
                    '地区': row.iloc[col_region] if pd.notna(row.iloc[col_region]) else '',
                    '机构类别': row.iloc[col_type] if pd.notna(row.iloc[col_type]) else '',
                    '机构性质': row.iloc[col_nature] if pd.notna(row.iloc[col_nature]) else '',
                    '等级': row.iloc[col_level] if pd.notna(row.iloc[col_level]) else '[空值]',
                    '经营性质': row.iloc[col_business] if pd.notna(row.iloc[col_business]) else '',
                    '重复次数': duplicates[combo]
                })
    
    df_output = pd.DataFrame(output_data)
    
    output_file = os.path.join(project_root, 'Excel中重复的(名字+USCC)记录.xlsx')
    df_output.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n已导出重复记录到: {output_file}")
    
    output_csv = os.path.join(project_root, 'Excel中重复的(名字+USCC)记录.csv')
    df_output.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"已导出重复记录到: {output_csv}")

print(f"\n检查完成！")
