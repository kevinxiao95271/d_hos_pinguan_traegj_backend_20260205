import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606, user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("""
    SELECT ua.id, ua.name, ua.phone, r.final_session_code
    FROM review_tasks rt
    JOIN user_accounts ua ON ua.id = rt.reviewer_id
    JOIN registrations r ON r.id = rt.registration_id
    WHERE rt.stage = 'FINAL' AND ua.role = 'REVIEWER'
    GROUP BY ua.id, ua.name, ua.phone, r.final_session_code
    ORDER BY r.final_session_code, ua.name
    LIMIT 20
""")
for row in cur.fetchall():
    print('\t'.join(str(x) for x in row))
conn.close()
