import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute('DESCRIBE const_init_institutions')
print('=== const_init_institutions 字段 ===')
for r in cur.fetchall():
    print(r)

cur.execute('DESCRIBE institutions')
print('\n=== institutions 字段 ===')
for r in cur.fetchall():
    print(r)

cur.execute('SELECT * FROM const_init_institutions WHERE city=%s LIMIT 3', ('宁波',))
print('\n=== const_init_institutions 宁波样本 ===')
for r in cur.fetchall():
    print(r)

cur.execute('SELECT * FROM institutions WHERE city=%s LIMIT 3', ('宁波',))
print('\n=== institutions 宁波样本 ===')
for r in cur.fetchall():
    print(r)

conn.close()
