# -*- coding: utf-8 -*-
"""
对比：
1) 书审专家名单-4.13.xlsx（终稿） vs 书审专家单位(1)-0410.xlsx
2) 4.13 名单 vs 专家数据含机构ID0410.csv（生产对齐用主数据）

输出：scripts/shushen_413_report.txt
"""
from __future__ import annotations

import re
from pathlib import Path
from collections import defaultdict

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("shushen_413_report.txt")


def parse_sheet(path: Path, sheet: int | str = 0) -> list[tuple[str, str, str, str, str]]:
    """返回 [(组别, 姓名, 专业, 单位, 电话), ...]"""
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    rows: list[tuple[str, str, str, str, str]] = []
    current = None
    for i in range(len(df)):
        r = df.iloc[i]
        g = r[0]
        if pd.notna(g) and str(g).strip():
            current = str(g).strip()
        if current is None or current == "组别":
            continue
        name = r[3]
        if pd.isna(name) or str(name).strip() in ("", "专家"):
            continue
        spec = "" if pd.isna(r[4]) else str(r[4]).strip()
        unit = "" if pd.isna(r[5]) else str(r[5]).strip()
        phone = r[7] if len(r) > 7 else ""
        phone_s = "" if pd.isna(phone) else re.sub(r"\D", "", str(phone))
        rows.append((current, str(name).strip(), spec, unit, phone_s))
    return rows


def main():
    p413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"), None)
    p0410 = ROOT / "书审专家单位(1)-0410.xlsx"
    if not p413:
        raise SystemExit("未找到 *书审*名单*4.13*.xlsx")
    xl413 = pd.ExcelFile(p413)
    sheet413 = xl413.sheet_names[0]

    new_rows = parse_sheet(p413, sheet413)
    old_rows = parse_sheet(p0410, 0)

    def key_phone(r):
        return r[4] if r[4] else f"NOPHONE:{r[1]}"

    old_by_phone = {key_phone(r): r for r in old_rows}
    new_by_phone = {key_phone(r): r for r in new_rows}

    old_phones = set(old_by_phone.keys()) - {k for k in old_by_phone if k.startswith("NOPHONE")}
    new_phones = set(new_by_phone.keys()) - {k for k in new_by_phone if k.startswith("NOPHONE")}

    removed = old_phones - new_phones
    added = new_phones - old_phones

    lines: list[str] = []
    lines.append("=== 文件")
    lines.append(f"新名单: {p413.name} / sheet={sheet413!r}")
    lines.append(f"旧名单: {p0410.name}")
    lines.append(f"专家主数据: 专家数据含机构ID0410.csv")
    lines.append("")
    lines.append(f"新名单专家人数（去重手机号）: {len(new_phones)}")
    lines.append(f"旧名单专家人数（去重手机号）: {len(old_phones)}")
    lines.append("")

    lines.append("=== 相对旧名单(0410) 不再参加（手机在新名单中不存在）")
    for ph in sorted(removed):
        r = old_by_phone[ph]
        lines.append(f"  {r[1]}  {ph}  组{r[0]}  {r[3]}")
    if not removed:
        lines.append("  （无）")
    lines.append("")

    lines.append("=== 相对旧名单 新增专家（手机在旧名单不存在）")
    for ph in sorted(added):
        r = new_by_phone[ph]
        lines.append(f"  {r[1]}  {ph}  组{r[0]}  {r[3]}")
    if not added:
        lines.append("  （无）")
    lines.append("")

    # 同手机但组别/单位变化
    lines.append("=== 同手机号但组别或单位变化")
    common = old_phones & new_phones
    nchg = 0
    for ph in sorted(common):
        o, n = old_by_phone[ph], new_by_phone[ph]
        if o[0] != n[0] or o[3] != n[3]:
            nchg += 1
            lines.append(f"  {n[1]} {ph}")
            if o[0] != n[0]:
                lines.append(f"    组别: {o[0]} -> {n[0]}")
            if o[3] != n[3]:
                lines.append(f"    单位: {o[3]} -> {n[3]}")
    if nchg == 0:
        lines.append("  （无）")
    lines.append("")

    # CSV
    csvp = ROOT / "专家数据含机构ID0410.csv"
    exp = pd.read_csv(csvp, encoding="utf-8-sig")
    exp["phone_n"] = exp["phone"].astype(str).map(lambda x: re.sub(r"\D", "", x))
    csv_phones = set(exp["phone_n"]) - {""}

    lines.append("=== 4.13 名单 vs 专家数据含机构ID0410.csv（生产账号主数据对齐）")
    lines.append("说明：CSV 含「全库专家」，不等同于书审名单；下面只列与书审直接相关的对照。")
    lines.append("")

    missing_in_csv = []
    for ph in sorted(new_phones):
        if ph not in csv_phones:
            r = new_by_phone[ph]
            missing_in_csv.append((r[0], r[1], ph, r[3]))

    lines.append(f"[补录] 在 4.13 书审名单中、但 CSV 无该手机号（生产需新建或核对）: {len(missing_in_csv)} 人")
    for g, name, ph, unit in missing_in_csv:
        lines.append(f"  [{g}] {name}  {ph}  {unit}")
    lines.append("")

    # 曾在旧书审名单、CSV 里也有号、但 4.13 已不在 → 可能不再参加本书审（生产可调整 reviewer_group_code / 备注）
    old_in_csv = old_phones & csv_phones
    left_book_review = sorted(old_in_csv - new_phones)
    lines.append(
        f"[退出书审?] 在旧名单(0410)中且 CSV 有账号，但 4.13 名单中已无该手机: {len(left_book_review)} 人"
    )
    for ph in left_book_review:
        r = old_by_phone[ph]
        hit = exp[exp["phone_n"] == ph].iloc[0]
        lines.append(
            f"  {hit['name']}  {ph}  旧组{r[0]}  CSV机构:{hit['institution_name']}"
        )
    lines.append("")

    # 新增到 4.13、CSV 里本来就有 → 仅组别变化，生产一般只需确认 reviewer_group_code
    new_in_csv = sorted((new_phones & csv_phones) - old_phones)
    lines.append(f"[新增于终稿且 CSV 已有号] {len(new_in_csv)} 人（核对生产 reviewer_group_code 是否与终稿组别一致）")
    for ph in new_in_csv[:40]:
        r = new_by_phone[ph]
        hit = exp[exp["phone_n"] == ph].iloc[0]
        lines.append(f"  {hit['name']}  {ph}  新组{r[0]}  {hit['institution_name']}")
    if len(new_in_csv) > 40:
        lines.append(f"  ... 共 {len(new_in_csv)}")

    text = "\n".join(lines)
    OUT.write_text(text, encoding="utf-8")
    print(text)
    print("\n全文:", OUT)


if __name__ == "__main__":
    main()
