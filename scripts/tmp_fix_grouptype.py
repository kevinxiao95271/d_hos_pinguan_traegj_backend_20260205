import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("UPDATE registrations SET group_type='BASIC' WHERE group_type='GRASSROOTS'")
print(f'修正 {cur.rowcount} 条 GRASSROOTS -> BASIC')
conn.commit()
conn.close()
