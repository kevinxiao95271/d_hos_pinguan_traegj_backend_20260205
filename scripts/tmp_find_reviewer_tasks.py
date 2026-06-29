import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 找有 FINAL 阶段任务的评委
cur.execute("""
SELECT ua.phone, ua.name, ua.id, rt.id as task_id, rt.status, r.final_session_code, r.final_score_form
FROM review_tasks rt
JOIN user_accounts ua ON ua.id = rt.reviewer_id
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'FINAL'
LIMIT 10
""")
rows = cur.fetchall()
print("有FINAL任务的评委:")
for r in rows:
    print(r)

# SCORED 状态
cur.execute("""
SELECT rt.id, ua.phone, ua.name, rt.status, r.final_session_code
FROM review_tasks rt
JOIN user_accounts ua ON ua.id = rt.reviewer_id
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'FINAL' AND rt.status = 'SCORED'
LIMIT 5
""")
print("\nSCORED 任务:")
for r in cur.fetchall():
    print(r)

# PENDING 状态
cur.execute("""
SELECT rt.id, ua.phone, ua.name, rt.status, r.final_session_code
FROM review_tasks rt
JOIN user_accounts ua ON ua.id = rt.reviewer_id
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'FINAL' AND rt.status = 'PENDING'
LIMIT 5
""")
print("\nPENDING 任务:")
for r in cur.fetchall():
    print(r)

# 沈佩儿负责的会场及其任务
cur.execute("""
SELECT sa.session_code FROM staff_session_assignments sa
JOIN user_accounts ua ON ua.id = sa.staff_id
WHERE ua.name = '沈佩儿'
""")
print("\n沈佩儿的会场:")
for r in cur.fetchall():
    print(r)

conn.close()
