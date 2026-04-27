# -*- coding: utf-8 -*-
import sys, re
import pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

# 机构全表
inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_df.columns = [c.strip() for c in inst_df.columns]
name2id = {str(r["name"]).strip(): int(r["id"]) for _, r in inst_df.iterrows()}
id2name = {int(r["id"]): str(r["name"]).strip() for _, r in inst_df.iterrows()}

# CSV 专家机构
csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_df.columns = [c.strip() for c in csv_df.columns]
phone2inst = {}
for _, r in csv_df.iterrows():
    pn = re.sub(r"\D", "", str(r.get("phone", "")))
    if pn:
        phone2inst[pn] = (str(r["name"]).strip(),
                          int(r["institution_id"]) if pd.notna(r.get("institution_id")) else 0,
                          str(r.get("institution_name","")).strip())

# grouping_final
proj_df = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
proj_df.columns = [c.strip() for c in proj_df.columns]
proj_df["_inst_id"] = proj_df["机构名称"].map(lambda n: name2id.get(str(n).strip(), 0))

# 同名医院映射（告知系统这两对是同一机构）
ALIAS = {
    # phone: (institution_id_in_prod, alias_name_in_413)
    "13958202082": (None, "鄞州人民医院",          "宁波大学附属人民医院"),  # 冯济业
    "13606700679": (None, "杭州市第二人民医院",     "杭州师范大学附属医院"),  # 洪理泉
    "13867134906": (None, "杭州市第二人民医院",     "杭州师范大学附属医院"),  # 封亚萍
}

focus = {
    "13958202082": "B21",
    "13606700679": "B4",
    "13867134906": "B17",
}

print("── 三位专家机构在 CSV / 机构全表 中的实际 id ─────────────────────")
for pn, gc in focus.items():
    nm, iid, iname = phone2inst.get(pn, ("?", 0, "?"))
    print(f"  {nm}  {pn}  {gc}  CSV institution_id={iid}  ({iname})")
    # 机构全表反查
    full_name = id2name.get(iid, "未找到")
    print(f"    → 机构全表 id={iid}: {full_name}")

print()
print("── 各组内是否有同机构项目 ────────────────────────────────────────")
for pn, gc in focus.items():
    nm, iid, iname = phone2inst.get(pn, ("?", 0, "?"))
    projs = proj_df[proj_df["建议分组"].astype(str).str.strip() == gc]
    clashes = projs[projs["_inst_id"] == iid]
    if clashes.empty:
        print(f"  ✅ [{gc}] {nm}(id={iid})  — 无冲突")
    else:
        for _, p in clashes.iterrows():
            print(f"  ⚠️  [{gc}] {nm}(id={iid}) 与项目 {p['项目编号']} ({p['机构名称']}) 冲突")
