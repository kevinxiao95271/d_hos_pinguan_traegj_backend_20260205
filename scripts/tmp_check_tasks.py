import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',port=63606,user='root',password='Yiguo9527_',
                       database='d_hos_pinguan_traegj_20260205',charset='utf8mb4')
cur = conn.cursor()
# reviewer id for 冯博士
cur.execute("SELECT id FROM user_accounts WHERE phone='13859958962'")
uid = cur.fetchone()
print('user id:', uid)
cur.execute("SELECT id, stage, status, registration_id FROM review_tasks WHERE reviewer_id=%s AND stage='FINAL' LIMIT 5", (uid[0],))
rows = cur.fetchall()
print(f'FINAL tasks: {len(rows)}')
for r in rows: print(r)

# 看看db里到底有没有FINAL任务
cur.execute("SELECT COUNT(*) FROM review_tasks WHERE stage='FINAL'")
print('total FINAL tasks:', cur.fetchone())
conn.close()
