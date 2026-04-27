# -*- coding: utf-8 -*-
"""读取 4.7 口径文件，摸清所有工作表结构"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

p = next(ROOT.glob("*4.7*(1).xlsx"))
xl = pd.ExcelFile(p)

out = open(Path(__file__).with_name("_read_47.txt"), "w", encoding="utf-8")
out.write(f"文件: {p.name}\n")
out.write(f"工作表: {xl.sheet_names}\n\n")

for sh in xl.sheet_names:
    df = pd.read_excel(p, sheet_name=sh, header=None, nrows=5)
    out.write(f"=== 工作表: {sh} ===\n")
    out.write(f"  维度(前5行): {df.shape}\n")
    out.write("  前5行:\n")
    for i, row in df.iterrows():
        vals = [str(v)[:30] for v in row if pd.notna(v)]
        out.write(f"    {vals}\n")
    # 真实行数
    df_full = pd.read_excel(p, sheet_name=sh, header=None)
    out.write(f"  全表行数: {len(df_full)}\n\n")

out.close()
print("done")
