# -*- coding: utf-8 -*-
"""独立复核 grouping_v4.xlsx 的分组逻辑与专家匹配正确性。"""
from __future__ import annotations
import re, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("_verify_v4_report.txt")

def parse_413_full():
    p = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
    xl = pd.ExcelFile(p)
    df = pd.read_excel(p, sheet_name=xl.sheet_names[0], header=None)
    rows = []
    current = None
    for i in range(len(df)):
        r = df.iloc[i]
        g = r[0]
        if pd.notna(g) and str(g).strip():
            current = str(g).strip()
        if current is None or current == "组别": continue
        name = r[3]; phone = r[7] if len(r)>7 else ""
        unit = r[5] if len(r)>5 else ""
        if pd.isna(name) or str(name).strip() in ("","专家"): continue
        pn = re.sub(r"\D","",str(phone)) if pd.notna(phone) else ""
        rows.append({"group":current,"name":str(name).strip(),"phone":pn,"unit_raw":str(unit).strip() if pd.notna(unit) else ""})
    return pd.DataFrame(rows)

def load_csv():
    df = pd.read_csv(ROOT/"专家数据含机构ID0410.csv", encoding="utf-8-sig")
    df["phone_n"] = df["phone"].astype(str).map(lambda x: re.sub(r"\D","",x))
    return df

def load_inst():
    df = pd.read_csv(ROOT/"机构全表0410.csv", encoding="utf-8-sig")
    return {str(r["name"]).strip():int(r["id"]) for _,r in df.iterrows()}

lines = []
def chk(ok, msg):
    tag = "  OK" if ok else "  NG"
    lines.append(f"{tag}  {msg}")
    return ok

detail = pd.read_excel(ROOT/"grouping_v4.xlsx", sheet_name="分组明细")
summary = pd.read_excel(ROOT/"grouping_v4.xlsx", sheet_name="分组汇总")
exp413 = parse_413_full()
csv_exp = load_csv()
inst_map = load_inst()

# ── 1. 项目总数 ────────────────────────────────────────────────
lines.append("=== 1. 项目总数与竞赛组别")
chk(len(detail)==833, f"明细总行数=833  实际={len(detail)}")
for comp,expect in [("基层组",194),("综合组",555),("进阶组",84)]:
    n = (detail["竞赛组别"]==comp).sum()
    chk(n==expect, f"{comp} 行数={expect}  实际={n}")

# ── 2. K 列冲突标记 ────────────────────────────────────────────
lines.append("\n=== 2. K列「⚠️冲突」重算验证")
kcol = next((c for c in detail.columns if "冲突" in str(c)),None)
if kcol:
    flagged = detail[kcol].astype(str).str.contains("冲突",na=False).sum()
    chk(flagged==0, f"K列标冲突行数=0  实际={flagged}")
else:
    lines.append("  NG  K列未找到")

# 独立重算
csv_ph = {r["phone_n"]:(int(r["institution_id"]),str(r["name"])) for _,r in csv_exp.iterrows() if str(r["phone_n"]).strip()}
name_cnt = csv_exp["name"].value_counts()
uniq_name = {str(r["name"]).strip():int(r["institution_id"]) for _,r in csv_exp.iterrows() if name_cnt[str(r["name"])]<2}

def resolve_iid(name, phone):
    pn = re.sub(r"\D","",str(phone))
    if pn and pn in csv_ph: return csv_ph[pn][0]
    base = re.split(r"[（(]",name)[0].strip()
    if base in uniq_name: return uniq_name[base]
    return uniq_name.get(name)

group_expert_inst = defaultdict(set)
for _,r in exp413.iterrows():
    iid = resolve_iid(r["name"],r["phone"])
    if iid: group_expert_inst[r["group"]].add(iid)

real_conflicts = []
for _,r in detail.iterrows():
    gc = str(r["建议分组"]).strip()
    iname = str(r["机构名称"]).strip()
    pi = inst_map.get(iname) or next((v for k,v in inst_map.items() if k.replace(" ","")==iname.replace(" ","")),None)
    if pi and pi in group_expert_inst.get(gc,set()):
        real_conflicts.append((r["项目编号"],r["竞赛组别"],gc,iname))

