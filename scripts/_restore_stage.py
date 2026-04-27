import sys, io, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("SELECT stage, register_end FROM competitions WHERE id = 1")
    before = cur.fetchone()
    print(f'修改前: stage={before[0]}, register_end={before[1]}')

    cur.execute("""
        UPDATE competitions 
        SET stage = 'BOOK_REVIEW',
            register_end = '2026-03-27 19:36:53'
        WHERE id = 1
    """)
    conn.commit()

    cur.execute("SELECT stage, register_end FROM competitions WHERE id = 1")
    after = cur.fetchone()
    print(f'修改后: stage={after[0]}, register_end={after[1]}')
conn.close()
print('完成')
