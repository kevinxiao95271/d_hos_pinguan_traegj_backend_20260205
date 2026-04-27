import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT ua.id, ua.name, ua.phone, i.name AS inst
    FROM user_accounts ua
    LEFT JOIN institutions i ON ua.institution_id = i.id
    WHERE ua.name = '尹艳玲'
""")
users = cur.fetchall()
print(f"=== 用户账号（共{len(users)}条）===")
for r in users:
    print(f"  uid={r[0]}  {r[1]}  phone={r[2]}  机构={r[3]}")

if users:
    uid = users[0][0]
    cur.execute("""
        SELECT r.id, r.project_name, r.group_type, r.status, r.submitted_at
        FROM registrations r WHERE r.applicant_id = %s
    """, (uid,))
    regs = cur.fetchall()
    print(f"\n=== 报名记录（共{len(regs)}条）===")
    for r in regs:
        print(f"  reg_id={r[0]}  {r[1]}  {r[2]}  {r[3]}  submitted={r[4]}")

conn.close()
