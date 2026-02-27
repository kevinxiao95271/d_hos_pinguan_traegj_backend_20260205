# -*- coding: utf-8 -*-
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

print(f"Total columns: {len(df.columns)}")
print(f"Total rows: {len(df)}")
print("\nColumn names:")
for i, col in enumerate(df.columns):
    print(f"[{i}] {col}")
