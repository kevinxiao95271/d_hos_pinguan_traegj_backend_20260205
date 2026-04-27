import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

sqls = [
    'ALTER TABLE institutions DROP INDEX UK_90wcwrx6ap068pspum25xhtyu',
    'ALTER TABLE institutions DROP INDEX UK_995bkje2y26mqm8f45fc51rwo',
    'ALTER TABLE institutions ADD UNIQUE KEY uk_uscc_name (uscc, name(100))',
]
for sql in sqls:
    cur.execute(sql)
    print('OK:', sql[:70])

conn.commit()

# 验证现有索引
cur.execute('SHOW INDEX FROM institutions')
for row in cur.fetchall():
    print('INDEX:', row[2], '->', row[4])

conn.close()
print('Done.')
