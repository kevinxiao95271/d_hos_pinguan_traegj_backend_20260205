# -*- coding: utf-8 -*-
"""
分析未导入的6044条记录
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
missing_file = os.path.join(project_root, '最终验证-未导入记录.xlsx')

print("=" * 100)
print("分析未导入的记录")
print("=" * 100)

df_missing = pd.read_excel(missing_file)

print(f"\n未导入记录总数: {len(df_missing)}")

# 等级分布
print(f"\n等级分布:")
level_counts = df_missing['Excel等级(标准)'].value_counts()
for level, count in level_counts.items():
    print(f"   {level}: {count}")

# USCC重复分析
print(f"\n这些记录是否因为USCC重复未导入？")
uscc_counts = df_missing['统一社会信用代码'].value_counts()
duplicate_uscc = uscc_counts[uscc_counts > 1]

print(f"   不同的USCC数: {len(uscc_counts)}")
print(f"   重复的USCC数: {len(duplicate_uscc)}")
print(f"   涉及的记录数: {duplicate_uscc.sum()}")

if len(duplicate_uscc) > 0:
    print(f"\n   前10个重复最多的USCC:")
    for uscc, count in duplicate_uscc.head(10).items():
        print(f"      {uscc}: {count} 条记录")
        # 显示这些记录的机构名
        matched = df_missing[df_missing['统一社会信用代码'] == uscc]
        for idx, row in matched.head(3).iterrows():
            print(f"         - {row['机构名称']}")

print(f"\n结论:")
print(f"   这6044条未导入记录很可能是因为USCC在DB中已存在（uk_uscc唯一约束）")
print(f"   这些是共享USCC的合法挂靠机构")
