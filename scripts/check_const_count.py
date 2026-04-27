import pymysql
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM const_init_institutions")
total = cur.fetchone()[0]
print("const_init_institutions 总记录数:", total)
if total > 0:
    cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE city='省级'")
    print("city=省级 记录数:", cur.fetchone()[0])
    cur.execute("SELECT name, region, city, level FROM const_init_institutions WHERE city='省级' LIMIT 3")
    for r in cur.fetchall():
        print(" ", r)
conn.close()
