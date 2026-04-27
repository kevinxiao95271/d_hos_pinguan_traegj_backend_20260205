# -*- coding: utf-8 -*-
"""
生成 grouping_final.xlsx（三个 Sheet）
  分组明细  ── 4.7 口径分组 + 机构回避试算，冲突=0
  分组汇总  ── 各组项目数
  差距说明  ── 因回避试算产生的手法构成偏差：少了谁/多了谁/原因
口径修正：基层组 QFD 4 条全部归 A7（综合工具组），A4 仅含品管圈-课题达成+品管圈-问题解决。
"""
from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path
import pandas as pd

ROOT   = Path(__file__).resolve().parents[1]
REPORT = Path(__file__).with_name("grouping_final_avoidance_report.txt")
OUTPUT = ROOT / "grouping_final.xlsx"

# ──────────────────────────────────────────────────────────────
# 复用 v5 分组逻辑（含 QFD4→A7 修正）
# ──────────────────────────────────────────────────────────────
import export_grouping_v5 as ev5
assign_groups = ev5.assign_groups

# ──────────────────────────────────────────────────────────────
# 加载评委机构集（用于差距溯源）
# ──────────────────────────────────────────────────────────────
def load_expert_group_inst_full():
    """返回 {group_code: {inst_id: [expert_name, ...]}}"""
    csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
    csv_ph = {re.sub(r"\D","",str(r["phone"])): (int(r["institution_id"]), str(r["institution_name"]))
              for _, r in csv_df.iterrows()}
    name_cnt = csv_df["name"].value_counts()
    uniq_name = {str(r["name"]).strip(): (int(r["institution_id"]), str(r["institution_name"]))
                 for _, r in csv_df.iterrows() if name_cnt[r["name"]] < 2}

    p = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
    xl = pd.ExcelFile(p)
    df = pd.read_excel(p, sheet_name=xl.sheet_names[0], header=None)
    cur = None
    grp: dict[str, dict] = defaultdict(dict)   # {gc: {inst_id: expert_name}}
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
        hit = csv_ph.get(pn) or uniq_name.get(str(name).strip())
        if hit:
            iid, iname = hit
            grp[cur][iid] = f"{name.strip()}({iname})"
    return grp


def get_inst_id(name: str, inst_map: dict) -> int | None:
    name = str(name).strip()
    return inst_map.get(name) or next(
        (v for k, v in inst_map.items() if k.replace(" ","") == name.replace(" ","")), None)


# ──────────────────────────────────────────────────────────────
# 差距说明生成
# ──────────────────────────────────────────────────────────────
def build_gap_sheet(init_df: pd.DataFrame, final_df: pd.DataFrame,
                    expert_grp_inst: dict, inst_map: dict) -> pd.DataFrame:
    """
    逐行对比初始分组（4.7口径）与最终分组（回避后），
    对每个被交换的项目找出触发原因（是哪位评委的机构冲突）。
    """
    rows = []
    mask = init_df["建议分组"].astype(str) != final_df["建议分组"].astype(str)
    for idx in init_df[mask].index:
        r       = init_df.loc[idx]
        init_gc = str(r["建议分组"]).strip()
        fin_gc  = str(final_df.at[idx, "建议分组"]).strip()
        method  = str(r["运用手法"]).strip()
        iname   = str(r["机构名称"]).strip()
        pid     = str(r["项目编号"])
        inst_id = get_inst_id(iname, inst_map)

        # 找是哪位评委导致该项目从 init_gc 换走
        cause = ""
        if inst_id and inst_id in expert_grp_inst.get(init_gc, {}):
            cause = f"原组{init_gc}评委 {expert_grp_inst[init_gc][inst_id]} 与该项目同机构"

        rows.append({
            "项目编号":      pid,
            "竞赛组别":      r["竞赛组别"],
            "机构名称":      iname,
            "运用手法":      method,
            "4.7初始分组":   init_gc,
            "最终分组":      fin_gc,
            "变动类型":      f"从{init_gc}移出" if cause else f"移入{fin_gc}（配对交换）",
            "少了/多了":     f"{init_gc} 少了该手法" if cause else f"{fin_gc} 多了该手法",
            "根本原因":      cause if cause else "作为配对项被换入",
        })

    df_gap = pd.DataFrame(rows)

    # 按竞赛组别 + 初始分组排序
    comp_order = {"基层组": 0, "综合组": 1, "进阶组": 2}
    df_gap["_ord"] = df_gap["竞赛组别"].map(comp_order)
    df_gap = df_gap.sort_values(["_ord", "4.7初始分组", "最终分组"]).drop(columns=["_ord"])

    return df_gap


