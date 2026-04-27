# -*- coding: utf-8 -*-
"""找出 A7 与预期 21 条的差距"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

d = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
jc = d[d["竞赛组别"] == "基层组"].copy()

out = open(Path(__file__).with_name("_a7_diff.txt"), "w", encoding="utf-8")

# 用户期望 A7 包含的手法
expected_methods = {"根本原因分析", "六西格玛管理", "失效模式与效应分析", "QFD", "流程改造"}
# 以及包含"其他"关键字的

def is_综合工具(m):
    if pd.isna(m): return False
    m = str(m)
    if m in expected_methods: return True
    if m.startswith("其他") and m not in {"其他：精益A3", "其他：Donabedian理论"}: return False
    if m.startswith("其他"): return True
    return False

# 当前 A7 实际手法
out.write("=== 当前 A7（17条）手法明细 ===\n")
a7 = jc[jc["建议分组"] == "A7"]
m7 = a7["运用手法"].value_counts()
for m, n in m7.items():
    out.write(f"  {m}: {n}\n")
out.write(f"  小计: {len(a7)}\n\n")

# 基层组里「综合工具类」手法分布在哪些组
target_methods = ["根本原因分析", "六西格玛管理", "失效模式与效应分析", "QFD", "流程改造"]
out.write("=== 基层组中「综合工具类手法」分布（含QFD在哪里）===\n")
for method in target_methods:
    sub = jc[jc["运用手法"] == method]
    if len(sub) == 0:
        out.write(f"  {method}: 0条\n")
        continue
    by_grp = sub["建议分组"].value_counts().to_dict()
    out.write(f"  {method}（共{len(sub)}条）: {by_grp}\n")
    if by_grp.get("A7", 0) < len(sub):
        # 不在 A7 的行
        elsewhere = sub[sub["建议分组"] != "A7"]
        for _, r in elsewhere.iterrows():
            out.write(f"    → 不在A7: {r['项目编号']}  {r['机构名称']}  {r['建议分组']}\n")

# 其他类
out.write("\n  其他：* 系列:\n")
others = jc[jc["运用手法"].astype(str).str.startswith("其他")]
by_grp = others.groupby(["运用手法", "建议分组"]).size()
out.write(by_grp.to_string() + "\n")

# 预期 vs 实际
out.write("\n=== 差距汇总 ===\n")
all_综合 = jc[jc["运用手法"].isin(target_methods) | jc["运用手法"].astype(str).str.startswith("其他")]
out.write(f"基层组中所有「综合工具类」项目总数: {len(all_综合)}\n")
in_a7 = all_综合[all_综合["建议分组"] == "A7"]
not_a7 = all_综合[all_综合["建议分组"] != "A7"]
out.write(f"  已在 A7: {len(in_a7)}\n")
out.write(f"  不在 A7: {len(not_a7)}\n")
if len(not_a7):
    for _, r in not_a7.iterrows():
        out.write(f"    {r['项目编号']}  {r['机构名称']}  {r['运用手法']}  当前分组={r['建议分组']}\n")
out.close()
print("done")
