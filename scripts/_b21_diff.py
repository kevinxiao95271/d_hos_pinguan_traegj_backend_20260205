# -*- coding: utf-8 -*-
"""分析综合组 B21/B22 与预期的差距"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

d = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
zh = d[d["竞赛组别"] == "综合组"].copy()

out = open(Path(__file__).with_name("_b21_diff.txt"), "w", encoding="utf-8")

# 当前综合组各分组项目数 + 手法构成
out.write("=== 综合组各分组项目数 & 手法构成 ===\n")
for g in sorted(zh["建议分组"].unique()):
    sub = zh[zh["建议分组"] == g]
    methods = sub["运用手法"].value_counts().to_dict()
    out.write(f"  {g}({len(sub)}): {methods}\n")

# B21 实际
out.write("\n=== B21 实际（当前）===\n")
b21 = zh[zh["建议分组"] == "B21"]
out.write(f"  共 {len(b21)} 条\n")
mc = b21["运用手法"].value_counts()
for m, n in mc.items():
    out.write(f"  {m}: {n}\n")

# B22 实际
out.write("\n=== B22 实际（当前）===\n")
b22 = zh[zh["建议分组"] == "B22"]
out.write(f"  共 {len(b22)} 条\n")
mc2 = b22["运用手法"].value_counts()
for m, n in mc2.items():
    out.write(f"  {m}: {n}\n")

# 预期 B21 手法：根本原因分析 + 其他（排除 B22 专属手法）
b21_expected_methods = ["根本原因分析"]
b22_expected_methods = ["专案改善", "六西格玛管理", "流程改造", "5S", "平衡计分卡"]
other_prefix = "其他"

out.write("\n=== 综合组中「根本原因分析」分布在哪里 ===\n")
rca = zh[zh["运用手法"] == "根本原因分析"]
by_grp = rca["建议分组"].value_counts().to_dict()
out.write(f"  合计 {len(rca)} 条: {by_grp}\n")
not_b21 = rca[rca["建议分组"] != "B21"]
for _, r in not_b21.iterrows():
    out.write(f"    不在B21: {r['项目编号']}  {r['机构名称']}  {r['建议分组']}\n")

out.write("\n=== 综合组中「B22 专属手法」分布 ===\n")
for method in b22_expected_methods:
    sub = zh[zh["运用手法"] == method]
    if len(sub) == 0:
        out.write(f"  {method}: 0条\n")
        continue
    by_grp2 = sub["建议分组"].value_counts().to_dict()
    out.write(f"  {method}（{len(sub)}条）: {by_grp2}\n")
    not_b22 = sub[sub["建议分组"] != "B22"]
    for _, r in not_b22.iterrows():
        out.write(f"    不在B22: {r['项目编号']}  {r['机构名称']}  {r['运用手法']}  {r['建议分组']}\n")

out.write("\n=== 综合组「其他：*」系列分布 ===\n")
others = zh[zh["运用手法"].astype(str).str.startswith("其他")]
by_method_grp = others.groupby(["运用手法", "建议分组"]).size().reset_index(name="n")
for _, r in by_method_grp.iterrows():
    out.write(f"  {r['运用手法']} -> {r['建议分组']}: {r['n']}\n")

out.write("\n=== 差距汇总 ===\n")
# 按预期 B21 应包含：根本原因分析 全部 + 其他（非B22专属的）
b22_set = set(b22_expected_methods)
def should_be_b21(m):
    m = str(m)
    if m == "根本原因分析": return True
    if m.startswith("其他") and m not in b22_set: return True
    return False

expected_b21 = zh[zh["运用手法"].apply(should_be_b21)]
in_b21 = expected_b21[expected_b21["建议分组"] == "B21"]
not_in_b21 = expected_b21[expected_b21["建议分组"] != "B21"]
out.write(f"  理论上属于B21的项目总数: {len(expected_b21)}\n")
out.write(f"  已在B21: {len(in_b21)}\n")
out.write(f"  不在B21: {len(not_in_b21)}\n")
if len(not_in_b21):
    for _, r in not_in_b21.iterrows():
        out.write(f"    {r['项目编号']}  {r['机构名称']}  {r['运用手法']}  当前={r['建议分组']}\n")

# 同样对B22
out.write("\n")
def should_be_b22(m):
    m = str(m)
    return m in b22_set

expected_b22 = zh[zh["运用手法"].apply(should_be_b22)]
in_b22 = expected_b22[expected_b22["建议分组"] == "B22"]
not_in_b22 = expected_b22[expected_b22["建议分组"] != "B22"]
out.write(f"  理论上属于B22的项目总数: {len(expected_b22)}\n")
out.write(f"  已在B22: {len(in_b22)}\n")
out.write(f"  不在B22: {len(not_in_b22)}\n")
if len(not_in_b22):
    for _, r in not_in_b22.iterrows():
        out.write(f"    {r['项目编号']}  {r['机构名称']}  {r['运用手法']}  当前={r['建议分组']}\n")

out.close()
print("done")
