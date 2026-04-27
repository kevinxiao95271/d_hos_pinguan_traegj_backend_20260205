import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

print('=== 赛事 ===')
cur.execute('SELECT id, name, stage FROM competitions ORDER BY id DESC LIMIT 3')
comps = cur.fetchall()
for c in comps: print(c)

print('\n=== 书审任务(SCORED)分布 ===')
cur.execute("""
    SELECT r.group_type, r.group_code, COUNT(*) tasks, COUNT(rs.id) scored
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
    WHERE rt.stage='BOOK' AND rt.status='SCORED'
    GROUP BY r.group_type, r.group_code
    ORDER BY r.group_type, r.group_code
""")
for row in cur.fetchall(): print(row)

print('\n=== 书审分数样本(前10) ===')
cur.execute("""
    SELECT rt.id task_id, r.group_code, r.group_type, rs.total
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    JOIN review_scores rs ON rs.review_task_id = rt.id
    WHERE rt.stage='BOOK'
    ORDER BY r.group_code, rs.total
    LIMIT 10
""")
for row in cur.fetchall(): print(row)

print('\n=== scoring_snapshots ===')
cur.execute('SELECT COUNT(*) FROM scoring_snapshots')
print('总行数:', cur.fetchone()[0])

print('\n=== interview_scores ===')
cur.execute('SELECT COUNT(*) FROM interview_scores')
print('总行数:', cur.fetchone()[0])

conn.close()
