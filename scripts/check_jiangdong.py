import pymysql
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

print('=== institutions: region=江东区 ===')
cur.execute("SELECT id, name, uscc, level, region, city FROM institutions WHERE region='江东区'")
for r in cur.fetchall():
    print(f"  id={r['id']} {r['name']} uscc={r['uscc']} level={r['level']} region={r['region']}")

print('\n=== const_init_institutions: region=江东区 ===')
cur.execute("SELECT id, name, uscc, level, region, city FROM const_init_institutions WHERE region='江东区'")
for r in cur.fetchall():
    print(f"  id={r['id']} {r['name']} uscc={r['uscc']} level={r['level']} region={r['region']}")

print('\n=== 李孝利 (user_accounts) ===')
cur.execute("""
    SELECT u.id, u.name, u.phone, u.role,
           i.id AS inst_id, i.name AS inst_name, i.uscc, i.region
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.name LIKE '%李%利%' OR u.name LIKE '%李孝%'
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  {r['name']} phone={r['phone']} role={r['role']} inst={r['inst_name']} region={r['region']}")
else:
    print('  未找到，尝试更宽松搜索...')
    cur.execute("SELECT id, name, phone, role FROM user_accounts WHERE name LIKE '%孝利%'")
    for r in cur.fetchall():
        print(f"  id={r['id']} {r['name']} phone={r['phone']} role={r['role']}")

cur.close()
conn.close()
