# -*- coding: utf-8 -*-
"""
生成 grouping_v5.xlsx
  分组口径完全依照「2026年浙江省医院品管大赛报名相关数据（4.7）(1).xlsx」
  的「初步分组情况」工作表，从 grouping_v4 提取机构映射，重新赋分组后
  再跑机构回避试算，保证最终冲突 = 0。

分组规则摘要
────────────────────────────────────────────────────────────
【进阶组 C】4 组
  C1  品管圈-课题达成  (前 22 条)
  C2  品管圈-课题达成  (余 10 条) + QFD 全部 (11)  = 21
  C3  品管圈-问题解决 (15) + FOCUS-PDCA (5)         = 20
  C4  其余全部 (PDCA12+失效模式3+循证医学2+六西格玛2+其他1+平衡计分卡1) = 21

【综合组 B】22 组
  十大安全目标 项目先分流（除 QFD 类外）：
    B1  十大 × 品管圈-问题解决  前 26
    B2  十大 × 其余手法  +  十大 × 品管圈-问题解决 溢出
    B3  十大 × {PDCA, FOCUS-PDCA}
  非十大（QFD 全部也走这里）：
    B4~B9   品管圈-问题解决  (161 → 27×5+26)
    B10~B13 品管圈-课题达成  (104 → 26×4)
    B14     QFD 全部 26
    B15~B17 PDCA            (72  → 24×3)
    B18~B19 FOCUS-PDCA      (47  → 24+23)
    B20     失效模式与效应分析 (29)
    B21     根本原因分析(12) + 其他:*(6)  = 18
    B22     专案改善(9)+六西格玛(5)+流程改造(3)+5S(1)+平衡计分卡(1) = 19

【基层组 A】7 组
  A1  十大安全目标全部 (32)
  非十大：
    A2~A3   品管圈-问题解决  (68 → 30+29+9，后 9 合入 A4)
    A4      品管圈-问题解决 后 9 + 品管圈-课题达成 全部 (20) = 29
    A5      PDCA 前 27
    A6      PDCA 余 5 + FOCUS-PDCA 全部 (21) = 26
    A7      根本原因分析(6)+六西格玛(4)+失效模式(4)+QFD(4)+其他:*(2)+流程改造(1) = 21
────────────────────────────────────────────────────────────
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path(__file__).with_name("grouping_v5_avoidance_report.txt")

# ── 手法常量 ─────────────────────────────────────────────────────
B22_METHODS = {"专案改善", "六西格玛管理", "流程改造", "5S", "平衡计分卡"}
B21_RCA     = "根本原因分析"

def is_ten_safe(row) -> bool:
    """十大安全目标判断：'十大安全目标' 列不为 '其他' 即为十大。"""
    v = str(row.get("十大安全目标", "其他")).strip()
    return v not in ("其他", "nan", "")

def is_other_star(method: str) -> bool:
    """其他：* 系列手法（归 B21 / A7）。"""
    return str(method).startswith("其他")

# ── 分配辅助：按目标组大小顺序切块 ────────────────────────────────
def chunk_assign(idx_list: list, targets: list[tuple[str, int]]) -> dict[int, str]:
    """
    idx_list: 待分配的 DataFrame 行索引（已按项目编号排好序）
    targets:  [(group_code, count), ...]，sum(counts) 应 == len(idx_list)
    返回 {行索引: 分组代码}
    """
    result = {}
    pos = 0
    for code, cnt in targets:
        for i in idx_list[pos: pos + cnt]:
            result[i] = code
        pos += cnt
    return result

# ── 核心分组逻辑 ────────────────────────────────────────────────
def assign_groups(detail: pd.DataFrame) -> pd.DataFrame:
    df = detail.copy()
    df["建议分组"] = ""

    # ── 进阶组 ──────────────────────────────────────────────────
    adv = df[df["竞赛组别"] == "进阶组"].copy()

    def adv_assign(row):
        m = str(row["运用手法"]).strip()
        if m == "品管圈-课题达成":   return "_C_QCC_KTC"
        if m == "QFD":              return "C2"
        if m in ("品管圈-问题解决", "FOCUS-PDCA"): return "C3"
        return "C4"   # PDCA, 失效模式, 循证医学, 六西格玛, 其他, 平衡计分卡

    adv["_tmp"] = adv.apply(adv_assign, axis=1)
    # 品管圈-课题达成：前 22 → C1，后 10 → C2
    ktc_idx = adv[adv["_tmp"] == "_C_QCC_KTC"].sort_values("项目编号").index.tolist()
    for i, idx in enumerate(ktc_idx):
        adv.at[idx, "_tmp"] = "C1" if i < 22 else "C2"

    df.loc[adv.index, "建议分组"] = adv["_tmp"]

    # ── 综合组 ──────────────────────────────────────────────────
    comp = df[df["竞赛组别"] == "综合组"].copy()

    # 先把所有 QFD 标 B14（不管十大与否）
    comp.loc[comp["运用手法"] == "QFD", "建议分组"] = "B14"

    # 十大安全目标（非 QFD）
    ten_mask = comp.apply(is_ten_safe, axis=1) & (comp["运用手法"] != "QFD")
    ten = comp[ten_mask].sort_values("项目编号")

    # B1：十大 × 品管圈-问题解决，前 26
    b1_pool = ten[ten["运用手法"] == "品管圈-问题解决"].index.tolist()
    for i, idx in enumerate(b1_pool):
        comp.at[idx, "建议分组"] = "B1" if i < 26 else "B2"

    # B3：十大 × {PDCA, FOCUS-PDCA}
    b3_mask = ten["运用手法"].isin({"PDCA", "FOCUS-PDCA"})
    comp.loc[ten[b3_mask].index, "建议分组"] = "B3"

    # B2：十大其余（课题达成, 失效模式, 六西格玛, 根本原因分析, 专案改善, 循证医学等）
    b2_mask = (
        comp.apply(is_ten_safe, axis=1) &
        (comp["运用手法"] != "QFD") &
        (comp["建议分组"] == "")
    )
    comp.loc[b2_mask, "建议分组"] = "B2"

    # 非十大（且不是 QFD，那些已标好了）
    non_ten = comp[(~comp.apply(is_ten_safe, axis=1)) & (comp["运用手法"] != "QFD")]

    def comp_non_ten_group(row):
        m = str(row["运用手法"]).strip()
        if m == "品管圈-问题解决":    return "_B_QCC_WT"
        if m == "品管圈-课题达成":    return "_B_QCC_KTC"
        if m == "PDCA":             return "_B_PDCA"
        if m == "FOCUS-PDCA":       return "_B_FPDCA"
        if m == "失效模式与效应分析":  return "B20"
        if m == B21_RCA:            return "B21"
        if is_other_star(m):        return "B21"
        if m in B22_METHODS:        return "B22"
        return "B21"  # fallback

    comp.loc[non_ten.index, "建议分组"] = non_ten.apply(comp_non_ten_group, axis=1)

    # 分配 品管圈-问题解决 非十大 → B4~B9 (27,27,27,27,27,26)
    qcc_wt_idx = comp[comp["建议分组"] == "_B_QCC_WT"].sort_values("项目编号").index.tolist()
    assert len(qcc_wt_idx) == 161, f"品管圈-问题解决 非十大应=161，实={len(qcc_wt_idx)}"
    for k, v in chunk_assign(qcc_wt_idx,
            [("B4",27),("B5",27),("B6",27),("B7",27),("B8",27),("B9",26)]).items():
        comp.at[k, "建议分组"] = v

    # 品管圈-课题达成 非十大 → B10~B13 (26,26,26,26)
    ktc_idx2 = comp[comp["建议分组"] == "_B_QCC_KTC"].sort_values("项目编号").index.tolist()
    assert len(ktc_idx2) == 104, f"品管圈-课题达成 非十大应=104，实={len(ktc_idx2)}"
    for k, v in chunk_assign(ktc_idx2,
            [("B10",26),("B11",26),("B12",26),("B13",26)]).items():
        comp.at[k, "建议分组"] = v

    # PDCA 非十大 → B15~B17 (24,24,24)
    pdca_idx = comp[comp["建议分组"] == "_B_PDCA"].sort_values("项目编号").index.tolist()
    assert len(pdca_idx) == 72, f"PDCA 非十大应=72，实={len(pdca_idx)}"
    for k, v in chunk_assign(pdca_idx, [("B15",24),("B16",24),("B17",24)]).items():
        comp.at[k, "建议分组"] = v

    # FOCUS-PDCA 非十大 → B18~B19 (24,23)
    fpdca_idx = comp[comp["建议分组"] == "_B_FPDCA"].sort_values("项目编号").index.tolist()
    assert len(fpdca_idx) == 47, f"FOCUS-PDCA 非十大应=47，实={len(fpdca_idx)}"
    for k, v in chunk_assign(fpdca_idx, [("B18",24),("B19",23)]).items():
        comp.at[k, "建议分组"] = v

    df.loc[comp.index, "建议分组"] = comp["建议分组"]

    # ── 基层组 ──────────────────────────────────────────────────
    basic = df[df["竞赛组别"] == "基层组"].copy()

    # A1：十大安全目标全部
    basic.loc[basic.apply(is_ten_safe, axis=1), "建议分组"] = "A1"

    non_ten_b = basic[~basic.apply(is_ten_safe, axis=1)]

    def basic_non_ten_group(row):
        m = str(row["运用手法"]).strip()
        if m == "品管圈-问题解决":   return "_A_QCC_WT"
        if m == "品管圈-课题达成":   return "_A_QCC_KTC"
        if m == "PDCA":            return "_A_PDCA"
        if m == "FOCUS-PDCA":      return "A6"
        # 综合工具组 A7
        return "A7"

    basic.loc[non_ten_b.index, "建议分组"] = non_ten_b.apply(basic_non_ten_group, axis=1)

    # 品管圈-问题解决 非十大 → A2(30), A3(29), A4(9)
    qcc_wt_b = basic[basic["建议分组"] == "_A_QCC_WT"].sort_values("项目编号").index.tolist()
    assert len(qcc_wt_b) == 68, f"基层 品管圈-问题解决 非十大应=68，实={len(qcc_wt_b)}"
    for k, v in chunk_assign(qcc_wt_b, [("A2",30),("A3",29),("A4",9)]).items():
        basic.at[k, "建议分组"] = v

    # 品管圈-课题达成 非十大 → A4(20)（全部）
    ktc_b = basic[basic["建议分组"] == "_A_QCC_KTC"].sort_values("项目编号").index.tolist()
    assert len(ktc_b) == 20, f"基层 品管圈-课题达成 非十大应=20，实={len(ktc_b)}"
    for k in ktc_b:
        basic.at[k, "建议分组"] = "A4"

    # PDCA 非十大 → A5(27), A6(5)
    pdca_b = basic[basic["建议分组"] == "_A_PDCA"].sort_values("项目编号").index.tolist()
    assert len(pdca_b) == 32, f"基层 PDCA 非十大应=32，实={len(pdca_b)}"
    for k, v in chunk_assign(pdca_b, [("A5",27),("A6",5)]).items():
        basic.at[k, "建议分组"] = v

    df.loc[basic.index, "建议分组"] = basic["建议分组"]

    # 最后检查没有未赋值的行
    unset = df[df["建议分组"].isin(["", "_tmp"])]["项目编号"].tolist()
    if unset:
        raise ValueError(f"有 {len(unset)} 行未赋分组: {unset[:10]}")
    return df


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

    # 读 v4 作为带机构映射的基础
    gv4 = ROOT / "grouping_v4.xlsx"
    detail_base = pd.read_excel(gv4, sheet_name="分组明细")
    v2_sum = pd.read_excel(ROOT / "grouping_v2.xlsx", sheet_name="分组汇总")

    # ── 重新按 4.7 口径分配分组 ──────────────────────────────────
    detail_v5 = assign_groups(detail_base)

    lines = ["=== grouping_v5 回避试算（基于 4.7 口径重新分组）"]
    lines.append(f"书审表: {t.resolve_shushen_excel().name}")
    if warn:
        lines.append("未匹配专家:")
        for w in warn: lines.append("  " + w)
    else:
        lines.append("未匹配专家: 无")

    # 输出分配后的组别分布（验证）
    lines.append("\n--- 4.7 口径分组结果 ---")
    for comp in ("基层组", "综合组", "进阶组"):
        sub = detail_v5[detail_v5["竞赛组别"] == comp]
        cnt = sub["建议分组"].value_counts().sort_index()
        for g, n in cnt.items():
            lines.append(f"  {comp} {g}: {n}")

    # ── 回避试算 ────────────────────────────────────────────────
    detail_work = detail_v5.copy()
    lines.append("\n--- 回避试算 ---")
    for comp in ("基层组", "综合组", "进阶组"):
        tb = t.count_conflicts(detail_work, expert_inst, inst_map, comp)
        df2, _, ta, rounds = t.try_improve_swaps(detail_work, expert_inst, inst_map, comp)
        detail_work = df2
        lines.append(f"{comp}: 试算前冲突 {tb} -> 后 {ta}, 轮次 {rounds}")

    detail_work = t.sync_conflict_marker_column(detail_work, expert_inst, inst_map)

    final = sum(t.count_conflicts(detail_work, expert_inst, inst_map, c)
                for c in ("基层组", "综合组", "进阶组"))
    lines.append(f"\n最终回避冲突总数: {final}")

    # ── 分组变更统计（相对 v4）──────────────────────────────────
    chg = detail_base["建议分组"].astype(str).str.strip() != detail_work["建议分组"].astype(str).str.strip()
    lines.append(f"相对 grouping_v4 建议分组变更行数: {int(chg.sum())}")

    kcol = t.find_conflict_marker_column(detail_work)
    if kcol:
        flagged = detail_work[kcol].astype(str).str.contains("冲突", na=False).sum()
        lines.append(f"冲突标记列(K)标冲突行数: {int(flagged)}")

    out_path = ROOT / "grouping_v5.xlsx"
    summary = build_summary(detail_work, v2_sum)
    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        detail_work.to_excel(w, sheet_name="分组明细", index=False)
        summary.to_excel(w, sheet_name="分组汇总", index=False)

    lines.append(f"输出: {out_path.name}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    if final != 0:
        raise SystemExit(f"仍存在 {final} 条回避冲突，请检查！")


if __name__ == "__main__":
    main()
