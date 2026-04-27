# -*- coding: utf-8 -*-
"""
对比 4.7 口径初始分组 vs grouping_v5 最终分组
找出因回避试算交换导致的手法构成偏差
"""
import re
from collections import defaultdict
from pathlib import Path
import pandas as pd, sys
sys.path.insert(0, str(Path(__file__).parent))
import export_grouping_v5 as ev5

ROOT = Path(__file__).resolve().parents[1]

# 1. 重建 4.7 口径初始分组（未经回避试算）
base = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
init = ev5.assign_groups(base)   # 纯 4.7 分组，未跑试算

# 2. 最终 v5
final = pd.read_excel(ROOT / "grouping_v5.xlsx", sheet_name="分组明细")

# 3. 找出被回避试算交换的行
mask = init["建议分组"].astype(str) != final["建议分组"].astype(str)
swapped = init[mask][["项目编号","竞赛组别","机构名称","运用手法"]].copy()
swapped["初始分组"] = init.loc[mask,"建议分组"].values
swapped["最终分组"] = final.loc[mask,"建议分组"].values

out = open(Path(__file__).with_name("_v5_composition.txt"),"w",encoding="utf-8")
out.write(f"回避试算共交换 {len(swapped)} 行\n\n")
out.write(swapped.to_string(index=False) + "\n\n")

# 4. 逐组统计手法构成偏差
out.write("=== 各组手法构成偏差（仅列出有偏差的组）===\n")
expected_method = {
    "A1":"十大安全目标混合","A2":"品管圈-问题解决","A3":"品管圈-问题解决",
    "A4":"品管圈-课题达成+品管圈-问题解决","A5":"PDCA","A6":"PDCA+FOCUS-PDCA","A7":"综合工具组",
    "B1":"品管圈-问题解决(十大)","B2":"十大安全目标混合","B3":"PDCA+FOCUS-PDCA(十大)",
    "B4":"品管圈-问题解决","B5":"品管圈-问题解决","B6":"品管圈-问题解决",
    "B7":"品管圈-问题解决","B8":"品管圈-问题解决","B9":"品管圈-问题解决",
    "B10":"品管圈-课题达成","B11":"品管圈-课题达成","B12":"品管圈-课题达成","B13":"品管圈-课题达成",
    "B14":"QFD","B15":"PDCA","B16":"PDCA","B17":"PDCA",
    "B18":"FOCUS-PDCA","B19":"FOCUS-PDCA","B20":"失效模式与效应分析",
    "B21":"根本原因分析+其他","B22":"综合工具组",
    "C1":"品管圈-课题达成","C2":"品管圈-课题达成+QFD","C3":"品管圈-问题解决+FOCUS-PDCA","C4":"综合工具组",
}
for grp in sorted(final["建议分组"].unique()):
    init_mc = init[init["建议分组"]==grp]["运用手法"].value_counts().to_dict()
    fin_mc  = final[final["建议分组"]==grp]["运用手法"].value_counts().to_dict()
    if init_mc != fin_mc:
        out.write(f"\n  {grp}（预期：{expected_method.get(grp,'')}）\n")
        all_m = set(init_mc)|set(fin_mc)
        for m in sorted(all_m):
            i_n = init_mc.get(m,0); f_n = fin_mc.get(m,0)
            if i_n != f_n:
                out.write(f"    {m}: 初始={i_n} → 最终={f_n}  {'↑' if f_n>i_n else '↓'}{abs(f_n-i_n)}\n")

out.close()
print("done")
