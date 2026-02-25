#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查Excel文件中的医疗机构数据
"""
import pandas as pd
import os

excel_path = r"D:\iWork\iYuo\浙江\品管大赛\工作群文件\2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx"

print("=" * 100)
print("检查Excel文件")
print("=" * 100)

if not os.path.exists(excel_path):
    print(f"错误: 文件不存在 - {excel_path}")
    exit(1)

print(f"\n文件路径: {excel_path}")
print(f"文件大小: {os.path.getsize(excel_path) / 1024:.2f} KB")

# 读取Excel文件
try:
    # 先看看有哪些sheet
    xl_file = pd.ExcelFile(excel_path)
    print(f"\nSheet列表: {xl_file.sheet_names}")
    
    # 读取第一个sheet
    df = pd.read_excel(excel_path, sheet_name=0)
    
    print(f"\n总行数: {len(df)}")
    print(f"总列数: {len(df.columns)}")
    
    print("\n列名:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print("\n数据类型:")
    print(df.dtypes)
    
    print("\n前5行数据:")
    print(df.head())
    
    print("\n数据统计:")
    print(f"  - 空值统计:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            print(f"    {col}: {count} ({count/len(df)*100:.1f}%)")
    
    # 检查重要字段
    print("\n关键字段检查:")
    
    # 检查机构名称
    if '机构名称' in df.columns:
        print(f"\n  机构名称:")
        print(f"    - 总数: {len(df)}")
        print(f"    - 唯一值数量: {df['机构名称'].nunique()}")
        print(f"    - 重复数量: {len(df) - df['机构名称'].nunique()}")
        if df['机构名称'].duplicated().any():
            print(f"    - 重复的机构名称:")
            duplicates = df[df['机构名称'].duplicated(keep=False)].sort_values('机构名称')
            for name, group in duplicates.groupby('机构名称'):
                print(f"      {name}: {len(group)}条")
    
    # 检查社会信用代码
    credit_code_cols = [col for col in df.columns if '信用代码' in col or 'USCC' in col.upper() or '统一社会' in col]
    if credit_code_cols:
        credit_col = credit_code_cols[0]
        print(f"\n  社会信用代码字段: {credit_col}")
        print(f"    - 总数: {len(df)}")
        print(f"    - 非空数量: {df[credit_col].notna().sum()}")
        print(f"    - 唯一值数量: {df[credit_col].nunique()}")
        print(f"    - 重复数量: {df[credit_col].notna().sum() - df[credit_col].nunique()}")
        if df[credit_col].duplicated().any():
            print(f"    - 重复的信用代码:")
            duplicates = df[df[credit_col].duplicated(keep=False)].sort_values(credit_col)
            for code, group in duplicates.groupby(credit_col):
                if pd.notna(code):
                    print(f"      {code}: {len(group)}条")
    
    # 检查机构类别
    category_cols = [col for col in df.columns if '类别' in col or '类型' in col]
    if category_cols:
        category_col = category_cols[0]
        print(f"\n  机构类别字段: {category_col}")
        print(f"    - 唯一类别数: {df[category_col].nunique()}")
        print(f"    - 类别分布:")
        for cat, count in df[category_col].value_counts().items():
            print(f"      {cat}: {count}")
    
    # 检查地区
    region_cols = [col for col in df.columns if '地区' in col or '地市' in col or '市' in col]
    if region_cols:
        region_col = region_cols[0]
        print(f"\n  地区字段: {region_col}")
        print(f"    - 唯一地区数: {df[region_col].nunique()}")
        print(f"    - 地区分布:")
        for region, count in df[region_col].value_counts().items():
            print(f"      {region}: {count}")
    
    # 保存示例数据
    sample_file = "d:/AiCode/cursor/d_hos_pinguan_traegj_backend_20260205/data/institution_sample.csv"
    os.makedirs(os.path.dirname(sample_file), exist_ok=True)
    df.head(20).to_csv(sample_file, index=False, encoding='utf-8-sig')
    print(f"\n示例数据已保存到: {sample_file}")
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
