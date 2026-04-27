import pymysql
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4',
    connect_timeout=10
)
cur = conn.cursor()

cur.execute("""
    SELECT i.id, i.name, COUNT(r.id) as cnt
    FROM registrations r
    JOIN institutions i ON r.institution_id = i.id
    WHERE r.status = 'SUBMITTED'
    GROUP BY i.id, i.name
    ORDER BY cnt DESC
    LIMIT 10
""")

rows = cur.fetchall()
print(f"{'机构ID':<10} {'已提交数':<8} 机构名称")
print("-" * 60)
for inst_id, name, cnt in rows:
    print(f"{inst_id:<10} {cnt:<8} {name}")

cur.close()
conn.close()
