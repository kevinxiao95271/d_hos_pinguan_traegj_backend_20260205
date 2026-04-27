import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

name = '金华市婺城区白龙桥镇中心卫生院'

# 精确查
print('=== institutions 表（精确）===')
cur.execute("SELECT id, name, level, region FROM institutions WHERE name=%s", (name,))
for r in cur.fetchall(): print(f'  id={r[0]} name={r[1]} level={r[2]} region={r[3]}')

print('=== institutions 表（模糊）===')
cur.execute("SELECT id, name, level, region FROM institutions WHERE name LIKE %s", (f'%白龙桥%',))
for r in cur.fetchall(): print(f'  id={r[0]} name={r[1]} level={r[2]} region={r[3]}')

print('=== const_init_institutions 表（精确）===')
cur.execute("SELECT id, name, level, region FROM const_init_institutions WHERE name=%s", (name,))
for r in cur.fetchall(): print(f'  id={r[0]} name={r[1]} level={r[2]} region={r[3]}')

print('=== const_init_institutions 表（模糊）===')
cur.execute("SELECT id, name, level, region FROM const_init_institutions WHERE name LIKE %s", (f'%白龙桥%',))
for r in cur.fetchall(): print(f'  id={r[0]} name={r[1]} level={r[2]} region={r[3]}')

conn.close()
