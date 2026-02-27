# -*- coding: utf-8 -*-
"""
对比Excel和DB中USCC为空的记录是否是同一批
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("对比Excel和DB中USCC为空的记录")
print("=" * 100)

# 读取Excel中USCC为空的记录
file_path = os.path.join(project_root, excel_file)
df_excel = pd.read_excel(file_path)

col_name = 0
col_uscc = 6
col_level = 4

uscc_empty_mask = df_excel.iloc[:, col_uscc].isna() | \
                  (df_excel.iloc[:, col_uscc].astype(str).str.strip() == '') | \
                  (df_excel.iloc[:, col_uscc].astype(str).str.strip() == 'nan')

df_excel_empty_uscc = df_excel[uscc_empty_mask].copy()
excel_empty_names = set(df_excel_empty_uscc.iloc[:, col_name].astype(str).str.strip())

print(f"\n[Excel中USCC为空的记录]")
print(f"   数量: {len(df_excel_empty_uscc)}")
print(f"   机构名称:")
for name in sorted(excel_empty_names):
    print(f"      - {name}")

# 读取DB中USCC为空的记录
db_empty_file = os.path.join(project_root, 'DB独有的11个组合.csv')
df_db_empty = pd.read_csv(db_empty_file, encoding='utf-8-sig')

db_empty_names = set(df_db_empty['机构名称'].astype(str).str.strip())

print(f"\n[DB中USCC为空的记录]")
print(f"   数量: {len(df_db_empty)}")
print(f"   机构名称:")
for name in sorted(db_empty_names):
    print(f"      - {name}")

# 对比
print(f"\n" + "=" * 100)
print("对比结果")
print("=" * 100)

common_names = excel_empty_names & db_empty_names
excel_only_names = excel_empty_names - db_empty_names
db_only_names = db_empty_names - excel_empty_names

print(f"\n[名称对比]")
print(f"   Excel和DB都有: {len(common_names)} 个")
print(f"   Excel独有: {len(excel_only_names)} 个")
print(f"   DB独有: {len(db_only_names)} 个")

if len(common_names) == len(excel_empty_names) == len(db_empty_names):
    print(f"\n   [PERFECT] 完全一致！Excel和DB中USCC为空的记录完全相同！")
else:
    if len(excel_only_names) > 0:
        print(f"\n   Excel独有的机构名:")
        for name in excel_only_names:
            print(f"      - {name}")
    
    if len(db_only_names) > 0:
        print(f"\n   DB独有的机构名:")
        for name in db_only_names:
            print(f"      - {name}")

print(f"\n[结论]")
if len(excel_empty_names) == len(db_empty_names) and len(common_names) == len(excel_empty_names):
    print(f"   Excel中那11条USCC为空的记录，已经全部导入DB了！")
    print(f"   DB比Excel多的11个组合，就是这11条USCC为空的记录！")
    print(f"   它们在之前某个导入批次中被导入了。")
else:
    print(f"   Excel和DB中USCC为空的记录不完全相同。")

print(f"\n检查完成！")
