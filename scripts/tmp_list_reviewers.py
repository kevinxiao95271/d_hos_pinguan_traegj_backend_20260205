import pymysql, io, sys, bcrypt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT ua.id, ua.name, ua.phone,
           COUNT(rt.id) as task_cnt
    FROM user_accounts ua
    JOIN review_tasks rt ON rt.reviewer_id = ua.id AND rt.stage = 'FINAL'
    WHERE ua.role = 'REVIEWER' AND ua.enabled = 1
    GROUP BY ua.id, ua.name, ua.phone
    ORDER BY ua.id
""")
rows = cur.fetchall()

hashed = bcrypt.hashpw(b'user123', bcrypt.gensalt(rounds=10)).decode()
ids = [r[0] for r in rows]
if ids:
    placeholders = ','.join(['%s']*len(ids))
    cur.execute(f"UPDATE user_accounts SET password=%s WHERE id IN ({placeholders})", [hashed]+ids)
    conn.commit()

print(f"共 {len(rows)} 位评委，已全部重置密码为 user123\n")
for uid, name, phone, task_cnt in rows:
    print(f"{phone}  {name}  (任务{task_cnt}条)")

conn.close()
