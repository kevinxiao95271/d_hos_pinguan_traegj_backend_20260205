import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT rt.stage, rt.status, COUNT(*)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
    GROUP BY rt.stage, rt.status
    ORDER BY rt.stage, rt.status
""")
print('review_tasks 阶段+状态分布:')
for row in cur.fetchall():
    print(f'  {row[0]} | {row[1]}: {row[2]}')

cur.execute("SELECT COUNT(*) FROM review_scores")
print(f'\nreview_scores 总数: {cur.fetchone()[0]}')

cur.execute("SELECT COUNT(*) FROM interview_scores")
print(f'interview_scores 总数: {cur.fetchone()[0]}')

cur.execute("""
    SELECT COUNT(DISTINCT rt.registration_id)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id=1 AND rt.stage='BOOK'
""")
print(f'\nBOOK 阶段参赛项目数: {cur.fetchone()[0]}')

cur.execute("""
    SELECT COUNT(DISTINCT rt.registration_id)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id=1 AND rt.stage='INTERVIEW'
""")
print(f'INTERVIEW 阶段参赛项目数: {cur.fetchone()[0]}')

cur.execute("SELECT group_type, COUNT(*) FROM registrations WHERE competition_id=1 GROUP BY group_type")
print('\n报名项目组别分布:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# PENDING/RETURNED 任务列表（可用来补打分）
cur.execute("""
    SELECT rt.id, rt.stage, rt.status, rt.reviewer_id, rt.registration_id
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id=1 AND rt.status IN ('PENDING','RETURNED')
    ORDER BY rt.stage, rt.id
    LIMIT 10
""")
print('\nPENDING/RETURNED 任务样例（最多10条）:')
for row in cur.fetchall():
    print(f'  task_id={row[0]} stage={row[1]} status={row[2]} reviewer_id={row[3]} reg_id={row[4]}')

conn.close()
