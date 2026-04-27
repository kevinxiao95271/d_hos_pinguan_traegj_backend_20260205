# -*- coding: utf-8 -*-
"""
根据 grouping_final 分组 + 4.13 专家分组，生成 review_tasks INSERT SQL
每位专家对应其组内所有 SUBMITTED 项目，stage=BOOK，status=PENDING
"""
import sys, re, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

# ── 1. 读专家 phone→group_code（4.13 名单）────────────────────────────────────
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
xl    = pd.ExcelFile(p_413)
df_sh = pd.read_excel(p_413, sheet_name=xl.sheet_names[0], header=None)

experts = []   # {phone, group_code}
cur_gc = None
for i in range(len(df_sh)):
    r = df_sh.iloc[i]
    g = r[0]
    if pd.notna(g) and str(g).strip() not in ("", "nan"):
        cur_gc = str(g).strip()
    if not cur_gc: continue
    nm = r[3] if len(r) > 3 else None
    if pd.isna(nm) or str(nm).strip() in ("", "专家", "姓名", "nan"): continue
    ph_raw = r[7] if len(r) > 7 else ""
    pn = re.sub(r"\D", "", str(ph_raw)) if pd.notna(ph_raw) else ""
    if not pn: continue
    experts.append({"name": str(nm).strip(), "phone": pn, "group_code": cur_gc})

# ── 2. 读 grouping_final 分组明细 ─────────────────────────────────────────────
df_proj = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
df_proj.columns = [c.strip() for c in df_proj.columns]
# group_code → [registration_id]
grp_projs: dict[str, list[int]] = {}
for _, r in df_proj.iterrows():
    gc  = str(r["建议分组"]).strip()
    pid = int(r["项目编号"])
    grp_projs.setdefault(gc, []).append(pid)

# ── 3. 生成 SQL ───────────────────────────────────────────────────────────────
lines = []
lines.append("-- ==============================================================")
lines.append("-- 书审任务分配：review_tasks INSERT")
lines.append("-- stage=BOOK  status=PENDING")
lines.append("-- 仅对 status='SUBMITTED' 的项目生成任务")
lines.append("-- ==============================================================")
lines.append("")
lines.append("-- 先清空旧的 BOOK 阶段任务（如果是全新分配，防止重复）")
lines.append("-- DELETE FROM review_tasks WHERE stage = 'BOOK';")
lines.append("-- ↑ 如是首次分配可取消注释；如已有数据请谨慎")
lines.append("")

total = 0
cur_gc = None
for e in experts:
    gc   = e["group_code"]
    pids = grp_projs.get(gc, [])
    if not pids: continue

    if gc != cur_gc:
        lines.append(f"-- ── {gc}  专家:{e['name']}({e['phone']})  项目{len(pids)}个 ──────────────")
        cur_gc = gc
    else:
        lines.append(f"-- ── {gc}  专家:{e['name']}({e['phone']}) ──────────────")

    for pid in sorted(pids):
        lines.append(
            f"INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)"
            f"\nSELECT 'BOOK', {pid}, ua.id, 'PENDING', NOW(), NOW()"
            f"\nFROM user_accounts ua"
            f"\nJOIN registrations r ON r.id = {pid}"
            f"\nWHERE ua.phone = '{e['phone']}'"
            f"\n  AND r.status = 'SUBMITTED';"
        )
        total += 1
    lines.append("")

lines.append("-- ── 验证 ────────────────────────────────────────────────────────")
lines.append("""SELECT
    r.group_code,
    COUNT(DISTINCT rt.reviewer_id) AS reviewer_cnt,
    COUNT(DISTINCT rt.registration_id) AS project_cnt,
    COUNT(*) AS task_cnt
FROM review_tasks rt
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'BOOK'
GROUP BY r.group_code
ORDER BY r.group_code;""")

sql = "\n".join(lines)
out = Path(__file__).with_name("deploy_review_tasks_prod.sql")
out.write_text(sql, encoding="utf-8")
print(f"INSERT 语句数: {total}")
print(f"专家数: {len(experts)}")
print(f"输出: {out}")
