import pymysql
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("""
    SELECT status, COUNT(*) AS cnt
    FROM registrations
    GROUP BY status
    ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(f"  {r['status']}: {r['cnt']} 条")
cur.close()
conn.close()
