import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

roles = ['OPS', 'COMMITTEE_ADMIN', 'REVIEWER', 'CONTESTANT']

for role in roles:
    cur.execute("""
        SELECT ua.id, ua.name, ua.phone, ua.enabled,
               i.name as inst_name
        FROM user_accounts ua
        LEFT JOIN institutions i ON ua.institution_id = i.id
        WHERE ua.role = %s
        ORDER BY ua.id
        LIMIT 5
    """, (role,))
    rows = cur.fetchall()
    print(f'\n=== {role} ({len(rows)}条) ===')
    for r in rows:
        inst = f' [{r[4]}]' if r[4] else ''
        print(f'  id={r[0]:<4} phone={r[2]:<14} name={r[1]}{inst}  enabled={r[3]}')

# 额外统计总数
print('\n=== 各角色总数 ===')
cur.execute("""
    SELECT role, COUNT(*), SUM(enabled) FROM user_accounts GROUP BY role ORDER BY role
""")
for r in cur.fetchall():
    print(f'  {r[0]:<20} 总计{r[1]} 条，启用{r[2]}条')

conn.close()
