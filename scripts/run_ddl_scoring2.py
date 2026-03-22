import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

def col_exists(table, col):
    cur.execute('SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s',
                ('d_hos_pinguan_traegj_20260205', table, col))
    return cur.fetchone()[0] > 0

# shortlist_override
if not col_exists('registrations', 'shortlist_override'):
    cur.execute("ALTER TABLE `registrations` ADD COLUMN `shortlist_override` varchar(16) DEFAULT NULL COMMENT 'INCLUDE/EXCLUDE'")
    conn.commit()
    print('[OK] registrations.shortlist_override added')
else:
    print('[SKIP] registrations.shortlist_override already exists')

# shortlist_note
if not col_exists('registrations', 'shortlist_note'):
    cur.execute("ALTER TABLE `registrations` ADD COLUMN `shortlist_note` varchar(200) DEFAULT NULL COMMENT '人工干预说明'")
    conn.commit()
    print('[OK] registrations.shortlist_note added')
else:
    print('[SKIP] registrations.shortlist_note already exists')

# 验证
print('\n=== 验证 ===')
cur.execute('SHOW COLUMNS FROM registrations LIKE %s', ('shortlist%',))
for c in cur.fetchall():
    print(f'  {c[0]}: {c[1]}')

conn.close()
