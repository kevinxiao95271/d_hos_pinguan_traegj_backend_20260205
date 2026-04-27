import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

print('=== const_init_institutions 按名称搜索 ===')
cur.execute("SELECT id, code, name, region, city, level, uscc FROM const_init_institutions WHERE name LIKE %s", ('%鄞州%三%院%',))
for r in cur.fetchall(): print(r)

print('\n=== institutions 按名称搜索 ===')
cur.execute("SELECT id, code, name, region, city, level, uscc FROM institutions WHERE name LIKE %s", ('%鄞州%三%院%',))
for r in cur.fetchall(): print(r)

conn.close()
