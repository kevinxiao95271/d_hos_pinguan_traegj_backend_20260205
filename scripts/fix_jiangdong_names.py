import pymysql

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

UPDATES = [
    {
        'uscc': '1233020041952986XM',
        'name': '宁波市医疗中心李惠利医院',
        'region': '鄞州区',
    },
    {
        'uscc': 'TE3302043300201770',
        'name': '中国人民解放军联勤保障部队第九〇六医院',
        'region': '鄞州区',
    },
]

conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

for table in ('institutions', 'const_init_institutions'):
    print(f'\n[{table}]')
    for u in UPDATES:
        cur.execute(
            f"UPDATE `{table}` SET `name`=%s, `region`=%s WHERE `uscc`=%s",
            (u['name'], u['region'], u['uscc'])
        )
        print(f"  uscc={u['uscc']} -> name={u['name']} region={u['region']}  affected={cur.rowcount}")

conn.commit()

# 验证
print('\n验证:')
cur.execute("""
    SELECT id, name, uscc, region
    FROM institutions
    WHERE uscc IN ('1233020041952986XM','TE3302043300201770')
""")
for r in cur.fetchall():
    print(f"  id={r['id']} name={r['name']} uscc={r['uscc']} region={r['region']}")

cur.close()
conn.close()
