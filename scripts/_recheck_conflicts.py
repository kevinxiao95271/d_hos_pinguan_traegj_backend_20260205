# -*- coding: utf-8 -*-
"""
用 4.13 名单中的实际机构（含三位修正值）重新校验 grouping_final 是否存在机构回避冲突
"""
import sys, re
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

# ── 1. 专家机构修正覆盖（phone → 正确 institution_id）────────────────────────
# 以 4.13 名单 xls 为准的三位修正值
INST_OVERRIDE = {
    "13757119185": (218, "杭州市妇幼保健院"),      # 陈昌贵  B7
    "13516743880": (12,  "宁波市第二医院"),         # 楼尉    A6
    "13758953542": (1,   "东阳市人民医院"),         # 吴海英  A7
}

# ── 2. 读专家 CSV（生产库快照）────────────────────────────────────────────────
csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_df.columns = [c.strip() for c in csv_df.columns]
expert_map: dict[str, tuple[str, int, str]] = {}   # phone → (name, inst_id, inst_name)
for _, r in csv_df.iterrows():
    pn = re.sub(r"\D", "", str(r.get("phone", "")))
    if not pn:
        continue
    iid  = int(r["institution_id"]) if pd.notna(r.get("institution_id")) else 0
    iname = str(r.get("institution_name", "")).strip()
    expert_map[pn] = (str(r["name"]).strip(), iid, iname)

# ── 3. 读 4.13 名单，得到 phone→group_code ────────────────────────────────────
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
xl    = pd.ExcelFile(p_413)
df_sh = pd.read_excel(p_413, sheet_name=xl.sheet_names[0], header=None)

expert_grp: dict[str, str]              = {}   # phone → group_code
grp_experts: dict[str, list[tuple]]     = {}   # group_code → [(name, inst_id, inst_name)]

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
    if not pn:
        continue

    # 取机构（优先 INST_OVERRIDE，其次 CSV）
    if pn in INST_OVERRIDE:
        iid, iname = INST_OVERRIDE[pn]
        nm_str = str(nm).strip()
    elif pn in expert_map:
        nm_str, iid, iname = expert_map[pn]
    else:
        nm_str = str(nm).strip()
        iid, iname = 0, "未知"

    expert_grp[pn] = cur_gc
    grp_experts.setdefault(cur_gc, []).append((nm_str, iid, iname))

# ── 4. 读机构全表，建立名称→id 映射 ─────────────────────────────────────────
inst_df = pd.read_csv(ROOT / "机构全表0410.csv", encoding="utf-8-sig")
inst_df.columns = [c.strip() for c in inst_df.columns]
name2id: dict[str, int] = {str(r["name"]).strip(): int(r["id"]) for _, r in inst_df.iterrows()}

# ── 5. 读 grouping_final 分组明细 ─────────────────────────────────────────────
gf_path = ROOT / "grouping_final.xlsx"
proj_df = pd.read_excel(gf_path, sheet_name="分组明细")
proj_df.columns = [c.strip() for c in proj_df.columns]

gc_col    = "建议分组"
pid_col   = "项目编号"
iname_col = "机构名称"

# 用机构名称反查 institution_id
proj_df["_inst_id"] = proj_df[iname_col].map(lambda n: name2id.get(str(n).strip(), 0))
inst_col = "_inst_id"

# ── 6. 逐组检查冲突 ────────────────────────────────────────────────────────────
conflicts = []

for gc, exp_list in grp_experts.items():
    exp_inst_ids = {e[1] for e in exp_list if e[1]}
    projs_in_grp = proj_df[proj_df[gc_col].astype(str).str.strip() == gc]
    for _, pr in projs_in_grp.iterrows():
        try:
            p_iid = int(pr[inst_col])
        except (ValueError, TypeError):
            continue
        if p_iid in exp_inst_ids:
            # 找出是哪位专家
            clash_experts = [e for e in exp_list if e[1] == p_iid]
            conflicts.append({
                "组别": gc,
                "项目编号": pr.get(pid_col, ""),
                "项目机构": pr.get(iname_col, p_iid),
                "冲突专家": "、".join(f"{e[0]}({e[2]})" for e in clash_experts),
            })

# ── 7. 输出 ───────────────────────────────────────────────────────────────────
print("=" * 60)
print(f"重新校验（含陈昌贵/楼尉/吴海英机构修正）")
print(f"冲突数: {len(conflicts)}")
print("=" * 60)

if conflicts:
    print("\n⚠️  发现冲突：")
    for c in conflicts:
        print(f"  [{c['组别']}] 项目 {c['项目编号']}  机构={c['项目机构']}")
        print(f"         冲突专家: {c['冲突专家']}")
else:
    print("\n✅ 零冲突，所有分组均通过机构回避校验。")

# ── 附：仅打印三位修正专家所在组的项目机构列表，方便人工复核 ─────────────────
print("\n── 修正专家所在组项目机构明细 ──────────────────────────────────")
focus = {"B7": ("陈昌贵", 218, "杭州市妇幼保健院"),
         "A6": ("楼尉",   12,  "宁波市第二医院"),
         "A7": ("吴海英", 1,   "东阳市人民医院")}
for gc, (nm, iid, iname) in focus.items():
    projs = proj_df[proj_df[gc_col].astype(str).str.strip() == gc]
    print(f"\n[{gc}] 专家={nm}({iname}, id={iid})  项目数={len(projs)}")
    for _, pr in projs.iterrows():
        try:
            p_iid = int(pr[inst_col])
        except Exception:
            p_iid = -1
        flag = " ⚠️ 冲突" if p_iid == iid else ""
        print(f"  {pr.get(pid_col,'')}  机构={pr.get(iname_col, p_iid)}(id={p_iid}){flag}")
