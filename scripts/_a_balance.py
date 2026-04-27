# -*- coding: utf-8 -*-
"""分析基层组各分组的分布及可均衡性"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

d = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
jc = d[d["竞赛组别"] == "基层组"].copy()

out = open(Path(__file__).with_name("_a_balance.txt"), "w", encoding="utf-8")

out.write("=== 基层组各组项目数 ===\n")
cnt = jc["建议分组"].value_counts().sort_index()
total = cnt.sum()
ideal = total / len(cnt)
for g, n in cnt.items():
    diff = n - ideal
    out.write(f"  {g}: {n:3d}  (偏差 {diff:+.1f})\n")
out.write(f"  合计: {total}  均值: {ideal:.1f}\n\n")

out.write("=== A7 全部项目（17条）===\n")
a7 = jc[jc["建议分组"] == "A7"]
for _, r in a7.iterrows():
    out.write(f"  {r['项目编号']}  {r['机构名称']}  {r['城市']}  {r['运用手法']}  {r['主题类型']}\n")

out.write("\n=== A6 全部项目（21条）===\n")
a6 = jc[jc["建议分组"] == "A6"]
for _, r in a6.iterrows():
    out.write(f"  {r['项目编号']}  {r['机构名称']}  {r['城市']}  {r['运用手法']}  {r['主题类型']}\n")

out.write("\n=== A4 全部项目（24条）===\n")
a4 = jc[jc["建议分组"] == "A4"]
for _, r in a4.iterrows():
    out.write(f"  {r['项目编号']}  {r['机构名称']}  {r['城市']}  {r['运用手法']}  {r['主题类型']}\n")

# 分析分组依据：看看是按城市还是手法还是顺序编排的
out.write("\n=== 各分组城市分布 ===\n")
for g in sorted(jc["建议分组"].unique()):
    sub = jc[jc["建议分组"] == g]
    cities = sub["城市"].value_counts().to_dict()
    out.write(f"  {g}({len(sub)}): {cities}\n")

out.write("\n=== 各分组手法分布 ===\n")
for g in sorted(jc["建议分组"].unique()):
    sub = jc[jc["建议分组"] == g]
    methods = sub["运用手法"].value_counts().to_dict()
    out.write(f"  {g}({len(sub)}): {dict(list(methods.items())[:4])}\n")

out.write("\n=== 各分组机构等级分布 ===\n")
for g in sorted(jc["建议分组"].unique()):
    sub = jc[jc["建议分组"] == g]
    lvl = sub["机构等级"].value_counts().to_dict()
    out.write(f"  {g}({len(sub)}): {lvl}\n")

out.close()
print("done")
