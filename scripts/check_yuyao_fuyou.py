import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT id, name, uscc, region, city, level FROM institutions WHERE name = '余姚市妇幼保健院'")
print("=== institutions ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  region={r[3]}  city={r[4]}  level={r[5]}")

cur.execute("SELECT id, name, uscc FROM const_init_institutions WHERE name = '余姚市妇幼保健院'")
print("\n=== const_init_institutions ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

conn.close()
