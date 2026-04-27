# -*- coding: utf-8 -*-
"""
试算分组：以「书审专家单位」各组专家所属机构（对齐 专家数据含机构ID0410.csv）与项目机构比对，
检测机构回避冲突；在同竞赛组别内尝试两两交换建议分组以降低冲突。

输出：控制台摘要 + scripts/trial_grouping_report.txt
"""
from __future__ import annotations

import re
from pathlib import Path
from collections import defaultdict

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("trial_grouping_report.txt")


def resolve_shushen_excel() -> Path:
    """优先使用最新「书审专家名单-*.*.xlsx」终稿，否则回退 书审专家单位(1)-0410.xlsx。"""
    for g in ("*书审*名单*4.13*.xlsx", "*书审*名单*.xlsx"):
        found = sorted(ROOT.glob(g), key=lambda x: x.stat().st_mtime, reverse=True)
        if found:
            return found[0]
    return ROOT / "书审专家单位(1)-0410.xlsx"


def load_expert_lookup() -> tuple[dict[str, tuple[int, str]], dict[str, tuple[int, str]], list[str]]:
    """phone(纯数字) -> (inst_id, inst_name); 仅重名时唯一条目 name -> inst。返回 (phone_map, unique_name_map, 重名列表)"""
    p = ROOT / "专家数据含机构ID0410.csv"
    df = pd.read_csv(p, encoding="utf-8-sig")
    phone_map: dict[str, tuple[int, str]] = {}
    name_counts: dict[str, int] = defaultdict(int)
    rows: list[tuple[str, str, int, str]] = []
    for _, r in df.iterrows():
        name = str(r["name"]).strip()
        phone = re.sub(r"\D", "", str(r.get("phone", "")))
        iid = int(r["institution_id"])
        iname = str(r["institution_name"]).strip()
        rows.append((name, phone, iid, iname))
        name_counts[name] += 1
        if phone:
            phone_map[phone] = (iid, iname)
    unique_name: dict[str, tuple[int, str]] = {}
    dup_names = [n for n, c in name_counts.items() if c > 1]
    for name, phone, iid, iname in rows:
        if name_counts[name] == 1:
            unique_name[name] = (iid, iname)
    return phone_map, unique_name, dup_names


def load_inst_name_to_id() -> dict[str, int]:
    p = ROOT / "机构全表0410.csv"
    df = pd.read_csv(p, encoding="utf-8-sig")
    m: dict[str, int] = {}
    for _, r in df.iterrows():
        n = str(r["name"]).strip()
        iid = int(r["id"])
        if n in m and m[n] != iid:
            # 重名机构：保留首次，后续记别名
            pass
        m.setdefault(n, iid)
    return m


def parse_shushen_groups() -> dict[str, list[tuple[str, str, str]]]:
    """书审表：组别 -> [(专家姓名, 原始单位, 联系电话原始字符串), ...]"""
    p = resolve_shushen_excel()
    xl = pd.ExcelFile(p)
    df = pd.read_excel(p, sheet_name=xl.sheet_names[0], header=None)
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    current = None
    for i in range(len(df)):
        row = df.iloc[i]
        g = row[0]
        if pd.notna(g) and str(g).strip():
            current = str(g).strip()
        if current is None:
            continue
        expert = row[3]
        unit = row[5] if len(row) > 5 else ""
        phone_raw = row[7] if len(row) > 7 else ""
        if pd.isna(expert) or str(expert).strip() == "" or str(expert).strip() == "专家":
            continue
        name = str(expert).strip()
        if name == "专家" or current in ("组别",):
            continue
        u = "" if pd.isna(unit) else str(unit).strip()
        pr = "" if pd.isna(phone_raw) else str(phone_raw).strip()
        groups[current].append((name, u, pr))
    return dict(groups)


def resolve_expert_institutions(
    groups: dict[str, list[tuple[str, str, str]]],
    phone_map: dict[str, tuple[int, str]],
    unique_name: dict[str, tuple[int, str]],
) -> tuple[dict[str, set[int]], list[str]]:
    """组别 -> 专家 institution_id 集合；无法解析的告警"""
    by_group: dict[str, set[int]] = {}
    warnings: list[str] = []
    for g, pairs in groups.items():
        ids: set[int] = set()
        for name, raw_unit, phone_raw in pairs:
            base = re.split(r"[（(]", name)[0].strip()
            pn = re.sub(r"\D", "", phone_raw)
            resolved = None
            if pn and pn in phone_map:
                resolved = phone_map[pn][0]
            elif base in unique_name:
                resolved = unique_name[base][0]
            elif name in unique_name:
                resolved = unique_name[name][0]
            if resolved is not None:
                ids.add(resolved)
            else:
                warnings.append(
                    f"专家未匹配CSV(请用手机号或消歧重名): 组别={g} name={name!r} phone={phone_raw!r} 单位={raw_unit!r}"
                )
        by_group[g] = ids
    return by_group, warnings


