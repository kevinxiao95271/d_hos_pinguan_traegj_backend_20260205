import pymysql
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4',
    connect_timeout=10, read_timeout=15, write_timeout=15
)
cur = conn.cursor()
# 用 information_schema 查行数估算，避免全表扫描
cur.execute("""
    SELECT TABLE_NAME, TABLE_ROWS 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA='d_hos_pinguan_traegj_20260205'
    ORDER BY TABLE_NAME
""")
for row in cur.fetchall():
    print(f"{row[0]}: ~{row[1]} rows")
conn.close()
