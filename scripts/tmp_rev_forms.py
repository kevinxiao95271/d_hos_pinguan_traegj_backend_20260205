import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT ua.phone, ua.name,
           SUM(CASE WHEN rt.status='SCORED' THEN 1 ELSE 0 END) as scored,
           SUM(CASE WHEN rt.status='DRAFT'  THEN 1 ELSE 0 END) as draft,
           SUM(CASE WHEN rt.status='PENDING' THEN 1 ELSE 0 END) as pending,
           GROUP_CONCAT(DISTINCT r.final_score_form ORDER BY r.final_score_form) as forms
    FROM user_accounts ua
    JOIN review_tasks rt ON rt.reviewer_id = ua.id AND rt.stage = 'FINAL'
    JOIN registrations r ON r.id = rt.registration_id
    WHERE ua.role = 'REVIEWER' AND ua.enabled = 1
    GROUP BY ua.id, ua.phone, ua.name
    ORDER BY ua.id
""")
rows = cur.fetchall()
conn.close()

print(f"共 {len(rows)} 位评委\n")
for phone, name, scored, draft, pending, forms in rows:
    print(f"{phone}  {name}  [{forms}]  已评:{scored} 草稿:{draft} 待评:{pending}")
