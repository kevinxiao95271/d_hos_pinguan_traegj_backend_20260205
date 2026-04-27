# -*- coding: utf-8 -*-
"""
根据 grouping_final.xlsx 分组明细，生成生产库 UPDATE group_code SQL
只更新 status = 'SUBMITTED' 的项目
"""
import sys, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
df.columns = [c.strip() for c in df.columns]

print(f"分组明细总行数: {len(df)}")
print()

lines = []
lines.append("-- ==============================================================")
lines.append("-- grouping_final → 生产库 group_code 分配")
lines.append(f"-- 来源: grouping_final.xlsx 分组明细  共 {len(df)} 条")
lines.append("-- 条件: status = 'SUBMITTED'（被删除/驳回的项目自动跳过）")
lines.append("-- ==============================================================")
lines.append("")

# 按分组排序输出，方便核查
df_sorted = df.sort_values(["建议分组", "项目编号"])

cur_gc = None
for _, r in df_sorted.iterrows():
    gc  = str(r["建议分组"]).strip()
    pid = int(r["项目编号"])
    if gc != cur_gc:
        lines.append(f"-- ── {gc} ──────────────────────────────────────────────────────")
        cur_gc = gc
    lines.append(
        f"UPDATE registrations SET group_code = '{gc}' "
        f"WHERE id = {pid} AND status = 'SUBMITTED';"
    )

lines.append("")
lines.append("-- ── 验证：各组项目数 ──────────────────────────────────────────────")
lines.append("""SELECT group_code, COUNT(*) AS cnt
FROM registrations
WHERE group_code IS NOT NULL AND status = 'SUBMITTED'
GROUP BY group_code
ORDER BY group_code;""")

sql = "\n".join(lines)
out = Path(__file__).with_name("deploy_grouping_prod.sql")
out.write_text(sql, encoding="utf-8")
print(f"输出: {out}")
print(f"UPDATE 语句数: {len(df)}")
