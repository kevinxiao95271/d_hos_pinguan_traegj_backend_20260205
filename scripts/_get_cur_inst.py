# -*- coding: utf-8 -*-
import sys, re, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_df.columns = [c.strip() for c in inst_df.columns]
name2id = {str(r["name"]).strip(): int(r["id"]) for _, r in inst_df.iterrows()}

csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_df.columns = [c.strip() for c in csv_df.columns]

for phone in ["13757119185", "13516743880", "13758953542"]:
    pn = re.sub(r"\D", "", phone)
    r = csv_df[csv_df["phone"].astype(str).str.replace(r"\D","",regex=True) == pn]
    if not r.empty:
        row = r.iloc[0]
        print(f"{row['name']}  {phone}  institution_id={int(row['institution_id'])}  ({row['institution_name']})")
