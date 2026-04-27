import pymysql
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE city='省级'")
print("city=省级 总记录数:", cur.fetchone()[0])

cur.execute("SELECT region, level, name FROM const_init_institutions WHERE city='省级' LIMIT 8")
print("省级样本:")
for row in cur.fetchall():
    print(" ", row)

cur.execute("SELECT DISTINCT city FROM const_init_institutions WHERE city IS NOT NULL ORDER BY city")
cities = [r[0] for r in cur.fetchall()]
print("city字段所有不同值:", cities)

conn.close()
