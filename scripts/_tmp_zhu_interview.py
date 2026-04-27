import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 1. 找名字含'朱'的用户
print('=== 名字含[朱]的账户 ===')
cur.execute("SELECT id, name, role, username FROM user_accounts WHERE name LIKE '%朱%'")
zhus = cur.fetchall()
for r in zhus:
    print(f'  id={r[0]}  name={r[1]}  role={r[2]}  username={r[3]}')

# 2. 取其 reviewer_id，查其 review_tasks（面谈阶段）
zhu_ids = [r[0] for r in zhus]
if not zhu_ids:
    print('未找到含朱的账户，退出')
    conn.close()
    sys.exit(0)

print()
for zid in zhu_ids:
    zname = next(r[1] for r in zhus if r[0] == zid)
    print(f'=== {zname}(id={zid}) 的面谈任务 ===')
    cur.execute("""
        SELECT rt.id, rt.registration_id, rt.stage, rt.status, rt.created_at
        FROM review_tasks rt
        WHERE rt.reviewer_id = %s AND rt.stage = 'INTERVIEW'
        ORDER BY rt.created_at DESC
        LIMIT 20
    """, (zid,))
    tasks = cur.fetchall()
    if not tasks:
        print('  无面谈任务')
    for t in tasks:
        print(f'  task_id={t[0]}  reg={t[1]}  stage={t[2]}  status={t[3]}  created={t[4]}')

    # 3. 查该人提交过的 interview_scores
    print(f'\n  --- {zname} 提交的 interview_scores ---')
    cur.execute("""
        SELECT is2.id, is2.review_task_id, is2.topic, is2.process,
               is2.interview_operation, is2.result, is2.total, is2.submitted_at,
               rt.registration_id, rt.status
        FROM interview_scores is2
        JOIN review_tasks rt ON is2.review_task_id = rt.id
        WHERE rt.reviewer_id = %s
        ORDER BY is2.submitted_at DESC
    """, (zid,))
    scores = cur.fetchall()
    if not scores:
        print('  无 interview_scores 记录')
    for s in scores:
        print(f'  score_id={s[0]}  task={s[1]}  topic={s[2]}  process={s[3]}  '
              f'op={s[4]}  result={s[5]}  total={s[6]}')
        print(f'    reg={s[8]}  task_status={s[9]}  submitted={s[7]}')

# 4. 全局 interview_scores 概览
print('\n=== 全局 interview_scores 概览 ===')
cur.execute("SELECT COUNT(*) FROM interview_scores")
print(f'  总记录数: {cur.fetchone()[0]}')

cur.execute("""
    SELECT rt.stage, COUNT(*) as cnt
    FROM interview_scores is2
    JOIN review_tasks rt ON is2.review_task_id = rt.id
    GROUP BY rt.stage
""")
for r in cur.fetchall():
    print(f'  stage={r[0]}  count={r[1]}')

cur.execute("""
    SELECT is2.submitted_at IS NOT NULL as has_submit, COUNT(*) as cnt
    FROM interview_scores is2
    GROUP BY has_submit
""")
print('  submitted_at 分布:')
for r in cur.fetchall():
    print(f'    has_submitted={r[0]}  count={r[1]}')

conn.close()
print('\n分析完毕')
