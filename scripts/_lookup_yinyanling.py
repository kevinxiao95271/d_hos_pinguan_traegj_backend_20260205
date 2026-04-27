import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 查 user_accounts 总数
cur.execute('SELECT COUNT(*) FROM user_accounts')
total = cur.fetchone()[0]
print(f'user_accounts 总数: {total}')

# 查所有 CONTESTANT 账号
cur.execute("""
    SELECT ua.id, ua.name, ua.phone, ua.role, ua.enabled, i.name AS inst
    FROM user_accounts ua
    LEFT JOIN institutions i ON ua.institution_id = i.id
    WHERE ua.role = 'CONTESTANT'
    ORDER BY ua.id
""")
contestants = cur.fetchall()
print(f'\n=== CONTESTANT账号（共{len(contestants)}条）===')
for r in contestants:
    print(f'  uid={r[0]}  name={r[1]}  phone={r[2]}  role={r[3]}  enabled={r[4]}  机构={r[5]}')

conn.close()
