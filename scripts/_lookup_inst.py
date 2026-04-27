# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]
for kw in ["第九", "妇幼保健", "东阳"]:
    hits = df[df["name"].str.contains(kw, na=False)]
    for _, r in hits.iterrows():
        print(f"id={int(r['id'])}  {r['name']}")
    print()
