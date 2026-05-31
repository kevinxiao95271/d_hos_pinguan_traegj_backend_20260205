import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("DESCRIBE registrations")
for r in cur.fetchall():
    print(f"{r[0]:35s} {r[1]:25s} {'NOT NULL' if r[2]=='NO' else 'NULL':8s} default={r[4]}")
# 看一条真实数据样本
print("\n=== 真实样本 ===")
cur.execute("SELECT * FROM registrations WHERE status='SUBMITTED' LIMIT 1")
cols = [d[0] for d in cur.description]
row = cur.fetchone()
for c, v in zip(cols, row):
    print(f"  {c}: {v}")
conn.close()
