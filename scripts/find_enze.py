import pymysql
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, code, uscc, name, region, city, level
    FROM const_init_institutions
    WHERE name LIKE '%恩泽%'
""")
for row in cur.fetchall():
    print(row)

conn.close()