def build_summary(detail: pd.DataFrame, v2_summary: pd.DataFrame) -> pd.DataFrame:
    cnt = detail.groupby("建议分组", as_index=False).size().rename(columns={"size": "项目数"})
    m = v2_summary.merge(cnt, left_on="小组", right_on="建议分组", how="left", suffixes=("","_new"))
    if "项目数_new" in m.columns:
        m["项目数"] = m["项目数_new"].fillna(m["项目数"])
        m = m.drop(columns=[c for c in m.columns if c.endswith("_new")])
    if "建议分组" in m.columns: m = m.drop(columns=["建议分组"])
    if "剩余冲突" in m.columns: m["剩余冲突"] = 0
    if "状态"   in m.columns: m["状态"] = "✅ 无冲突"
    return m


# ──────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────
def main():
    import trial_grouping_avoidance as t

    phone_map, unique_name, _dup = t.load_expert_lookup()
    inst_map  = t.load_inst_name_to_id()
    grp_raw   = t.parse_shushen_groups()
    expert_inst, warn = t.resolve_expert_institutions(grp_raw, phone_map, unique_name)
    expert_grp_inst_full = load_expert_group_inst_full()

    base     = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
    v2_sum   = pd.read_excel(ROOT / "grouping_v2.xlsx", sheet_name="分组汇总")

    # 4.7 口径初始分组
    init_df  = assign_groups(base)

    # 断言：基层组 QFD 全在 A7
    a7_qfd = ((init_df["竞赛组别"]=="基层组") &
              (init_df["运用手法"]=="QFD") &
              (init_df["建议分组"]=="A7")).sum()
    total_qfd_basic = ((init_df["竞赛组别"]=="基层组") & (init_df["运用手法"]=="QFD")).sum()
    assert a7_qfd == total_qfd_basic == 4, f"基层组QFD应全在A7，实际A7={a7_qfd}/总={total_qfd_basic}"

    lines = ["=== grouping_final 回避试算"]
    lines.append(f"书审表: {t.resolve_shushen_excel().name}")
    lines.append("未匹配专家: 无" if not warn else "未匹配专家:\n" + "\n".join(warn))

    detail_work = init_df.copy()
    for comp in ("基层组", "综合组", "进阶组"):
        tb = t.count_conflicts(detail_work, expert_inst, inst_map, comp)
        df2, _, ta, rounds = t.try_improve_swaps(detail_work, expert_inst, inst_map, comp)
        detail_work = df2
        lines.append(f"{comp}: {tb} -> {ta}, 轮次{rounds}")

    detail_work = t.sync_conflict_marker_column(detail_work, expert_inst, inst_map)
    final_n = sum(t.count_conflicts(detail_work, expert_inst, inst_map, c)
                  for c in ("基层组","综合组","进阶组"))
    lines.append(f"最终冲突: {final_n}")

    # 差距说明
    gap_df = build_gap_sheet(init_df, detail_work, expert_grp_inst_full, inst_map)

    chg = init_df["建议分组"].astype(str) != detail_work["建议分组"].astype(str)
    lines.append(f"因回避试算交换行数: {int(chg.sum())}")
    lines.append(f"基层组 QFD 在 A7: {a7_qfd} 条（✅ 全部正确）")
    lines.append(f"输出: {OUTPUT.name}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    summary = build_summary(detail_work, v2_sum)

    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as w:
        detail_work.to_excel(w, sheet_name="分组明细", index=False)
        summary.to_excel(w, sheet_name="分组汇总", index=False)
        gap_df.to_excel(w, sheet_name="差距说明", index=False)

    import sys
    sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8", errors="replace"))
    if final_n != 0:
        raise SystemExit(f"仍存在 {final_n} 条回避冲突！")


if __name__ == "__main__":
    main()
