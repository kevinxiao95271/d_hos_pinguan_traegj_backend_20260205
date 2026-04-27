import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute('SELECT VERSION()')
print('MySQL:', cur.fetchone()[0])
cur.execute('SHOW COLUMNS FROM registrations LIKE %s', ('shortlist%',))
print('existing shortlist cols:', cur.fetchall())
conn.close()
