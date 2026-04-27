# -*- coding: utf-8 -*-
import sys, re, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]
for phone in ["13588426741", "13567534846"]:
    r = df[df["phone"].astype(str).str.replace(r"\D","",regex=True) == phone]
    if not r.empty:
        row = r.iloc[0]
        print(dict(row))
    else:
        print(f"{phone}  NOT FOUND")
