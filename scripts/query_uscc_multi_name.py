import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("""
SELECT
    uscc,
    COUNT(DISTINCT name)               AS name_count,
    GROUP_CONCAT(DISTINCT name ORDER BY name SEPARATOR ' | ') AS names,
    GROUP_CONCAT(DISTINCT id  ORDER BY name SEPARATOR ' | ') AS const_ids
FROM const_init_institutions
WHERE uscc IS NOT NULL
GROUP BY uscc
HAVING COUNT(DISTINCT name) > 1
ORDER BY name_count DESC, uscc
""")
rows = cur.fetchall()
print(f'共 {len(rows)} 条同USCC多名称记录\n')
for row in rows:
    print(f'USCC: {row[0]}')
    print(f'  名称数: {row[1]}')
    print(f'  名称: {row[2]}')
    print(f'  const_ids: {row[3]}')
    print()
conn.close()
