# -*- coding: utf-8 -*-
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_df.columns = [c.strip() for c in inst_df.columns]
name2id = {str(r["name"]).strip(): int(r["id"]) for _, r in inst_df.iterrows()}

proj_df = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
proj_df.columns = [c.strip() for c in proj_df.columns]
proj_df["_inst_id"] = proj_df["机构名称"].map(lambda n: name2id.get(str(n).strip(), 0))

# 核实后的确认机构
FOCUS = {
    "陈昌贵": ("B7",  218, "杭州市妇幼保健院"),
    "楼尉":   ("A6",  11,  "宁波市第九医院（宁波市第一医院江北分院、宁波市江北区人民医院）"),
    "吴海英": ("A7",  1,   "东阳市人民医院"),
}

print("=" * 60)
for nm, (gc, iid, iname) in FOCUS.items():
    projs = proj_df[proj_df["建议分组"].astype(str).str.strip() == gc]
    clashes = projs[projs["_inst_id"] == iid]
    if clashes.empty:
        print(f"✅  [{gc}] {nm} ({iname}, id={iid}) — 无冲突")
    else:
        print(f"⚠️  [{gc}] {nm} ({iname}, id={iid}) — 发现冲突：")
        for _, p in clashes.iterrows():
            print(f"     项目 {p['项目编号']}  机构={p['机构名称']}")
print("=" * 60)
