import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 查看review_tasks表的列结构
cur.execute("SHOW COLUMNS FROM review_tasks")
print("review_tasks columns:")
for r in cur.fetchall():
    print(r)

conn.close()
