import sys, io, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute('SHOW COLUMNS FROM competitions')
    cols = [r[0] for r in cur.fetchall()]
    print('competitions 列:', cols)
    cur.execute('SELECT * FROM competitions')
    for r in cur.fetchall():
        print(dict(zip(cols, r)))
conn.close()
