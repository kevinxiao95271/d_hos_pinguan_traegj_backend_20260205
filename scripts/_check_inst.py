# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_df.columns = [c.strip() for c in inst_df.columns]

# 需要确认的机构名（4.13 名单里的说法，去简称后的全称）
checks = {
    "洪理泉/封亚萍": "杭州市第二人民医院",
    "陈昌贵":         "杭州市妇幼保健院",
    "楼尉":           "宁波市第二医院",
    "吴海英":         "东阳市人民医院",
}

for person, name in checks.items():
    hits = inst_df[inst_df["name"].str.contains(name.replace("（","").replace("）",""), na=False)]
    print(f"── {person} 查询：'{name}'")
    if hits.empty:
        print("  ❌ 未找到")
    else:
        for _, r in hits.iterrows():
            print(f"  ✅ id={int(r['id'])}  name={r['name']}")
    print()
