# -*- coding: utf-8 -*-
"""
生成 grouping_final 两份文本：
  1. grouping_final_gap.txt   ── 分组级差距 summary（4.7预期 vs 实际，含手法构成偏差）
  2. grouping_final_listing.txt ── 各组书审专家 + 报名机构清单
"""
from __future__ import annotations
import re, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ── 4.7 口径预期（数量 + 预期手法描述）────────────────────────────
EXPECTED = {
    # 基层组
    "A1": (32,  "十大安全目标混合（品管圈-问题解决21+PDCA3+FOCUS-PDCA1+课题达成1+根本原因4+失效模式2）"),
    "A2": (30,  "品管圈-问题解决"),
    "A3": (29,  "品管圈-问题解决"),
    "A4": (29,  "品管圈-课题达成20+品管圈-问题解决9"),
    "A5": (27,  "PDCA"),
    "A6": (26,  "PDCA5+FOCUS-PDCA21"),
    "A7": (21,  "综合工具组（根本原因6+六西格玛4+失效模式4+QFD4+其他2+流程改造1）"),
    # 综合组
    "B1":  (26, "十大安全目标×品管圈-问题解决26"),
    "B2":  (26, "十大安全目标×混合（品管圈-问题解决9+课题达成11+失效模式3+六西格玛1+根本原因1+专案改善1）"),
    "B3":  (27, "十大安全目标×PDCA17+FOCUS-PDCA10"),
    "B4":  (27, "品管圈-问题解决"),
    "B5":  (27, "品管圈-问题解决"),
    "B6":  (27, "品管圈-问题解决"),
    "B7":  (27, "品管圈-问题解决"),
    "B8":  (27, "品管圈-问题解决"),
    "B9":  (26, "品管圈-问题解决"),
    "B10": (26, "品管圈-课题达成"),
    "B11": (26, "品管圈-课题达成"),
    "B12": (26, "品管圈-课题达成"),
    "B13": (26, "品管圈-课题达成"),
    "B14": (26, "QFD"),
    "B15": (24, "PDCA"),
    "B16": (24, "PDCA"),
    "B17": (24, "PDCA"),
    "B18": (24, "FOCUS-PDCA"),
    "B19": (23, "FOCUS-PDCA"),
    "B20": (29, "失效模式与效应分析"),
    "B21": (18, "根本原因分析12+其他:*6"),
    "B22": (19, "综合工具组（专案改善9+六西格玛5+流程改造3+5S1+平衡计分卡1）"),
    # 进阶组
    "C1": (22, "品管圈-课题达成"),
    "C2": (21, "品管圈-课题达成10+QFD11"),
    "C3": (20, "品管圈-问题解决15+FOCUS-PDCA5"),
    "C4": (21, "综合工具组（PDCA12+失效模式3+循证医学2+六西格玛2+其他1+平衡计分卡1）"),
}
COMP_MAP = {
    **{f"A{i}": "基层组" for i in range(1,8)},
    **{f"B{i}": "综合组" for i in range(1,23)},
    **{f"C{i}": "进阶组" for i in range(1,5)},
}

# ── 载入数据 ──────────────────────────────────────────────────────
detail = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")

# 重建初始 4.7 分组（对比用）
import export_grouping_v5 as ev5
base = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
init = ev5.assign_groups(base)

# ── 专家数据 ─────────────────────────────────────────────────────
csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_ph = {re.sub(r"\D","",str(r["phone"])): (str(r["name"]), str(r["institution_name"]),
          str(r.get("title","")).strip()) for _, r in csv_df.iterrows()}
name_cnt = csv_df["name"].value_counts()
uniq_name = {str(r["name"]).strip(): (str(r["institution_name"]), str(r.get("title","")).strip())
             for _, r in csv_df.iterrows() if name_cnt[r["name"]] < 2}

def expert_info(name, phone):
    pn = re.sub(r"\D","",str(phone)) if pd.notna(phone) else ""
    if pn and pn in csv_ph:
        _, inst, title = csv_ph[pn]
        return inst, title
    base = re.split(r"[（(]", str(name))[0].strip()
    if base in uniq_name: return uniq_name[base]
    return uniq_name.get(str(name).strip(), ("(未匹配)", ""))

