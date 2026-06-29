import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 生产库连接（需要用户提供，暂用测试库）
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606, user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 面谈和书审涉及的专家（REVIEWER角色）
cur.execute("""
    SELECT DISTINCT ua.id, ua.phone, ua.name, ua.title,
           i.name AS institution,
           ua.role
    FROM user_accounts ua
    LEFT JOIN institutions i ON i.id = ua.institution_id
    WHERE ua.role = 'REVIEWER'
    ORDER BY ua.name
""")
rows = cur.fetchall()
conn.close()

print(f"REVIEWER 共 {len(rows)} 人:\n")
for r in rows:
    print(f"  id={r[0]}  {r[1]}  {r[2]}  {r[3] or ''}  {r[4] or ''}")
