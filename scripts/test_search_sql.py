import pymysql
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4',
    connect_timeout=10, read_timeout=15, write_timeout=15
)
cur = conn.cursor()

print("1. COUNT(*) 无条件:")
cur.execute("SELECT COUNT(*) FROM const_init_institutions")
print(" ", cur.fetchone()[0])

print("2. region='上城区' 的记录数:")
cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE region='上城区'")
print(" ", cur.fetchone()[0])

print("3. city='省级' 的记录数:")
cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE city='省级'")
print(" ", cur.fetchone()[0])

print("4. name LIKE '%医院%' 记录数:")
cur.execute("SELECT COUNT(*) FROM const_init_institutions WHERE name LIKE '%医院%'")
print(" ", cur.fetchone()[0])

print("5. region='上城区' 样本:")
cur.execute("SELECT name, region, city, level FROM const_init_institutions WHERE region='上城区' LIMIT 3")
for r in cur.fetchall():
    print(" ", r)

print("6. city='省级' 样本:")
cur.execute("SELECT name, region, city, level FROM const_init_institutions WHERE city='省级' LIMIT 3")
for r in cur.fetchall():
    print(" ", r)

conn.close()
print("done")
