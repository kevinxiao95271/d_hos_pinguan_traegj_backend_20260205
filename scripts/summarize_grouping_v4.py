# -*- coding: utf-8 -*-
"""
根据 grouping_v4.xlsx + 4.13 书审名单 + 专家数据含机构ID0410.csv
生成分组验算总结：scripts/grouping_v4_summary.txt
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "grouping_v4_summary.txt"


def resolve_shushen() -> Path:
    for g in ("*书审*名单*4.13*.xlsx", "*书审*名单*.xlsx"):
        found = sorted(ROOT.glob(g), key=lambda x: x.stat().st_mtime, reverse=True)
        if found:
            return found[0]
    return ROOT / "书审专家单位(1)-0410.xlsx"


def parse_shushen_groups() -> dict[str, list[tuple[str, str, str]]]:
    p = resolve_shushen()
    xl = pd.ExcelFile(p)
    df = pd.read_excel(p, sheet_name=xl.sheet_names[0], header=None)
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    current = None
    for i in range(len(df)):
        row = df.iloc[i]
        g = row[0]
        if pd.notna(g) and str(g).strip():
            current = str(g).strip()
        if current is None or current == "组别":
            continue
        expert = row[3]
        unit = row[5] if len(row) > 5 else ""
        phone_raw = row[7] if len(row) > 7 else ""
        if pd.isna(expert) or str(expert).strip() in ("", "专家"):
            continue
        name = str(expert).strip()
        u = "" if pd.isna(unit) else str(unit).strip()
        pr = "" if pd.isna(phone_raw) else str(phone_raw).strip()
        groups[current].append((name, u, pr))
    return dict(groups)


def load_expert_lookup():
    p = ROOT / "专家数据含机构ID0410.csv"
    df = pd.read_csv(p, encoding="utf-8-sig")
    phone_map: dict[str, tuple[str, str, str]] = {}
    name_counts: dict[str, int] = defaultdict(int)
    for _, r in df.iterrows():
        name = str(r["name"]).strip()
        name_counts[name] += 1
        phone = re.sub(r"\D", "", str(r.get("phone", "")))
        iname = str(r["institution_name"]).strip()
        iid = int(r["institution_id"])
        title = str(r.get("title", "") or "").strip()
        if phone:
            phone_map[phone] = (name, iname, title)
    unique_name: dict[str, tuple[str, str, str]] = {}
    for _, r in df.iterrows():
        name = str(r["name"]).strip()
        if name_counts[name] != 1:
            continue
        unique_name[name] = (
            str(r["institution_name"]).strip(),
            str(r.get("title", "") or "").strip(),
        )

    def resolve(name: str, phone_raw: str) -> tuple[str, str, str] | None:
        pn = re.sub(r"\D", "", phone_raw)
        if pn and pn in phone_map:
            n, inst, tit = phone_map[pn]
            return (n, inst, tit)
        base = re.split(r"[（(]", name)[0].strip()
        if base in unique_name:
            inst, tit = unique_name[base]
            return (base, inst, tit)
        if name in unique_name:
            inst, tit = unique_name[name]
            return (name, inst, tit)
        return None

    return resolve


def main():
    detail = pd.read_excel(ROOT / "grouping_v4.xlsx", sheet_name="分组明细")
    groups_raw = parse_shushen_groups()
    resolve_expert = load_expert_lookup()

    lines: list[str] = []
    lines.append("=== 浙江省医院品管大赛 · 分组验算总结（基于 grouping_v4.xlsx）")
    lines.append(f"书审名单: {resolve_shushen().name}")
    lines.append("")

    comp_order = ("基层组", "综合组", "进阶组")
    def _gkey_sort(x) -> tuple:
        m = re.match(r"^([A-Z])(\d+)$", str(x).strip())
        return (m.group(1), int(m.group(2))) if m else (str(x), 0)

    lines.append("=== 一、按竞赛大类汇总（项目条数）")
    for comp in comp_order:
        sub = detail[detail["竞赛组别"] == comp]
        lines.append(f"  {comp}: {len(sub)} 条")
    lines.append(f"  合计: {len(detail)} 条")
    lines.append("")

    lines.append("=== 二、各大类下按「建议分组」项目数")

    for comp in comp_order:
        sub = detail[detail["竞赛组别"] == comp]
        vc = sub["建议分组"].value_counts()
        keys = sorted(vc.index, key=_gkey_sort)
        lines.append(f"【{comp}】")
        for g in keys:
            lines.append(f"  {g}: {int(vc[g])} 条")
        lines.append("")

    lines.append("=== 三、各建议分组：书审专家（及机构）+ 该组报名项目涉及机构")
    lines.append("（专家机构以 专家数据含机构ID0410.csv 为准；书审名单仅定人选与组别）")
    lines.append("")

    pairs = detail.groupby(["竞赛组别", "建议分组"], as_index=False).agg(项目数=("项目编号", "count"))
    comp_ord = {"基层组": 0, "综合组": 1, "进阶组": 2}
    pairs["__co"] = pairs["竞赛组别"].map(lambda x: comp_ord.get(str(x).strip(), 9))
    pairs["__g2"] = pairs["建议分组"].map(lambda x: _gkey_sort(x)[1])
    pairs["__g1"] = pairs["建议分组"].map(lambda x: _gkey_sort(x)[0])
    pairs = pairs.sort_values(by=["__co", "__g1", "__g2"]).drop(columns=["__co", "__g1", "__g2"])

    for _, row in pairs.iterrows():
        comp = str(row["竞赛组别"]).strip()
        gc = str(row["建议分组"]).strip()
        nproj = int(row["项目数"])
        sub = detail[(detail["竞赛组别"] == comp) & (detail["建议分组"] == gc)]
        insts = sorted(sub["机构名称"].astype(str).str.strip().unique().tolist())

        lines.append("─" * 60)
        lines.append(f"【{comp} · {gc}】 项目数: {nproj}")
        lines.append("")
        lines.append("  ■ 书审专家（名单顺序）及所属机构（CSV）:")
        experts = groups_raw.get(gc, [])
        if not experts:
            lines.append("      （书审表中未找到该组别，请核对名单文件）")
        for name, raw_unit, phone in experts:
            info = resolve_expert(name, phone)
            pn = re.sub(r"\D", "", phone)
            if info:
                n2, inst, tit = info[0], info[1], info[2]
                tit_s = f" / {tit}" if tit else ""
                lines.append(f"      · {name}  {pn}  →  {inst}{tit_s}")
            else:
                lines.append(f"      · {name}  {pn}  （CSV 未匹配，书审单位: {raw_unit}）")

        lines.append("")
        lines.append(f"  ■ 该组报名项目涉及机构（去重，共 {len(insts)} 家）:")
        for ins in insts:
            cnt = (sub["机构名称"].astype(str).str.strip() == ins).sum()
            lines.append(f"      · {ins}  （{cnt} 项）")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
