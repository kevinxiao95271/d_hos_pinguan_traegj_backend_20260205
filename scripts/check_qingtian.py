import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT id, name, level, uscc FROM institutions WHERE name LIKE '%青田县人民医院%'")
print('institutions 表:')
for r in cur.fetchall():
    print(f'  id={r[0]} name={r[1]} level={r[2]} uscc={r[3]}')

cur.execute("SELECT id, name, level, uscc FROM const_init_institutions WHERE name LIKE '%青田县人民医院%'")
print('const_init_institutions 表:')
for r in cur.fetchall():
    print(f'  id={r[0]} name={r[1]} level={r[2]} uscc={r[3]}')

conn.close()
