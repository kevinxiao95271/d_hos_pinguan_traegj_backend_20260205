# -*- coding: utf-8 -*-
"""
对比生产库导出（评审专家&机构0413.csv）与 4.13 书审名单
检查：name / phone / institution_name 是否一致
"""
import sys, re
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

# ── 1. 读生产库导出 ──────────────────────────────────────────────────────────
prod_df = pd.read_csv(ROOT / "评审专家&机构0413.csv", encoding="utf-8-sig")
prod_df.columns = [c.strip() for c in prod_df.columns]
print("生产库列名:", prod_df.columns.tolist())
print()

# 统一用 phone 作主键，去掉非数字
prod: dict[str, dict] = {}
for _, r in prod_df.iterrows():
    pn = re.sub(r"\D", "", str(r.get("phone", "") or ""))
    if pn:
        prod[pn] = {k: str(v).strip() if pd.notna(v) else "" for k, v in r.items()}

# ── 2. 读 4.13 名单 ──────────────────────────────────────────────────────────
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
xl    = pd.ExcelFile(p_413)
df_sh = pd.read_excel(p_413, sheet_name=xl.sheet_names[0], header=None)

experts413: list[dict] = []
cur_gc = None
for i in range(len(df_sh)):
    r  = df_sh.iloc[i]
    g  = r[0]
    if pd.notna(g) and str(g).strip() not in ("", "nan"):
        cur_gc = str(g).strip()
    if not cur_gc:
        continue
    nm = r[3] if len(r) > 3 else None
    if pd.isna(nm) or str(nm).strip() in ("", "专家", "姓名", "nan"):
        continue
    ph_raw = r[7] if len(r) > 7 else ""
    pn = re.sub(r"\D", "", str(ph_raw)) if pd.notna(ph_raw) else ""
    inst = str(r[5]).strip() if len(r) > 5 and pd.notna(r[5]) else ""
    if not pn:
        continue
    experts413.append({"group": cur_gc, "name": str(nm).strip(),
                       "phone": pn, "institution": inst})

# ── 3. 对比 ──────────────────────────────────────────────────────────────────
ok, warn = [], []

for e in experts413:
    pn = e["phone"]
    if pn not in prod:
        warn.append(f"❌ 【不在生产库】{e['name']}  {pn}  ({e['group']})")
        continue

    p = prod[pn]
    issues = []

    # name 对比
    prod_name = p.get("name", "")
    if prod_name != e["name"]:
        issues.append(f"name: 生产库={prod_name!r} / 名单={e['name']!r}")

    # institution_name 对比（生产库字段可能叫 institution_name 或 name）
    prod_inst = p.get("institution_name", p.get("inst_name", ""))
    xls_inst  = e["institution"]
    if xls_inst and prod_inst and prod_inst != xls_inst:
        issues.append(f"机构: 生产库={prod_inst!r} / 名单={xls_inst!r}")

    if issues:
        warn.append(f"⚠️  {e['name']}  {pn}  ({e['group']})  →  " + "；".join(issues))
    else:
        ok.append(f"✅  {e['name']}  {pn}  ({e['group']})")

# ── 4. 输出 ──────────────────────────────────────────────────────────────────
print(f"{'='*60}")
print(f"4.13 名单: {len(experts413)} 人   生产库: {len(prod)} 条")
print(f"一致: {len(ok)}   有差异/缺失: {len(warn)}")
print(f"{'='*60}")

if warn:
    print("\n── 需关注 ──────────────────────────────────────────────────")
    for w in warn:
        print(w)

print("\n── 全部一致 ────────────────────────────────────────────────")
for o in ok:
    print(o)
