import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SHOW COLUMNS FROM scoring_snapshots LIKE 'rank'")
if cur.fetchone():
    cur.execute("ALTER TABLE `scoring_snapshots` CHANGE COLUMN `rank` `irank` INT DEFAULT NULL COMMENT '排名'")
    conn.commit()
    print('[OK] rank -> irank 列改名完成')
else:
    cur.execute("SHOW COLUMNS FROM scoring_snapshots LIKE 'irank'")
    if cur.fetchone():
        print('[SKIP] 列已是 irank，无需变更')
    else:
        print('[WARN] 列不存在，请手动检查')

cur.execute("SHOW COLUMNS FROM scoring_snapshots")
print('\n当前 scoring_snapshots 列:')
for c in cur.fetchall():
    print(f'  {c[0]:30s} {c[1]}')
conn.close()
