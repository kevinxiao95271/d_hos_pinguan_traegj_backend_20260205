# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
d = pd.read_excel(ROOT / "grouping_v5.xlsx", sheet_name="分组明细")
b14 = d[d["建议分组"] == "B14"]
out = open(Path(__file__).with_name("_b14_check.txt"), "w", encoding="utf-8")
out.write(f"B14 共 {len(b14)} 条\n")
out.write(b14["运用手法"].value_counts().to_string() + "\n\n")
non_qfd = b14[b14["运用手法"] != "QFD"]
out.write(f"非 QFD: {len(non_qfd)} 条\n")
for _, r in non_qfd.iterrows():
    out.write(f"  {r['项目编号']}  {r['机构名称']}  {r['运用手法']}\n")
# 找原来是 QFD 但不在 B14 的
qfd_all = d[(d["竞赛组别"] == "综合组") & (d["运用手法"] == "QFD")]
not_b14 = qfd_all[qfd_all["建议分组"] != "B14"]
out.write(f"\n综合组 QFD 不在 B14: {len(not_b14)} 条\n")
for _, r in not_b14.iterrows():
    out.write(f"  {r['项目编号']}  {r['机构名称']}  {r['建议分组']}\n")
out.close()
print("done")
