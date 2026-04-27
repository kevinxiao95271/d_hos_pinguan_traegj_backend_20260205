# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
f = next(ROOT.glob("项目数据（含机构ID+手法+主题0410*.csv"))
df = pd.read_csv(f, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

rows = df[df["registration_id"].isin([20260040, 20260836])]
print(rows.to_string(index=False))
