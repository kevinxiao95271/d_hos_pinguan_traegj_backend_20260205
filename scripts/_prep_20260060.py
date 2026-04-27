# -*- coding: utf-8 -*-
import sys, bcrypt, pymysql
sys.stdout.reconfigure(encoding="utf-8")

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com", port=63606,
    user="root", password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205", charset="utf8mb4"
)
cur = conn.cursor()

# 先看看 registration 20260060 的信息
cur.execute("SELECT id, project_name, status, applicant_id FROM registrations WHERE id = 20260060")
reg = cur.fetchone()
print(f"项目: {reg}")

if reg and reg[3]:
    cur.execute("SELECT id, name, phone, password FROM user_accounts WHERE id = %s", (reg[3],))
    row = cur.fetchone()
else:
    # 也许通过机构找
    cur.execute("""
        SELECT ua.id, ua.name, ua.phone, ua.password
        FROM registrations r
        JOIN institutions i ON i.id = r.institution_id
        JOIN user_accounts ua ON ua.institution_id = i.id AND ua.role = 'CONTESTANT'
        WHERE r.id = 20260060
        LIMIT 1
    """)
    row = cur.fetchone()

if not row:
    print("找不到对应账号，请手动确认 applicant_id")
    conn.close()
    sys.exit()

uid, name, phone, orig_hash = row
print(f"\n账号: id={uid}  name={name}  phone={phone}")
print(f"原始密码密文: {orig_hash}")
print()

tmp_pwd  = "user20260414"
tmp_hash = bcrypt.hashpw(tmp_pwd.encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")

print(f"临时密码: {tmp_pwd}")
print(f"临时密文: {tmp_hash}")
print()
print("=" * 60)
print("-- ① 设置临时密码（你登录用）")
print(f"UPDATE user_accounts SET password = '{tmp_hash}' WHERE id = {uid};")
print()
print("-- ② 项目改 DRAFT（开放补传入口）")
print("UPDATE registrations SET status = 'DRAFT' WHERE id = 20260060 AND status = 'SUBMITTED';")
print()
print("-- ③ 传完后改回 SUBMITTED")
print("UPDATE registrations SET status = 'SUBMITTED' WHERE id = 20260060 AND status = 'DRAFT';")
print()
print("-- ④ 改回原密码")
print(f"UPDATE user_accounts SET password = '{orig_hash}' WHERE id = {uid};")

conn.close()
