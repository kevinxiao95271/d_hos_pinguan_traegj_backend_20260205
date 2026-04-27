# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
f = next(ROOT.glob("项目数据（含机构ID+手法+主题0410*.csv"))
df = pd.read_csv(f, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]
print(f"总行数: {len(df)}")
print()

pid_col   = "registration_id"
name_col  = "project_name"
inst_col  = "institution_name"
inst_id   = "institution_id"

# ── 1. 项目名 + 机构名 重复 ──────────────────────────────────────────────────
dup1 = df[df.duplicated(subset=[name_col, inst_col], keep=False)].sort_values([name_col, inst_col])
print(f"── 项目名 + 机构 完全重复: {len(dup1)} 行")
if not dup1.empty:
    print(dup1[[pid_col, name_col, inst_col]].to_string(index=False))
print()

# ── 2. 仅项目名重复（跨机构）────────────────────────────────────────────────
dup2 = df[df.duplicated(subset=[name_col], keep=False)].sort_values(name_col)
# 排除与 dup1 完全相同的（即同名同机构）
dup2_cross = dup2[~dup2.duplicated(subset=[name_col, inst_col], keep=False) |
                   ~dup2[[name_col, inst_col]].apply(tuple, axis=1).isin(
                       dup1[[name_col, inst_col]].apply(tuple, axis=1)
                   )]
# 重新取：只要 project_name 重复但机构不同
dup2_all = df[df.duplicated(subset=[name_col], keep=False)].sort_values(name_col)
print(f"── 项目名相同（含跨机构）: {len(dup2_all)} 行")
if not dup2_all.empty:
    print(dup2_all[[pid_col, name_col, inst_col]].to_string(index=False))
print()

# ── 3. 同机构提交多个同名项目汇总 ───────────────────────────────────────────
grp = df.groupby([name_col, inst_col]).size().reset_index(name="count")
grp = grp[grp["count"] > 1].sort_values("count", ascending=False)
print(f"── 同机构同名项目组数: {len(grp)}")
if not grp.empty:
    print(grp.to_string(index=False))
