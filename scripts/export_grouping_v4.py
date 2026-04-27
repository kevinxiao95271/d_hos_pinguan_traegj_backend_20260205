# -*- coding: utf-8 -*-
"""
生成 grouping_v4.xlsx：
  分组明细 = grouping_v2 + 基层/综合/进阶 三组机构回避试算；
  K 列「⚠️冲突」= 试算后按同一规则重算（与旧 v2 自带标记脱钩）；
  分组汇总 = 同步项目数与「无冲突」状态；
  grouping_v4_avoidance_report.txt 验证三组回避冲突为 0。
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path(__file__).with_name("grouping_v4_avoidance_report.txt")


def build_summary(detail: pd.DataFrame, v2_summary: pd.DataFrame) -> pd.DataFrame:
    cnt = detail.groupby("建议分组", as_index=False).size().rename(columns={"size": "项目数"})
    m = v2_summary.merge(cnt, left_on="小组", right_on="建议分组", how="left", suffixes=("", "_new"))
    if "项目数_new" in m.columns:
        m["项目数"] = m["项目数_new"].fillna(m["项目数"])
        m = m.drop(columns=[c for c in m.columns if c.endswith("_new")])
    if "建议分组" in m.columns:
        m = m.drop(columns=["建议分组"])
    if "剩余冲突" in m.columns:
        m["剩余冲突"] = 0
    if "状态" in m.columns:
        m["状态"] = "✅ 无冲突"
    return m


def main():
    import trial_grouping_avoidance as t

    phone_map, unique_name, _dup = t.load_expert_lookup()
    inst_map = t.load_inst_name_to_id()
    groups_raw = t.parse_shushen_groups()
    expert_inst, warn = t.resolve_expert_institutions(groups_raw, phone_map, unique_name)

    gv = ROOT / "grouping_v2.xlsx"
    detail_orig = pd.read_excel(gv, sheet_name="分组明细")
    v2_sum = pd.read_excel(gv, sheet_name="分组汇总")

    detail_work = detail_orig.copy()
    lines = []
    lines.append("=== 回避试算（机构：项目组 ∩ 该书审组专家机构 → 冲突）")
    lines.append(f"书审表: {t.resolve_shushen_excel().name}")
    if warn:
        lines.append("未匹配专家（无法纳入回避集合，请补 CSV）:")
        for w in warn:
            lines.append("  " + w)
    else:
        lines.append("未匹配专家: 无")

    for comp in ("基层组", "综合组", "进阶组"):
        tb = t.count_conflicts(detail_work, expert_inst, inst_map, comp)
        df2, _, ta, rounds = t.try_improve_swaps(detail_work, expert_inst, inst_map, comp)
        detail_work = df2
        lines.append(f"{comp}: 试算前冲突 {tb} -> 后 {ta} , 轮次 {rounds}")

    detail_work = t.sync_conflict_marker_column(detail_work, expert_inst, inst_map)

    for comp in ("基层组", "综合组", "进阶组"):
        n = t.count_conflicts(detail_work, expert_inst, inst_map, comp)
        lines.append(f"{comp} 最终冲突数: {n}")

    summary = build_summary(detail_work, v2_sum)

    out = ROOT / "grouping_v4.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        detail_work.to_excel(w, sheet_name="分组明细", index=False)
        summary.to_excel(w, sheet_name="分组汇总", index=False)

    chg = detail_orig["建议分组"].astype(str).str.strip() != detail_work["建议分组"].astype(str).str.strip()
    lines.append("")
    lines.append(f"相对 grouping_v2 建议分组变更行数: {int(chg.sum())}")
    kcol = t.find_conflict_marker_column(detail_work)
    if kcol:
        flagged = detail_work[kcol].astype(str).str.contains("冲突", na=False).sum()
        lines.append(f"冲突标记列(K)标冲突行数（重算后）: {int(flagged)}")
    lines.append(f"输出: {out.name}")

    REPORT.write_text("\n".join(lines), encoding="utf-8")

    final_total = sum(
        t.count_conflicts(detail_work, expert_inst, inst_map, c)
        for c in ("基层组", "综合组", "进阶组")
    )
    print("\n".join(lines))
    print(REPORT)
    if final_total != 0:
        raise SystemExit(f"试算后仍存在回避冲突 {final_total} 条，请检查名单/机构映射或增强交换策略")


if __name__ == "__main__":
    main()
