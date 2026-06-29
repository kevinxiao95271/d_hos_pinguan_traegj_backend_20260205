import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 详查孙丽娟的问题解决型专场1任务
cur.execute("""
SELECT rt.id, rt.status, r.final_session_code, r.final_score_form, r.project_name
FROM review_tasks rt
JOIN registrations r ON r.id = rt.registration_id
JOIN user_accounts ua ON ua.id = rt.reviewer_id
WHERE ua.name = '孙丽娟' AND rt.stage = 'FINAL' AND r.final_session_code LIKE '%问题解决型专场1'
""")
print("孙丽娟 问题解决型专场1 任务:")
for r in cur.fetchall():
    print(r)

conn.close()
