# -*- coding: utf-8 -*-
"""读取 4.7 文件全部关键工作表"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

p = next(ROOT.glob("*4.7*(1).xlsx"))
out = open(Path(__file__).with_name("_read_47_full.txt"), "w", encoding="utf-8")

# ── 1. 初步分组情况（全表）
df_grp = pd.read_excel(p, sheet_name="初步分组情况", header=None)
out.write("=== 初步分组情况（全表）===\n")
for i, row in df_grp.iterrows():
    vals = [str(v) if pd.notna(v) else "" for v in row]
    if any(v.strip() for v in vals):
        out.write("  " + " | ".join(vals) + "\n")

# ── 2. 分组数据分析（全表）
df_ana = pd.read_excel(p, sheet_name="分组数据分析", header=None)
out.write("\n=== 分组数据分析（全表）===\n")
for i, row in df_ana.iterrows():
    vals = [str(v) if pd.notna(v) else "" for v in row]
    if any(v.strip() for v in vals):
        out.write("  " + " | ".join(vals) + "\n")

# ── 3. 原始文档列名 + 手法分布
df_raw = pd.read_excel(p, sheet_name="品管报名原始文档0407")
out.write("\n=== 原始文档列名 ===\n")
out.write("  " + str(list(df_raw.columns)) + "\n")
out.write(f"  数据行数（含表头后）: {len(df_raw)}\n")

out.write("\n=== 各竞赛组别运用手法分布 ===\n")
for comp in ["基层组", "综合组", "进阶组"]:
    sub = df_raw[df_raw["竞赛组别"] == comp]
    mc = sub["运用手法"].value_counts()
    out.write(f"\n  【{comp}】共 {len(sub)} 条\n")
    for m, n in mc.items():
        out.write(f"    {m}: {n}\n")

out.close()
print("done")
