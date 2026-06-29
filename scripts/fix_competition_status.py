import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
c = conn.cursor()

# 旧数据 status='' 需要修正；真实赛事（id<=2）设 ACTIVE，其余测试数据设 DRAFT
c.execute("UPDATE competitions SET status='ACTIVE' WHERE id IN (1, 2)")
c.execute("UPDATE competitions SET status='DRAFT'  WHERE id NOT IN (1, 2) AND (status IS NULL OR status = '')")

# 让列支持 NULL，并加默认值 DRAFT
c.execute("ALTER TABLE competitions MODIFY COLUMN status VARCHAR(16) NULL DEFAULT 'DRAFT'")

conn.commit()

c.execute('SELECT id, name, status FROM competitions')
for row in c.fetchall():
    print(row)

conn.close()
print('done')
