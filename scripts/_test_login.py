# -*- coding: utf-8 -*-
import sys, bcrypt, pymysql
sys.stdout.reconfigure(encoding="utf-8")

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com", port=63606,
    user="root", password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205", charset="utf8mb4"
)
cur = conn.cursor()

PWD = "ops2026"
new_hash = bcrypt.hashpw(PWD.encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")

cur.execute("UPDATE user_accounts SET password = %s WHERE phone = '13800000005'", (new_hash,))
conn.commit()
print(f"已重置 13800000005 密码为: {PWD}")
print(f"新 hash: {new_hash}")

# 验证写入
cur.execute("SELECT password FROM user_accounts WHERE phone = '13800000005'")
stored = cur.fetchone()[0]
check = bcrypt.checkpw(PWD.encode(), stored.replace("$2a$", "$2b$").encode())
print(f"写入后验证: {check}")
conn.close()
