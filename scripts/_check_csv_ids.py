# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
f = next(ROOT.glob("项目数据（含机构ID+手法+主题0410*.csv"))
df = pd.read_csv(f, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

ids = [20260136, 20260548, 20260809, 20260824, 20260822, 20260826,
       20260922, 20260923, 20260176, 20260245]

rows = df[df["registration_id"].isin(ids)].sort_values(["institution_name","registration_id"])
print(f"CSV 中找到 {len(rows)} 条（共查 {len(ids)} 个编号）")
print()
for _, r in rows.iterrows():
    print(f"[{r['registration_id']}]  {r['institution_name']}")
    print(f"  {r['project_name']}")
    print()

missing = set(ids) - set(df["registration_id"].tolist())
if missing:
    print(f"以下编号在 CSV 中不存在: {sorted(missing)}")
