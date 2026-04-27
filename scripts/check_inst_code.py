import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 看几条湖州机构的 code 样本
cur.execute("""
    SELECT id, name, code, uscc, region, level FROM institutions
    WHERE region LIKE '%湖州%' ORDER BY id LIMIT 10
""")
print("=== 湖州机构样本 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  code={r[2]}  {r[1]}")

# 看最近新增的几条
cur.execute("""
    SELECT id, name, code, uscc, region, level FROM institutions
    ORDER BY id DESC LIMIT 5
""")
print("\n=== 最新插入的5条 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  code={r[2]}  uscc={r[3]}  {r[1]}")

conn.close()
