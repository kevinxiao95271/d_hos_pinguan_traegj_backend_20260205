import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    UPDATE institutions SET city = '湖州市吴兴区长兴路999号'
    WHERE id = 36310
""")
conn.commit()
print(f"更新成功，affected={cur.rowcount}")

cur.execute("SELECT id, name, region, city, level FROM institutions WHERE id = 36310")
r = cur.fetchone()
print(f"  id={r[0]}  {r[1]}  region={r[2]}  city={r[3]}  level={r[4]}")
conn.close()
