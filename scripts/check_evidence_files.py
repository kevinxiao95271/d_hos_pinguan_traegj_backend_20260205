import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT id FROM user_accounts WHERE phone='13300003355'")
row = cur.fetchone()
if not row:
    print('用户不存在'); conn.close(); exit()
uid = row[0]

cur.execute("SELECT id, status FROM registrations WHERE applicant_id=%s ORDER BY id DESC LIMIT 1", (uid,))
reg = cur.fetchone()
if not reg:
    print('无报名记录'); conn.close(); exit()
reg_id, status = reg
print(f'报名 id={reg_id} 状态={status}\n')

cur.execute("""
    SELECT id, type, file_name, uploaded_at
    FROM material_files
    WHERE registration_id=%s
    ORDER BY type, uploaded_at
""", (reg_id,))
rows = cur.fetchall()
print(f'全部附件（{len(rows)} 条）:')
for r in rows:
    print(f'  id={r[0]:>4}  type={r[1]:<30} file={r[2]}  uploaded={r[3]}')

# 单独列佐证材料
evidence = [r for r in rows if r[1].upper() == 'EVIDENCE']
print(f'\n佐证材料 EVIDENCE（{len(evidence)} 条）:')
for r in evidence:
    print(f'  id={r[0]}  file={r[2]}  uploaded={r[3]}')

conn.close()
