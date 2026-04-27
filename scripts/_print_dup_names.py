# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "项目提交人信息0413.csv", encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

ids = [20260136, 20260548,
       20260822, 20260826,
       20260922, 20260923,
       20260176, 20260245,
       20260809, 20260824]

rows = df[df["registration_id"].isin(ids)].sort_values(["institution_name", "registration_id"])

for _, r in rows.iterrows():
    print(f"[{r['registration_id']}]  {r['institution_name']}  {r['submitter_name']}({r['submitter_phone']})")
    print(f"  {r['project_name']}")
    print()
