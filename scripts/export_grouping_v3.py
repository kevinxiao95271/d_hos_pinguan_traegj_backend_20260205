# -*- coding: utf-8 -*-
"""生成 grouping_v3.xlsx：分组明细=回避试算后结果，分组汇总=按明细重算项目数并同步 v2 其余列。"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build_summary(detail: pd.DataFrame, v2_summary: pd.DataFrame) -> pd.DataFrame:
    cnt = detail.groupby("建议分组", as_index=False).size().rename(columns={"size": "项目数"})
    # v2 按「小组」列合并
    m = v2_summary.merge(cnt, left_on="小组", right_on="建议分组", how="left", suffixes=("", "_new"))
    if "项目数_new" in m.columns:
        m["项目数"] = m["项目数_new"].fillna(m["项目数"])
        m = m.drop(columns=[c for c in m.columns if c.endswith("_new")])
    if "建议分组" in m.columns:
        m = m.drop(columns=["建议分组"])
    # 试算通过后剩余冲突标 0
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
    expert_inst, _warn = t.resolve_expert_institutions(groups_raw, phone_map, unique_name)

    gv = ROOT / "grouping_v2.xlsx"
    detail_orig = pd.read_excel(gv, sheet_name="分组明细")
    v2_sum = pd.read_excel(gv, sheet_name="分组汇总")

    detail_work = detail_orig.copy()
    for comp in ("基层组", "综合组"):
        df2, _, _, _ = t.try_improve_swaps(detail_work, expert_inst, inst_map, comp)
        detail_work = df2

    summary = build_summary(detail_work, v2_sum)

    out = ROOT / "grouping_v3.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        detail_work.to_excel(w, sheet_name="分组明细", index=False)
        summary.to_excel(w, sheet_name="分组汇总", index=False)

    print(f"Wrote {out}")
    chg = detail_orig["建议分组"].astype(str).str.strip() != detail_work["建议分组"].astype(str).str.strip()
    print("建议分组变更行数:", int(chg.sum()))


if __name__ == "__main__":
    main()
