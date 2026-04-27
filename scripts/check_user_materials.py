import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 找用户
cur.execute("SELECT id, name, phone FROM user_accounts WHERE phone='13300003355'")
user = cur.fetchone()
if not user:
    print('用户不存在'); conn.close(); exit()
print(f'用户: id={user[0]} name={user[1]} phone={user[2]}')

# 找该用户的报名记录
cur.execute("""
    SELECT id, project_name, status, created_at, submitted_at
    FROM registrations WHERE applicant_id=%s ORDER BY id DESC
""", (user[0],))
regs = cur.fetchall()
print(f'\n报名记录 ({len(regs)} 条):')
for r in regs:
    print(f'  reg_id={r[0]} project={r[1]} status={r[2]} created={r[3]}')

# 找每个报名的材料
for r in regs:
    cur.execute("""
        SELECT id, type, file_name, file_url, uploaded_at
        FROM material_files WHERE registration_id=%s ORDER BY uploaded_at
    """, (r[0],))
    mats = cur.fetchall()
    print(f'\n  reg_id={r[0]} 的材料 ({len(mats)} 条):')
    for m in mats:
        print(f'    id={m[0]} type={m[1]} file={m[2]} uploaded={m[4]}')

conn.close()
