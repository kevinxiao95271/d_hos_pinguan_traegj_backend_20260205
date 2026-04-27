import pymysql

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

USCCS = ('1233020041952986XM', 'TE3302043300201770')

for table in ('institutions', 'const_init_institutions'):
    fmt = ','.join(['%s'] * len(USCCS))
    cur.execute(f"SELECT id, name, uscc, region FROM `{table}` WHERE uscc IN ({fmt})", USCCS)
    rows = cur.fetchall()
    print(f'\n[{table}] 查到 {len(rows)} 条:')
    for r in rows:
        print(f"  id={r['id']}")
        print(f"    name   = {r['name']}")
        print(f"    uscc   = {r['uscc']}")
        print(f"    region = {r['region']}")

cur.close()
conn.close()
