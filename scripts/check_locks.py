import pymysql
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4',
    connect_timeout=10, read_timeout=10, write_timeout=10
)
cur = conn.cursor()

print("=== 当前进程列表 ===")
cur.execute("SHOW FULL PROCESSLIST")
for row in cur.fetchall():
    print(row)

print("\n=== InnoDB 状态（锁信息）===")
cur.execute("SHOW ENGINE INNODB STATUS")
status = cur.fetchone()[2]
# 只取 TRANSACTIONS 部分
start = status.find('TRANSACTIONS')
end = status.find('FILE I/O', start)
print(status[start:end] if start > 0 else "no transactions section")

conn.close()
