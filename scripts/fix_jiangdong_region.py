"""
宁波江东区已撤销并入鄞州区
将 institutions 和 const_init_institutions 中 region='江东区' 的记录改为 '鄞州区'
"""
import pymysql

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

# ── 更新前先确认 ─────────────────────────────────────────────────────────────
for table in ('institutions', 'const_init_institutions'):
    cur.execute(f"SELECT id, name, uscc, region FROM `{table}` WHERE region='江东区'")
    rows = cur.fetchall()
    print(f'\n[{table}] 待更新 {len(rows)} 条:')
    for r in rows:
        print(f"  id={r['id']} {r['name']} uscc={r['uscc']}")

# ── 执行更新 ─────────────────────────────────────────────────────────────────
cur.execute("UPDATE institutions SET region='鄞州区' WHERE region='江东区'")
n1 = cur.rowcount
cur.execute("UPDATE const_init_institutions SET region='鄞州区' WHERE region='江东区'")
n2 = cur.rowcount
conn.commit()

print(f'\n[OK] institutions 更新 {n1} 条，const_init_institutions 更新 {n2} 条')

# ── 验证 ─────────────────────────────────────────────────────────────────────
cur.execute("SELECT id, name, region FROM institutions WHERE uscc IN ('1233020041952986XM','TE3302043300201770')")
print('\n验证结果:')
for r in cur.fetchall():
    print(f"  id={r['id']} {r['name']} region={r['region']}")

cur.close()
conn.close()
