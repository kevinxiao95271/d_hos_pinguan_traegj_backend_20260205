import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT id, name, uscc FROM const_init_institutions WHERE name LIKE '%杭州市第一人民医院%'")
for r in cur.fetchall():
    print(f"id={r[0]}  {r[1]}  uscc={r[2]}")
conn.close()
