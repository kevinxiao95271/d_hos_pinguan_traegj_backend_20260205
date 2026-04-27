# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

d = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
jc = d[d["竞赛组别"] == "基层组"].copy()

out = open(Path(__file__).with_name("_check_cols.txt"), "w", encoding="utf-8")
out.write("列名: " + ", ".join(jc.columns.tolist()) + "\n\n")

# 各组详细情况 —— 有无手法/主题等分类字段
for col in jc.columns:
    if col in ("建议分组", "竞赛组别", "机构名称", "项目编号"):
        continue
    vals = jc[col].dropna().unique()
    if len(vals) <= 20:
        out.write(f"{col}: {sorted(str(v) for v in vals)}\n")

out.write("\n=== 各组项目数 ===\n")
cnt = jc["建议分组"].value_counts().sort_index()
for g, n in cnt.items():
    out.write(f"  {g}: {n}\n")
out.write(f"  均值: {cnt.mean():.1f}  最大: {cnt.max()}  最小: {cnt.min()}\n")
out.close()
print("done")
