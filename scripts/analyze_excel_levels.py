# -*- coding: utf-8 -*-
"""
分析Excel文件中的等级数据
"""
import os
import pandas as pd

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("分析Excel文件 - 等级数据")
print("=" * 100)

file_path = os.path.join(project_root, excel_file)

try:
    # 读取Excel
    df = pd.read_excel(file_path)
    
    print(f"\n基本信息:")
    print(f"  文件: {excel_file}")
    print(f"  总行数: {len(df)}")
    print(f"  总列数: {len(df.columns)}")
    
    print(f"\n所有列名:")
    for i, col in enumerate(df.columns):
        # 显示前几行数据样本
        sample = df[col].dropna().head(3).tolist()
        sample_str = str(sample)[:50] if sample else "无数据"
        print(f"  [{i+1}] {col:<30} 样本: {sample_str}")
    
    # 查找可能的等级列
    print(f"\n[分析] 查找等级相关的列...")
    
    possible_level_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['等级', 'level', '级别', '机构']):
            possible_level_cols.append(col)
    
    if possible_level_cols:
        print(f"可能的等级列: {possible_level_cols}")
        
        # 分析每个可能的列
        for col in possible_level_cols:
            print(f"\n列 '{col}' 的数据分布:")
            value_counts = df[col].value_counts(dropna=False)
            null_count = df[col].isna().sum()
            
            print(f"  空值(NULL): {null_count} 个")
            
            # 显示前10个最常见的值
            for value, count in value_counts.head(10).items():
                if pd.notna(value):
                    print(f"  {value}: {count} 个")
    else:
        print("未找到明确的等级列")
        print("\n尝试分析每一列的数据特征...")
        
        for col in df.columns:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 50:  # 可能是分类列
                print(f"\n列 '{col}' (唯一值数: {unique_count}):")
                value_counts = df[col].value_counts(dropna=False)
                null_count = df[col].isna().sum()
                
                if null_count > 0:
                    print(f"  空值: {null_count} 个")
                
                for value, count in value_counts.head(5).items():
                    if pd.notna(value):
                        print(f"  {value}: {count} 个")

except Exception as e:
    print(f"出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