# 解析 4.13 书审名单
p_shu = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
xl    = pd.ExcelFile(p_shu)
df_sh = pd.read_excel(p_shu, sheet_name=xl.sheet_names[0], header=None)
grp_experts: dict[str, list] = defaultdict(list)
cur = None
for i in range(len(df_sh)):
    r = df_sh.iloc[i]; g = r[0]
    if pd.notna(g) and str(g).strip() and str(g).strip() != "nan":
        cur = str(g).strip()
    if not cur: continue
    nm = r[3] if len(r) > 3 else None
    if pd.isna(nm) or str(nm).strip() in ("","专家","姓名","nan"): continue
    ph = r[7] if len(r) > 7 else ""
    pn = re.sub(r"\D","",str(ph)) if pd.notna(ph) else ""
    inst, title = expert_info(nm, ph)
    grp_experts[cur].append((str(nm).strip(), pn, inst, title))


# ════════════════════════════════════════════════════════════════
# 1. 差距 summary
# ════════════════════════════════════════════════════════════════
gap_lines = []
gap_lines.append("=" * 70)
gap_lines.append("  grouping_final vs 4.7 口径  分组级差距 summary")
gap_lines.append("=" * 70)

for comp in ["基层组", "综合组", "进阶组"]:
    groups = [g for g in sorted(EXPECTED, key=lambda x: (x[0], int(x[1:]))) if COMP_MAP[g] == comp]
    gap_lines.append(f"\n【{comp}】")
    for g in groups:
        exp_cnt, exp_desc = EXPECTED[g]
        act_cnt = (detail["建议分组"] == g).sum()
        init_mc  = init[init["建议分组"]==g]["运用手法"].value_counts().to_dict()
        final_mc = detail[detail["建议分组"]==g]["运用手法"].value_counts().to_dict()

        cnt_mark = "✓" if act_cnt == exp_cnt else f"△(差{act_cnt-exp_cnt:+d})"
        gap_lines.append(f"  {g:<4}  预期 {exp_cnt:3d} 条  实际 {act_cnt:3d} 条  {cnt_mark}")
        gap_lines.append(f"       预期构成: {exp_desc}")

        # 手法构成差异
        all_m = sorted(set(init_mc) | set(final_mc))
        diffs = [(m, init_mc.get(m,0), final_mc.get(m,0)) for m in all_m
                 if init_mc.get(m,0) != final_mc.get(m,0)]
        if diffs:
            gap_lines.append("       实际构成偏差（因回避试算交换）:")
            for m, i_n, f_n in diffs:
                arrow = "↓少了" if f_n < i_n else "↑多了"
                gap_lines.append(f"         {m}: {i_n}→{f_n}  {arrow}{abs(f_n-i_n)}")
        else:
            gap_lines.append("       实际构成: 与预期完全一致")

Path("grouping_final_gap.txt").write_text("\n".join(gap_lines), encoding="utf-8")


# ════════════════════════════════════════════════════════════════
# 2. 全量清单
# ════════════════════════════════════════════════════════════════
listing = []
listing.append("=" * 70)
listing.append("  grouping_final  各分组书审专家 + 报名机构清单")
listing.append("=" * 70)

for comp in ["基层组", "综合组", "进阶组"]:
    groups = [g for g in sorted(EXPECTED, key=lambda x: (x[0], int(x[1:]))) if COMP_MAP[g] == comp]
    listing.append(f"\n{'─'*60}")
    listing.append(f"  {comp}")
    listing.append(f"{'─'*60}")
    for g in groups:
        sub = detail[detail["建议分组"] == g]
        listing.append(f"\n【{comp} · {g}】 项目数: {len(sub)}")

        experts = grp_experts.get(g, [])
        listing.append("\n  ■ 书审专家（名单顺序）及所属机构（CSV）:")
        if experts:
            for nm, pn, inst, title in experts:
                t_str = f" / {title}" if title and title not in ("nan","") else ""
                listing.append(f"      · {nm}  {pn}  →  {inst}{t_str}")
        else:
            listing.append("      · （无）")

        inst_cnt = sub["机构名称"].value_counts()
        listing.append(f"\n  ■ 该组报名项目涉及机构（去重，共 {len(inst_cnt)} 家）:")
        for iname, cnt in inst_cnt.sort_index().items():
            listing.append(f"      · {iname}  （{cnt} 项）")

Path("grouping_final_listing.txt").write_text("\n".join(listing), encoding="utf-8")

print(f"差距summary → grouping_final_gap.txt ({len(gap_lines)} 行)")
print(f"全量清单   → grouping_final_listing.txt ({len(listing)} 行)")
