# -*- coding: utf-8 -*-
"""
对比「生产库快照 CSV」与「4.13 书审名单」，只输出真正需要变更的 SQL。

生产库快照 = 专家数据含机构ID0410.csv
   列: id, name, phone, institution_id, institution_name, title,
       reviewer_group_code (若有) …

4.13 名单  = 书审终稿（唯一权威：谁参加、分哪组）
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ─── 1. 读生产库快照 CSV ─────────────────────────────────────────────────────
csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_df.columns = [c.strip() for c in csv_df.columns]

# phone → row dict（主键用手机号）
prod: dict[str, dict] = {}
for _, r in csv_df.iterrows():
    pn = re.sub(r"\D", "", str(r.get("phone", "")))
    if pn:
        prod[pn] = {k: (None if pd.isna(v) else v) for k, v in r.items()}

# ─── 2. 读 4.13 名单 ─────────────────────────────────────────────────────────
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
xl    = pd.ExcelFile(p_413)
df_sh = pd.read_excel(p_413, sheet_name=xl.sheet_names[0], header=None)

experts413: list[dict] = []   # {name, phone, group_code}
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
    experts413.append({"name": str(nm).strip(), "phone": pn, "group_code": cur_gc})

# ─── 3. 已知需要修正的 institution_id（生产库错误值 → 正确值）────────────────
# 格式: phone: (当前错误值, 正确值, 机构名称)
INST_FIX = {
    "13958009748": (25, 24, "浙江大学医学院附属第二医院"),   # 李伟：25浙医四院→24浙医二院
}

# ─── 4. 差异比对 ─────────────────────────────────────────────────────────────
updates_group = []   # [(name, phone, old_gc, new_gc)]
updates_inst  = []   # [(name, phone, old_id, new_id, inst_name)]
inserts       = []   # [{name, phone, group_code, institution_id, institution_name, title}]
not_in_prod   = []   # 4.13 有、CSV 没有（需要 INSERT 或人工核查）

for e in experts413:
    pn = e["phone"]
    gc = e["group_code"]

    if pn not in prod:
        not_in_prod.append(e)
        continue

    row = prod[pn]

    # reviewer_group_code 差异
    cur_gc = str(row.get("reviewer_group_code") or "").strip()
    if cur_gc != gc:
        updates_group.append((e["name"], pn, cur_gc or "(空)", gc))

    # institution_id 修正（已知错误）
    if pn in INST_FIX:
        bad_id, good_id, iname = INST_FIX[pn]
        cur_id = int(row.get("institution_id") or 0)
        if cur_id == bad_id:
            updates_inst.append((e["name"], pn, bad_id, good_id, iname))

# 4.13 有但 CSV（生产库）无的专家 → 需要新建账号
for e in not_in_prod:
    inserts.append(e)

# ─── 5. 生成 SQL ─────────────────────────────────────────────────────────────
lines = []
lines.append("-- ==============================================================")
lines.append("-- 书审专家生产库最小变更脚本")
lines.append("-- 生成依据：专家数据含机构ID0410.csv（生产库快照）vs 4.13 名单")
lines.append(f"-- 需更新分组: {len(updates_group)} 条")
lines.append(f"-- 需修正机构: {len(updates_inst)} 条")
lines.append(f"-- 需新建账号: {len(inserts)} 条")
lines.append("-- ==============================================================")

# ── 5a. 更新 reviewer_group_code ─────────────────────────────────────────────
if updates_group:
    lines.append("")
    lines.append("-- ── A. 更新书审分组 (reviewer_group_code) ──────────────────────")
    for name, phone, old, new in updates_group:
        lines.append(f"-- {name}  {phone}  {old} → {new}")
        lines.append(
            f"UPDATE user_accounts SET reviewer_group_code = '{new}' "
            f"WHERE phone = '{phone}' AND role = 'REVIEWER';  -- {name}"
        )
else:
    lines.append("")
    lines.append("-- ── A. reviewer_group_code：无需更新（全部一致）")

# ── 5b. 修正 institution_id ───────────────────────────────────────────────────
if updates_inst:
    lines.append("")
    lines.append("-- ── B. 修正机构 institution_id ─────────────────────────────────")
    for name, phone, old_id, new_id, iname in updates_inst:
        lines.append(f"-- {name}  {phone}  institution_id: {old_id} → {new_id}  ({iname})")
        lines.append(
            f"UPDATE user_accounts SET institution_id = {new_id} "
            f"WHERE phone = '{phone}' AND role = 'REVIEWER';  -- {name}"
        )
else:
    lines.append("")
    lines.append("-- ── B. institution_id：无需修正（生产库已正确）")

# ── 5c. 新建账号 ──────────────────────────────────────────────────────────────
if inserts:
    lines.append("")
    lines.append("-- ── C. 新建评委账号（4.13 有、生产库无）────────────────────────")
    for e in inserts:
        nm  = e["name"]
        pn  = e["phone"]
        gc  = e["group_code"]
        # 尝试从 CSV 补全机构（可能 CSV 里有但手机不匹配）
        lines.append(f"-- ⚠️ {nm}  {pn}  分组: {gc}  — 生产库无此手机，需建账号")
        lines.append(f"-- 请先查询: SELECT * FROM user_accounts WHERE phone = '{pn}';")
        lines.append(
            f"INSERT IGNORE INTO user_accounts\n"
            f"    (name, phone, password, role, institution_id, enabled, reviewer_group_code, created_at)\n"
            f"VALUES\n"
            f"    ('{nm}', '{pn}', '【请填bcrypt密码】', 'REVIEWER',\n"
            f"     (SELECT id FROM institutions WHERE name LIKE '%{nm[:2]}%' LIMIT 1),\n"
            f"     1, '{gc}', NOW());\n"
            f"-- ↑ institution_id 请对照 机构全表0410.csv 人工填写正确值\n"
        )
else:
    lines.append("")
    lines.append("-- ── C. 新建账号：无需新建（所有 4.13 专家在生产库均有记录）")

# ── 5d. 验证查询 ──────────────────────────────────────────────────────────────
changed_phones = (
    [p for _, p, _, _ in updates_group]
    + [p for _, p, _, _, _ in updates_inst]
    + [e["phone"] for e in inserts]
)
if changed_phones:
    pq = ", ".join(f"'{p}'" for p in changed_phones)
    lines.append("")
    lines.append("-- ── D. 执行后验证 ───────────────────────────────────────────────")
    lines.append(f"""SELECT ua.name, ua.phone, ua.reviewer_group_code,
       ua.institution_id, i.name AS institution_name
FROM user_accounts ua
LEFT JOIN institutions i ON i.id = ua.institution_id
WHERE ua.phone IN ({pq})
ORDER BY ua.reviewer_group_code, ua.name;""")

sql_text = "\n".join(lines)
out_path = Path(__file__).with_name("sync_reviewers_prod.sql")
out_path.write_text(sql_text, encoding="utf-8")

# ── 控制台摘要 ────────────────────────────────────────────────────────────────
print(f"4.13 名单专家数   : {len(experts413)}")
print(f"需更新 group_code : {len(updates_group)}")
if updates_group:
    for name, phone, old, new in updates_group:
        print(f"  {name} {phone}  {old} -> {new}")
print(f"需修正 institution: {len(updates_inst)}")
if updates_inst:
    for name, phone, old_id, new_id, iname in updates_inst:
        print(f"  {name} {phone}  {old_id} -> {new_id}  {iname}")
print(f"需新建账号        : {len(inserts)}")
if inserts:
    for e in inserts:
        print(f"  {e['name']} {e['phone']}  {e['group_code']}")
print(f"\n输出: {out_path}")
