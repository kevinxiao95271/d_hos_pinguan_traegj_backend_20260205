"""
用有材料的项目重新分配书审/面谈任务给三位测试评委
评委: 孙丽娟(id=5), 朱研究员(id=28), 朱研究员(id=29)
"""
import pymysql
from datetime import datetime

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

RV_IDS = [5, 28, 29]  # 孙丽娟, 朱研究员x2
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 取有材料的 SUBMITTED 项目（排除 RETURNED）
cur.execute('''
    SELECT r.id, r.project_name, r.group_type, r.group_code,
           COUNT(mf.id) AS mat_cnt
    FROM registrations r
    JOIN material_files mf ON mf.registration_id = r.id
    WHERE r.competition_id = 1 AND r.status = 'SUBMITTED'
    GROUP BY r.id
    ORDER BY mat_cnt DESC
''')
regs = cur.fetchall()
print(f'有材料的 SUBMITTED 项目: {len(regs)} 条')

# 清理三位评委旧的书审/面谈任务
fmt = ','.join(['%s'] * len(RV_IDS))
cur.execute(f"DELETE FROM review_tasks WHERE reviewer_id IN ({fmt}) AND stage IN ('BOOK','INTERVIEW')", RV_IDS)
conn.commit()
print(f'清理旧任务: {cur.rowcount} 条')

# ── 书审任务分配 ─────────────────────────────────────────────────────────────
# 取前6条给书审
book_regs = regs[:6]
# 孙丽娟(5): 3条（多任务）, 朱研究员(28): 3条（书审专属）, 朱研究员(29): 1条（与面谈重叠）
book_assign = []
for i, r in enumerate(book_regs):
    if i < 3:
        # 前3条给 孙丽娟 + 朱研究员(28)
        book_assign.append((r['id'], 5, now))   # 孙丽娟
        book_assign.append((r['id'], 28, now))  # 朱研究员(书审专属)
    else:
        # 后3条给 孙丽娟 + 朱研究员(29)
        book_assign.append((r['id'], 5, now))   # 孙丽娟
        book_assign.append((r['id'], 29, now))  # 朱研究员(面谈专属，但这里给1条书审做交叉)

cur.executemany("""
    INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
    VALUES ('BOOK', %s, %s, 'PENDING', %s)
""", book_assign)
conn.commit()
book_count = cur.rowcount
print(f'书审任务已分配: {book_count} 条')

# ── 面谈任务分配 ─────────────────────────────────────────────────────────────
# 取第3-7条（与书审有2条重叠）给面谈
interview_regs = regs[2:7] if len(regs) >= 7 else regs[max(0,len(regs)-5):]
# 孙丽娟(5): 3条（多任务重叠）, 朱研究员(29): 3条（面谈专属）, 朱研究员(28): 1条交叉
interview_assign = []
for i, r in enumerate(interview_regs):
    if i < 3:
        interview_assign.append((r['id'], 5, now))   # 孙丽娟（与书审重叠）
        interview_assign.append((r['id'], 29, now))  # 朱研究员(面谈专属)
    else:
        interview_assign.append((r['id'], 5, now))   # 孙丽娟
        interview_assign.append((r['id'], 28, now))  # 朱研究员(书审专属加1条面谈)

cur.executemany("""
    INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
    VALUES ('INTERVIEW', %s, %s, 'PENDING', %s)
""", interview_assign)
conn.commit()
interview_count = cur.rowcount
print(f'面谈任务已分配: {interview_count} 条')

# ── 最终汇总 ─────────────────────────────────────────────────────────────────
print('\n各评委最终任务汇总:')
labels = {5: '孙丽娟(书审+面谈重叠)', 28: '朱研究员(书审专属+1面谈)', 29: '朱研究员(面谈专属+1书审)'}
for rv_id in RV_IDS:
    cur.execute("""
        SELECT rt.stage, COUNT(*) cnt
        FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE rt.reviewer_id = %s AND rt.stage IN ('BOOK','INTERVIEW')
        GROUP BY rt.stage
    """, (rv_id,))
    rows = cur.fetchall()
    summary = {row['stage']: row['cnt'] for row in rows}
    print(f"  {labels[rv_id]}: 书审={summary.get('BOOK',0)} 面谈={summary.get('INTERVIEW',0)}")

print('\n项目-材料确认:')
all_reg_ids = list({r['id'] for r in book_regs + interview_regs})
fmt2 = ','.join(['%s'] * len(all_reg_ids))
cur.execute(f"""
    SELECT r.id, r.project_name, COUNT(mf.id) mat_cnt
    FROM registrations r
    LEFT JOIN material_files mf ON mf.registration_id = r.id
    WHERE r.id IN ({fmt2})
    GROUP BY r.id
""", all_reg_ids)
for row in cur.fetchall():
    print(f"  reg_id={row['id']} 材料={row['mat_cnt']}个 {row['project_name'][:30]}")

cur.close()
conn.close()