chk(len(real_conflicts)==0, f"独立重算机构回避冲突=0  实际={len(real_conflicts)}")
for x in real_conflicts[:20]: lines.append(f"       冲突: {x}")

# ── 3. 专家全部在 CSV 有手机 ─────────────────────────────────────
lines.append("\n=== 3. 4.13 名单专家在 CSV 中的手机匹配")
miss = exp413[~exp413["phone"].isin(csv_ph.keys()) & (exp413["phone"]!="")]
miss2 = exp413[exp413["phone"]==""]
chk(len(miss)==0, f"有手机但 CSV 无匹配: {len(miss)} 人  {miss[['group','name','phone']].to_dict('records')[:5]}")
chk(len(miss2)==0, f"书审名单手机为空行: {len(miss2)} 人  {list(miss2['name'])}")

# ── 4. 书审名单各组别 = 分组明细建议分组组号一一对应 ─────────────
lines.append("\n=== 4. 书审名单「组别」均出现在分组明细「建议分组」中")
shu_groups = set(exp413["group"].unique())
detail_groups = set(detail["建议分组"].astype(str).str.strip().unique())
missing_in_detail = shu_groups - detail_groups
extra_in_detail = detail_groups - shu_groups
chk(len(missing_in_detail)==0, f"书审有但分组明细没有的组别: {sorted(missing_in_detail)}")
chk(len(extra_in_detail)==0, f"分组明细有但书审没有的组别: {sorted(extra_in_detail)}")

# ── 5. 汇总表项目数与明细一致 ──────────────────────────────────
lines.append("\n=== 5. 分组汇总「项目数」= 明细实际行数")
detail_cnt = detail["建议分组"].value_counts().to_dict()
ng5 = []
for _,row in summary.iterrows():
    g = str(row.get("小组","")).strip()
    n_sum = int(row.get("项目数",0))
    n_real = detail_cnt.get(g,0)
    if n_sum != n_real: ng5.append((g,n_sum,n_real))
chk(len(ng5)==0, f"汇总 vs 明细不一致: {len(ng5)} 组  {ng5[:5]}")

# ── 6. 每组「报名机构」不含该组任一专家所属机构（最终断言）──────
lines.append("\n=== 6. 最终断言：每组项目机构 ∩ 该组专家机构 = 空集")
failed6 = []
for gc in detail_groups:
    sub = detail[detail["建议分组"].astype(str).str.strip()==gc]
    proj_insts = set()
    for iname in sub["机构名称"].astype(str):
        iname = iname.strip()
        pi = inst_map.get(iname) or next((v for k,v in inst_map.items() if k.replace(" ","")==iname.replace(" ","")),None)
        if pi: proj_insts.add(pi)
    expert_insts = group_expert_inst.get(gc, set())
    overlap = proj_insts & expert_insts
    if overlap:
        inst_names = [k for k,v in inst_map.items() if v in overlap]
        failed6.append((gc, inst_names))
chk(len(failed6)==0, f"回避断言失败: {len(failed6)} 组  {failed6[:5]}")

# ── 7. 吕娜在 CSV 且 B12 专家机构含浙二 ─────────────────────────
lines.append("\n=== 7. 吕娜（13588426741）在 CSV 且 B12 专家集包含浙二(id=24)")
luna_row = csv_exp[csv_exp["phone_n"]=="13588426741"]
chk(len(luna_row)==1, f"吕娜在CSV中存在: {len(luna_row)} 条")
chk(len(luna_row)==1 and int(luna_row.iloc[0]["institution_id"])==24, "吕娜 institution_id=24(浙二)")
chk(24 in group_expert_inst.get("B12",set()), "B12 专家机构集含 24(浙二)")

# ── 写出 ──────────────────────────────────────────────────────
text = "\n".join(lines)
OUT.write_text(text, encoding="utf-8")
ok_cnt = text.count("  OK")
ng_cnt = text.count("  NG")
print(f"复核完成: {ok_cnt} 项通过 / {ng_cnt} 项失败   → {OUT}")
