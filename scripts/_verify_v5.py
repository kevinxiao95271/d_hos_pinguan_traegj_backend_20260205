# -*- coding: utf-8 -*-
"""独立复核 grouping_v5.xlsx：4.7 口径对齐 + 机构回避断言。"""
from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT  = Path(__file__).with_name("_verify_v5_report.txt")

lines: list[str] = []

def chk(ok: bool, msg: str) -> bool:
    lines.append(("  OK  " if ok else "  NG  ") + msg)
    return ok

# ── 载入数据 ────────────────────────────────────────────────────
detail = pd.read_excel(ROOT / "grouping_v5.xlsx", sheet_name="分组明细")
summary = pd.read_excel(ROOT / "grouping_v5.xlsx", sheet_name="分组汇总")

# ── 专家机构集 ───────────────────────────────────────────────────
def load_expert_group_inst():
    csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
    csv_ph = {re.sub(r"\D","",str(r["phone"])): int(r["institution_id"])
              for _, r in csv_df.iterrows()}
    name_cnt = csv_df["name"].value_counts()
    uniq_name = {str(r["name"]).strip(): int(r["institution_id"])
                 for _, r in csv_df.iterrows() if name_cnt[r["name"]] < 2}

    p = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
    xl = pd.ExcelFile(p)
    df = pd.read_excel(p, sheet_name=xl.sheet_names[0], header=None)
    cur = None
    grp_inst: dict[str, set] = defaultdict(set)
    for i in range(len(df)):
        r = df.iloc[i]
        g = r[0]
        if pd.notna(g) and str(g).strip() and str(g).strip() != "nan":
            cur = str(g).strip()
        if not cur: continue
        name = r[3] if len(r) > 3 else None
        if pd.isna(name) or str(name).strip() in ("", "专家", "姓名", "nan"): continue
        phone = r[7] if len(r) > 7 else ""
        pn = re.sub(r"\D", "", str(phone)) if pd.notna(phone) else ""
        iid = csv_ph.get(pn) or uniq_name.get(str(name).strip())
        if iid:
            grp_inst[cur].add(iid)
    return grp_inst

# ── 机构名→ID ────────────────────────────────────────────────────
inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_map = {str(r["name"]).strip(): int(r["id"]) for _, r in inst_df.iterrows()}

def get_inst_id(name: str):
    name = str(name).strip()
    if name in inst_map: return inst_map[name]
    return next((v for k, v in inst_map.items()
                 if k.replace(" ","") == name.replace(" ","")), None)

group_expert_inst = load_expert_group_inst()

# ── 1. 4.7 口径分组数量对齐 ──────────────────────────────────────
lines.append("=== 1. 4.7 口径分组数量校验")
expected = {
    "A1":32,"A2":30,"A3":29,"A4":29,"A5":27,"A6":26,"A7":21,
    "B1":26,"B2":26,"B3":27,
    "B4":27,"B5":27,"B6":27,"B7":27,"B8":27,"B9":26,
    "B10":26,"B11":26,"B12":26,"B13":26,
    "B14":26,"B15":24,"B16":24,"B17":24,"B18":24,"B19":23,
    "B20":29,"B21":18,"B22":19,
    "C1":22,"C2":21,"C3":20,"C4":21,
}
actual_cnt = detail["建议分组"].value_counts().to_dict()
all_ok = True
for grp, exp in sorted(expected.items()):
    act = actual_cnt.get(grp, 0)
    ok = chk(act == exp, f"{grp}: 期望={exp}  实际={act}")
    if not ok: all_ok = False

# ── 2. 手法构成抽查 ──────────────────────────────────────────────
lines.append("\n=== 2. 关键手法构成抽查")
def method_cnt(grp, method):
    return len(detail[(detail["建议分组"]==grp) & (detail["运用手法"]==method)])

