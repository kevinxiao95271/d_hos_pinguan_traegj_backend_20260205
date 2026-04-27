import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 先看表结构
cur.execute("DESCRIBE const_init_institutions")
print("表结构：")
for col in cur.fetchall():
    print(f"  {col[0]:30s} {col[1]}  null={col[2]}  default={col[4]}")

# 再看参考记录
cur.execute("SELECT * FROM const_init_institutions WHERE uscc = '123305004711716660' LIMIT 1")
cols = [d[0] for d in cur.description]
row = cur.fetchone()
if row:
    print("\n参考记录（湖州师范附一）：")
    for c, v in zip(cols, row):
        print(f"  {c:30s} = {v}")

conn.close()
