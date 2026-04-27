# -*- coding: utf-8 -*-
"""探查 4.7 原始文档各字段含义"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

p = next(ROOT.glob("*4.7*(1).xlsx"))
df = pd.read_excel(p, sheet_name="品管报名原始文档0407")
out = open(Path(__file__).with_name("_probe_47.txt"), "w", encoding="utf-8")

# 1. 所有列及 Unnamed 列的唯一值
out.write("=== 所有列名 ===\n")
for i, c in enumerate(df.columns):
    out.write(f"  [{i}] {c}\n")

out.write("\n=== Unnamed:17 唯一值（前20）===\n")
vals = df["Unnamed: 17"].value_counts().head(20)
out.write(vals.to_string() + "\n")

out.write("\n=== 医疗质量改进十大安全目标 唯一值（前20）===\n")
vals2 = df["医疗质量改进十大安全目标"].value_counts().head(20)
out.write(vals2.to_string() + "\n")

out.write("\n=== Unnamed:19 唯一值（前5）===\n")
if "Unnamed: 19" in df.columns:
    vals3 = df["Unnamed: 19"].value_counts().head(5)
    out.write(vals3.to_string() + "\n")

# 2. 十大安全目标：到底哪列是判断依据
# 按 grouping_v4 比对：取项目编号交叉比对
gv4 = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
# 看 grouping_v4 里十大安全目标列
out.write("\n=== grouping_v4 十大安全目标列唯一值 ===\n")
tcol = "十大安全目标"
if tcol in gv4.columns:
    out.write(gv4[tcol].value_counts().to_string() + "\n")

# 3. 交叉比对几条有十大安全目标的项目
sample_ten = gv4[gv4[tcol] != "其他"].head(5)["项目编号"].tolist()
out.write("\n=== 在 4.7 中这些十大安全目标项目的 Unnamed:17 是什么 ===\n")
for pid in sample_ten:
    row = df[df["项目编号"].astype(str) == str(pid)]
    if len(row):
        r = row.iloc[0]
        out.write(f"  {pid}  Unnamed:17=[{r['Unnamed: 17']}]  十大列=[{r['医疗质量改进十大安全目标']}]\n")

# 4. 基层组 综合组 十大安全目标 项目数（按 Unnamed:17 判断）
out.write("\n=== 按 Unnamed:17 != '其他' 判断十大安全目标 ===\n")
for comp in ["基层组", "综合组", "进阶组"]:
    sub = df[df["竞赛组别"] == comp]
    n_ten = (sub["Unnamed: 17"].fillna("其他") != "其他").sum()
    out.write(f"  {comp}: 十大安全目标={n_ten}  总={len(sub)}\n")

out.close()
print("done")