chk(method_cnt("B14","QFD")==26,          "B14 全为 QFD(26)")
chk(method_cnt("B20","失效模式与效应分析")==29, "B20 全为失效模式(29)")
chk(method_cnt("B21","根本原因分析")==12,  "B21 根本原因分析=12")
b21_other = len(detail[(detail["建议分组"]=="B21") & (detail["运用手法"].str.startswith("其他"))])
chk(b21_other == 6, f"B21 其他:*=6  实际={b21_other}")
b22_methods = {"专案改善","六西格玛管理","流程改造","5S","平衡计分卡"}
b22_wrong = detail[(detail["建议分组"]=="B22") & (~detail["运用手法"].isin(b22_methods))]
chk(len(b22_wrong)==0, f"B22 无混入手法  混入={len(b22_wrong)}")
chk(method_cnt("A7","QFD")==4, "A7 含 QFD(4)")

# ── 3. 十大安全目标归 A1 ────────────────────────────────────────
lines.append("\n=== 3. 基层组十大安全目标全归 A1")
jc = detail[detail["竞赛组别"]=="基层组"]
ten_not_a1 = jc[(jc["十大安全目标"]!="其他") & (jc["建议分组"]!="A1")]
chk(len(ten_not_a1)==0, f"基层十大全在A1  漏={len(ten_not_a1)}")
a1_non_ten = jc[(jc["十大安全目标"]=="其他") & (jc["建议分组"]=="A1")]
chk(len(a1_non_ten)==0, f"A1 无非十大项目  多={len(a1_non_ten)}")

# ── 4. K 列冲突 = 0 ─────────────────────────────────────────────
lines.append("\n=== 4. K列冲突标记")
kcol = next((c for c in detail.columns if "冲突" in str(c)), None)
if kcol:
    flagged = detail[kcol].astype(str).str.contains("冲突", na=False).sum()
    chk(flagged == 0, f"K列标冲突行数=0  实际={flagged}")
else:
    lines.append("  NG  K列未找到")

# ── 5. 独立重算机构回避冲突 ──────────────────────────────────────
lines.append("\n=== 5. 独立重算机构回避冲突（逐行断言）")
real_conflicts = []
for _, r in detail.iterrows():
    gc = str(r["建议分组"]).strip()
    pi = get_inst_id(str(r["机构名称"]))
    if pi and pi in group_expert_inst.get(gc, set()):
        real_conflicts.append((r["项目编号"], r["竞赛组别"], gc, r["机构名称"]))
chk(len(real_conflicts) == 0, f"机构回避冲突=0  实际={len(real_conflicts)}")
for x in real_conflicts[:10]: lines.append(f"       冲突: {x}")

# ── 6. 最终断言：每组项目机构 ∩ 专家机构 = 空集 ────────────────
lines.append("\n=== 6. 最终断言：每组项目机构 ∩ 专家机构 = 空集")
failed = []
for gc in detail["建议分组"].unique():
    sub = detail[detail["建议分组"].astype(str).str.strip()==gc]
    proj_insts = {get_inst_id(str(n)) for n in sub["机构名称"]} - {None}
    exp_insts = group_expert_inst.get(gc, set())
    overlap = proj_insts & exp_insts
    if overlap:
        names = [k for k,v in inst_map.items() if v in overlap]
        failed.append((gc, names))
chk(len(failed)==0, f"回避断言全通过  失败={len(failed)}")
for f in failed[:5]: lines.append(f"       {f}")

# ── 7. 吕娜 B12 ──────────────────────────────────────────────────
lines.append("\n=== 7. 吕娜（13588426741）在 B12 专家集 institution_id=24")
csv_df = pd.read_csv(ROOT/"专家数据含机构ID0410.csv", encoding="utf-8-sig")
luna = csv_df[csv_df["phone"].astype(str).str.replace(r"\D","",regex=True)=="13588426741"]
chk(len(luna)==1, f"吕娜在CSV中唯一  条数={len(luna)}")
chk(len(luna)==1 and int(luna.iloc[0]["institution_id"])==24, "吕娜 institution_id=24")
chk(24 in group_expert_inst.get("B12",set()), "B12 专家机构含 id=24(浙二)")

# ── 写出 ──────────────────────────────────────────────────────────
text = "\n".join(lines)
OUT.write_text(text, encoding="utf-8")
ok_n = text.count("  OK  ")
ng_n = text.count("  NG  ")
print(f"复核完成: {ok_n} 项通过 / {ng_n} 项失败  → {OUT.name}")
