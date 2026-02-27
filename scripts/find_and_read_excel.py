# -*- coding: utf-8 -*-
"""
查找并读取Excel文件
"""
import os
import pandas as pd

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"

print("=" * 100)
print("查找Excel文件")
print("=" * 100)

# 1. 列出根目录所有文件
print(f"\n[步骤1] 列出项目根目录所有文件...")
print(f"目录: {project_root}")
print("-" * 100)

try:
    files = os.listdir(project_root)
    
    # 只显示文件，不显示目录
    file_list = []
    xlsx_files = []
    
    for f in files:
        full_path = os.path.join(project_root, f)
        if os.path.isfile(full_path):
            file_list.append(f)
            if f.endswith('.xlsx') or f.endswith('.xls'):
                xlsx_files.append(f)
    
    print(f"找到 {len(file_list)} 个文件")
    
    if xlsx_files:
        print(f"\n找到 {len(xlsx_files)} 个Excel文件:")
        for f in xlsx_files:
            print(f"  - {f}")
    else:
        print("\n未找到Excel文件")
        print("\n显示前20个文件:")
        for f in file_list[:20]:
            print(f"  - {f}")
    
except Exception as e:
    print(f"列出文件出错: {e}")
    import traceback
    traceback.print_exc()

# 2. 如果找到Excel文件，读取第一个
if xlsx_files:
    excel_file = xlsx_files[0]
    print(f"\n[步骤2] 读取Excel文件: {excel_file}")
    print("-" * 100)
    
    try:
        file_path = os.path.join(project_root, excel_file)
        
        # 读取Excel
        df = pd.read_excel(file_path)
        
        print(f"成功读取Excel文件")
        print(f"  总行数: {len(df)}")
        print(f"  总列数: {len(df.columns)}")
        
        print(f"\n列名:")
        for i, col in enumerate(df.columns):
            print(f"  [{i+1}] {col}")
        
        # 查找等级列
        level_col = None
        for col in df.columns:
            if '等级' in str(col) or 'level' in str(col).lower():
                level_col = col
                print(f"\n找到等级列: {col}")
                break
        
        if level_col:
            # 统计等级分布
            print(f"\n[步骤3] 分析等级分布...")
            print("-" * 100)
            
            level_counts = df[level_col].value_counts(dropna=False)
            null_count = df[level_col].isna().sum()
            
            print(f"\n等级分布:")
            print(f"  空值(NULL): {null_count} 个")
            
            for level, count in level_counts.items():
                if pd.notna(level):
                    print(f"  {level}: {count} 个")
            
            print(f"\n总计: {len(df)} 个")
            
    except Exception as e:
        print(f"读取Excel出错: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 100)
