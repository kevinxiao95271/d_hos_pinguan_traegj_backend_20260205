import io
import sys
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    db="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)
cur = conn.cursor()
cur.execute(
    "SELECT LOWER(SUBSTRING_INDEX(file_name,'.',-1)) ext, COUNT(*) "
    "FROM material_files GROUP BY ext ORDER BY COUNT(*) DESC"
)
for ext, cnt in cur.fetchall():
    print(ext, cnt)
conn.close()
