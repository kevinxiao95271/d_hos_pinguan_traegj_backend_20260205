import pymysql
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 先看历史数据表结构
cur.execute("DESCRIBE pinguan_his_data")
cols = cur.fetchall()
print("=== pinguan_his_data 表结构 ===")
for c in cols:
    print(f"  {c[0]:30s} {c[1]}")
print()

# 看几条样例
cur.execute("SELECT * FROM pinguan_his_data LIMIT 3")
rows = cur.fetchall()
col_names = [c[0] for c in cur.description]
print("=== 样例数据（前3条）===")
print(" | ".join(col_names))
for row in rows:
    print(" | ".join(str(v) if v is not None else 'NULL' for v in row))

conn.close()
