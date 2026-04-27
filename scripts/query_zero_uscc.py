import pymysql
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

cur.execute("""
SELECT id, name, region, city, level, uscc
FROM const_init_institutions
WHERE uscc = '000000000000000000'
ORDER BY id
LIMIT 20
""")
rows = cur.fetchall()
print(f"USCC=000000000000000000 前20条：\n")
for row in rows:
    print(f"  id={row[0]}  name={row[1]}  region={row[2]}  level={row[4]}")

cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE uscc = '000000000000000000'")
total = cur.fetchone()[0]
print(f"\n合计: {total} 条")

conn.close()