def project_inst_id(inst_name: str, inst_map: dict[str, int]) -> int | None:
    n = str(inst_name).strip()
    if n in inst_map:
        return inst_map[n]
    # 宽松：去空格
    for k, v in inst_map.items():
        if k.replace(" ", "") == n.replace(" ", ""):
            return v
    return None


def conflict_rows(
    detail: pd.DataFrame,
    expert_inst: dict[str, set[int]],
    inst_map: dict[str, int],
    comp: str,
) -> list[tuple[int, str, str, int | None, set[int]]]:
    """返回回避冲突行 (行索引, 项目编号, 建议分组, 项目inst_id, 该组专家inst集合)"""
    d = detail[detail["竞赛组别"] == comp].copy()
    out = []
    for idx, r in d.iterrows():
        gc = str(r["建议分组"]).strip()
        pid = str(r["项目编号"]).strip()
        iname = str(r["机构名称"]).strip()
        pi = project_inst_id(iname, inst_map)
        ex = expert_inst.get(gc, set())
        if pi is None:
            continue
        if pi in ex:
            out.append((idx, pid, gc, pi, ex))
    return out


def unmapped_inst_rows(detail: pd.DataFrame, inst_map: dict[str, int], comp: str) -> list[str]:
    out = []
    d = detail[detail["竞赛组别"] == comp]
    for _, r in d.iterrows():
        iname = str(r["机构名称"]).strip()
        if project_inst_id(iname, inst_map) is None:
            out.append(iname)
    return sorted(set(out))


def count_conflicts(
    detail: pd.DataFrame,
    expert_inst: dict[str, set[int]],
    inst_map: dict[str, int],
    comp: str,
) -> int:
    n = 0
    d = detail[detail["竞赛组别"] == comp]
    for _, r in d.iterrows():
        gc = str(r["建议分组"]).strip()
        pi = project_inst_id(str(r["机构名称"]).strip(), inst_map)
        if pi is None:
            continue
        if pi in expert_inst.get(gc, set()):
            n += 1
    return n


def try_improve_swaps(
    detail: pd.DataFrame,
    expert_inst: dict[str, set[int]],
    inst_map: dict[str, int],
    comp: str,
):
    """同竞赛组别内，交换两项目的建议分组若降低冲突则接受；多轮直至无改进。"""
    df = detail.copy()
    mask = df["竞赛组别"] == comp
    idx_list = df.index[mask].tolist()

    def conflicts_for_index(iix) -> int:
        r = df.loc[iix]
        gc = str(r["建议分组"]).strip()
        pi = project_inst_id(str(r["机构名称"]).strip(), inst_map)
        if pi is None:
            return 0
        return 1 if pi in expert_inst.get(gc, set()) else 0

    total_before = sum(conflicts_for_index(i) for i in idx_list)

    improved = True
    rounds = 0
    # 仅当存在冲突行时，用「冲突行 × 全体」尝试交换，避免 O(n²) 全量两两在综合组上过慢
    while improved and rounds < 500:
        improved = False
        rounds += 1
        conflict_idx = [i for i in idx_list if conflicts_for_index(i)]
        if not conflict_idx:
            break
        best_delta = 0
        best_pair = None
        for ia in conflict_idx:
            for ib in idx_list:
                if ia == ib:
                    continue
                g1 = str(df.at[ia, "建议分组"]).strip()
                g2 = str(df.at[ib, "建议分组"]).strip()
                if g1 == g2:
                    continue
                before = conflicts_for_index(ia) + conflicts_for_index(ib)
                df.at[ia, "建议分组"] = g2
                df.at[ib, "建议分组"] = g1
                after = conflicts_for_index(ia) + conflicts_for_index(ib)
                df.at[ia, "建议分组"] = g1
                df.at[ib, "建议分组"] = g2
                delta = before - after
                if delta > best_delta:
                    best_delta = delta
                    best_pair = (ia, ib)
        if best_delta > 0 and best_pair:
            ia, ib = best_pair
            g1 = str(df.at[ia, "建议分组"]).strip()
            g2 = str(df.at[ib, "建议分组"]).strip()
            df.at[ia, "建议分组"] = g2
            df.at[ib, "建议分组"] = g1
            improved = True

    total_after = sum(conflicts_for_index(i) for i in idx_list)
    return df, total_before, total_after, rounds


