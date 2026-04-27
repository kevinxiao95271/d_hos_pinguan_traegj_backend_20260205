# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
df.columns = [c.strip() for c in df.columns]

summary = df.groupby("建议分组").size().reset_index(name="项目数")

# 按竞赛组别汇总
comp_map = df.set_index("项目编号")["竞赛组别"].to_dict()
df["竞赛组别2"] = df["竞赛组别"]

print(f"{'分组':<6} {'项目数':>6}  竞赛类型")
print("-" * 30)
total = 0
for _, r in summary.iterrows():
    gc = r["建议分组"]
    cnt = r["项目数"]
    total += cnt
    ct = df[df["建议分组"]==gc]["竞赛组别"].iloc[0]
    print(f"{gc:<6} {cnt:>6}  {ct}")

print("-" * 30)
print(f"{'合计':<6} {total:>6}")
print()

# 与 grouping_final 汇总 sheet 对比
try:
    sumdf = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组汇总")
    sumdf.columns = [c.strip() for c in sumdf.columns]
    print("分组汇总 sheet 内容：")
    print(sumdf.to_string(index=False))
except:
    pass
