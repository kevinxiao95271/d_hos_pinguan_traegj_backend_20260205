import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT phone, name, role FROM user_accounts WHERE role IN ('ADMIN','OPS','OPERATOR') LIMIT 10")
for r in cur.fetchall():
    print(r)
conn.close()