def find_conflict_marker_column(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "冲突" in str(c):
            return str(c)
    return None


def sync_conflict_marker_column(
    detail: pd.DataFrame,
    expert_inst: dict[str, set[int]],
    inst_map: dict[str, int],
) -> pd.DataFrame:
    """按「项目机构∈该书审组专家机构」重算 K 列（⚠️冲突），与试算逻辑一致。"""
    out = detail.copy()
    col = find_conflict_marker_column(out)
    if col is None:
        return out
    for idx in out.index:
        r = out.loc[idx]
        gc = str(r["建议分组"]).strip()
        pi = project_inst_id(str(r["机构名称"]).strip(), inst_map)
        if pi is not None and pi in expert_inst.get(gc, set()):
            out.at[idx, col] = "⚠️冲突"
        else:
            out.at[idx, col] = pd.NA
    return out


def main():
    lines: list[str] = []
    phone_map, unique_name, dup_names = load_expert_lookup()
    inst_map = load_inst_name_to_id()
    groups_raw = parse_shushen_groups()
    expert_inst, warn = resolve_expert_institutions(groups_raw, phone_map, unique_name)

    id_to_name: dict[int, str] = {}
    for _n, (iid, iname) in unique_name.items():
        id_to_name.setdefault(iid, iname)
    for _p, (iid, iname) in phone_map.items():
        id_to_name.setdefault(iid, iname)
    lines.append("=== 书审组别 -> 专家 institution_id（来自专家数据含机构ID0410.csv）")
    def _gk(x: str):
        m = re.match(r"^([A-Z])(\d+)$", x)
        return (m.group(1), int(m.group(2))) if m else (x, 0)

    for g in sorted(expert_inst.keys(), key=_gk):
        ids = expert_inst[g]
        detail_n = [f"{i}:{id_to_name.get(i, '?')}" for i in sorted(ids)]
        lines.append(f"  {g}: {', '.join(detail_n)}")

    if dup_names:
        lines.append("\n=== CSV 内重名专家（已改用手机号优先匹配）: " + ", ".join(dup_names))

    if warn:
        lines.append("\n=== 未匹配专家")
        for w in warn:
            lines.append("  " + w)

    gv = ROOT / "grouping_v2.xlsx"
    detail_orig = pd.read_excel(gv, sheet_name="分组明细")

    missing_inst = []
    for _, r in detail_orig.iterrows():
        iname = str(r["机构名称"]).strip()
        if project_inst_id(iname, inst_map) is None:
            missing_inst.append(iname)
    if missing_inst:
        uniq = sorted(set(missing_inst))
        lines.append(f"\n=== 项目机构名未在机构全表0410 命中: {len(uniq)} 个")
        for u in uniq[:40]:
            lines.append("  " + u)
        if len(uniq) > 40:
            lines.append(f"  ... 共 {len(uniq)}")

    detail_work = detail_orig.copy()
    for comp in ("基层组", "综合组", "进阶组"):
        lines.append(f"\n========== {comp} ==========")
        um = unmapped_inst_rows(detail_work, inst_map, comp)
        if um:
            lines.append(f"机构名未映射条数涉及机构样例: {len(um)} 个不同名称")

        cr = conflict_rows(detail_work, expert_inst, inst_map, comp)
        lines.append(f"回避冲突条数（项目机构∈该书审组专家机构）: {len(cr)}")
        for item in cr[:50]:
            _, pid, gc, pi, _ = item
            lines.append(f"  项目 {pid} 建议分组 {gc} 项目inst_id={pi}")
        if len(cr) > 50:
            lines.append(f"  ... 共 {len(cr)}")

        df2, tb, ta, rounds = try_improve_swaps(detail_work, expert_inst, inst_map, comp)
        lines.append(f"\n两两交换试算: 冲突 {tb} -> {ta} , 贪心轮次 {rounds}")
        detail_work = df2

    detail_work = sync_conflict_marker_column(detail_work, expert_inst, inst_map)

    lines.append("\n=== 试算后仍存在的回避冲突")
    for comp in ("基层组", "综合组", "进阶组"):
        cr = conflict_rows(detail_work, expert_inst, inst_map, comp)
        lines.append(f"{comp}: {len(cr)}")
        for item in cr[:40]:
            _, pid, gc, pi, _ = item
            lines.append(f"  {pid} 建议分组={gc} inst_id={pi}")

    chg = []
    for col in ["建议分组"]:
        o = detail_orig[col].astype(str).str.strip()
        n = detail_work[col].astype(str).str.strip()
        mask = o != n
        for i in detail_orig.index[mask]:
            chg.append(
                (
                    str(detail_orig.at[i, "项目编号"]).strip(),
                    str(detail_orig.at[i, "竞赛组别"]).strip(),
                    o.loc[i],
                    n.loc[i],
                    str(detail_orig.at[i, "机构名称"]).strip(),
                )
            )
    lines.append("\n=== 相对 grouping_v2 变更建议分组的项目（试算交换产生）")
    lines.append(f"共 {len(chg)} 条")
    for pid, comp, g0, g1, inst in chg[:80]:
        lines.append(f"  {pid} {comp}: {g0} -> {g1}  [{inst}]")
    if len(chg) > 80:
        lines.append(f"  ... 共 {len(chg)}")

    out_xlsx = ROOT / "scripts" / "trial_grouping_result.xlsx"
    detail_work.to_excel(out_xlsx, index=False)
    lines.append(f"\n试算明细已写: {out_xlsx.name}（相对 scripts/）")

    text = "\n".join(lines)
    OUT.write_text(text, encoding="utf-8")
    print(text[:12000])
    if len(text) > 12000:
        print("\n...(截断，全文见)", OUT)


if __name__ == "__main__":
    main()
