import pymysql, requests, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'
COMPETITION_ID = 1

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

print('='*60)
print('【1】竞赛基本信息 & 时间配置')
cur.execute("SHOW COLUMNS FROM competitions")
comp_cols = [r[0] for r in cur.fetchall()]
print('  competitions 字段:', ', '.join(comp_cols))
cur.execute("SELECT * FROM competitions WHERE id=%s", (COMPETITION_ID,))
row = cur.fetchone()
if row:
    row_dict = dict(zip(comp_cols, row))
    print(f'  id={row_dict.get("id")}  name={str(row_dict.get("name",""))[:20]}')
    for k in comp_cols:
        if 'time' in k.lower() or 'start' in k.lower() or 'end' in k.lower() or 'date' in k.lower() or 'status' in k.lower():
            print(f'  {k} = {row_dict.get(k)}')
else:
    print('  !! 未找到竞赛记录')

print()
print('='*60)
print('【2】报名数据')
cur.execute("SELECT group_type, COUNT(*) FROM registrations WHERE competition_id=%s GROUP BY group_type", (COMPETITION_ID,))
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} 条报名')

print()
print('='*60)
print('【3】评审任务分布')
cur.execute("""
    SELECT rt.stage, rt.status, COUNT(*) cnt
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    WHERE r.competition_id = %s
    GROUP BY rt.stage, rt.status ORDER BY rt.stage, rt.status
""", (COMPETITION_ID,))
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f'  stage={r[0]}  status={r[1]}  count={r[2]}')
else:
    print('  !! 无评审任务')

print()
print('='*60)
print('【4】评分数据')
cur.execute("""
    SELECT COUNT(*) FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    JOIN registrations r ON rt.registration_id = r.id
    WHERE r.competition_id = %s
""", (COMPETITION_ID,))
book_cnt = cur.fetchone()[0]
print(f'  书审打分(review_scores): {book_cnt} 条')

cur.execute("SHOW TABLES LIKE 'interview_scores'")
if cur.fetchone():
    cur.execute("""
        SELECT COUNT(*) FROM interview_scores ins
        JOIN review_tasks rt ON ins.review_task_id = rt.id
        JOIN registrations r ON rt.registration_id = r.id
        WHERE r.competition_id = %s
    """, (COMPETITION_ID,))
    int_cnt = cur.fetchone()[0]
    print(f'  面谈打分(interview_scores): {int_cnt} 条')
else:
    print('  !! interview_scores 表不存在')

print()
print('='*60)
print('【5】快照数据')
cur.execute("""
    SELECT stage, group_type, COUNT(*) FROM scoring_snapshots
    WHERE competition_id=%s GROUP BY stage, group_type
""", (COMPETITION_ID,))
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f'  stage={r[0]}  group={r[1]}  count={r[2]}')
else:
    print('  无快照数据')


print()
print('='*60)
print('【7】分析：书审/面谈得分页面为何无数据')
for stage_name in ['BOOK', 'INTERVIEW']:
    cur.execute("""
        SELECT COUNT(*) FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE r.competition_id=%s AND rt.stage=%s
    """, (COMPETITION_ID, stage_name))
    total = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE r.competition_id=%s AND rt.stage=%s AND rt.status='SCORED'
    """, (COMPETITION_ID, stage_name))
    scored = cur.fetchone()[0]
    print(f'  {stage_name} 任务总数: {total}   已打分: {scored}')

conn.close()
