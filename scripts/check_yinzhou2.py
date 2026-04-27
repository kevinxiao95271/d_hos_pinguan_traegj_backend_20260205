import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, name, uscc, region, level
    FROM const_init_institutions
    WHERE name LIKE '%中西医结合%' AND name LIKE '%宁波%'
""")
print("=== 宁波 中西医结合 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  {r[3]}  {r[4]}")

cur.execute("""
    SELECT id, name, uscc, region, level
    FROM const_init_institutions
    WHERE name LIKE '%鄞州区第二%'
""")
print("\n=== 鄞州区第二 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  {r[3]}  {r[4]}")

conn.close()
