import sys, io, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    before = cur.fetchone()[0]
    cur.execute("DELETE FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    conn.commit()
    print(f'删除前: {before} 条，已删除: {cur.rowcount} 条')
    cur.execute("SELECT COUNT(*) FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    after = cur.fetchone()[0]
    print(f'删除后剩余: {after} 条')
conn.close()
print('完成，所有面谈评委下次登录将重新触发诚信须知弹窗。')
