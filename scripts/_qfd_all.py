# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

d = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
qfd = d[d["运用手法"] == "QFD"]

out = open(Path(__file__).with_name("_qfd_all.txt"), "w", encoding="utf-8")
out.write(f"全部 QFD 项目共 {len(qfd)} 条\n\n")
for _, r in qfd.iterrows():
    out.write(f"  {r['项目编号']}  {r['竞赛组别']}  {r['建议分组']}  {r['机构名称']}  {r['城市']}\n")

out.write("\n各竞赛组别 QFD 数量:\n")
for comp in ["基层组", "综合组", "进阶组"]:
    n = (qfd["竞赛组别"] == comp).sum()
    out.write(f"  {comp}: {n}\n")
out.close()
print("done")
