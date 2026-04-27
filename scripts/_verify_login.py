# -*- coding: utf-8 -*-
import sys, bcrypt, pymysql
sys.stdout.reconfigure(encoding="utf-8")

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com", port=63606,
    user="root", password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205", charset="utf8mb4"
)
cur = conn.cursor()

# 查实际列名
cur.execute("SHOW COLUMNS FROM user_accounts")
cols = [r[0] for r in cur.fetchall()]
print("列名:", cols)
print()

# 查账号现状
cur.execute("SELECT * FROM user_accounts WHERE phone = '13800000027'")
row = cur.fetchone()
if row:
    for col, val in zip(cols, row):
        print(f"  {col}: {val}")

# 直接写入新密码
pwd = "ops2026"
new_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")
pwd_col = next((c for c in cols if "pass" in c.lower()), None)
print()
print(f"密码列: {pwd_col}")
print(f"新 hash: {new_hash}")

if pwd_col:
    cur.execute(f"UPDATE user_accounts SET `{pwd_col}` = %s WHERE phone = '13800000027'", (new_hash,))
    conn.commit()
    print(f"已直接更新 {cur.rowcount} 行")

conn.close()
