# -*- coding: utf-8 -*-
import sys, re, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

# 4.13 专家名单 phone→group_code
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
df_sh = pd.read_excel(p_413, sheet_name=0, header=None)
experts = []
cur_gc = None
for i in range(len(df_sh)):
    r = df_sh.iloc[i]; g = r[0]
    if pd.notna(g) and str(g).strip() not in ("","nan"): cur_gc = str(g).strip()
    if not cur_gc: continue
    nm = r[3] if len(r)>3 else None
    if pd.isna(nm) or str(nm).strip() in ("","专家","姓名","nan"): continue
    pn = re.sub(r"\D","",str(r[7])) if len(r)>7 and pd.notna(r[7]) else ""
    if not pn: continue
    experts.append({"name": str(nm).strip(), "phone": pn, "gc": cur_gc})

lines = []
lines.append("-- ==============================================================")
lines.append("-- 书审任务分配 review_tasks  (stage=BOOK, status=PENDING)")
lines.append(f"-- 共 {len(experts)} 位专家，每人对应其组内所有 SUBMITTED 项目")
lines.append("-- INSERT IGNORE 防重复执行")
lines.append("-- ==============================================================")
lines.append("")
lines.append("-- 如需重新分配，先清空：")
lines.append("-- DELETE FROM review_tasks WHERE stage = 'BOOK';")
lines.append("")

cur_gc = None
for e in experts:
    if e["gc"] != cur_gc:
        lines.append(f"-- ── {e['gc']} ───────────────────────────────────────────────")
        cur_gc = e["gc"]
    lines.append(f"-- {e['name']}  {e['phone']}")
    lines.append(
        f"INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)\n"
        f"SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()\n"
        f"FROM registrations r\n"
        f"JOIN user_accounts ua ON ua.phone = '{e['phone']}' AND ua.name = '{e['name']}'\n"
        f"WHERE r.group_code = '{e['gc']}' AND r.status = 'SUBMITTED';\n"
    )

lines.append("-- ── 验证 ─────────────────────────────────────────────────────────")
lines.append("""SELECT r.group_code,
       COUNT(DISTINCT rt.reviewer_id)     AS reviewer_cnt,
       COUNT(DISTINCT rt.registration_id) AS project_cnt,
       COUNT(*)                           AS task_cnt
FROM review_tasks rt
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'BOOK'
GROUP BY r.group_code
ORDER BY r.group_code;""")

out = Path(__file__).with_name("deploy_review_tasks_prod.sql")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"专家数: {len(experts)}  输出: {out}")
