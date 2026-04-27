# -*- coding: utf-8 -*-
import sys, bcrypt
sys.stdout.reconfigure(encoding="utf-8")

try:
    import pymysql
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "-q"])
    import pymysql

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4"
)
cur = conn.cursor()
cur.execute("SELECT id, name, phone, role, enabled FROM user_accounts WHERE role = 'OPS'")
rows = cur.fetchall()
print("── OPS 账号 ──────────────────────────────")
for r in rows:
    print(f"  id={r[0]}  name={r[1]}  phone={r[2]}  enabled={r[4]}")

# 顺便生成重置密码 SQL
print()
print("── 重置密码 SQL（ops2026）────────────────")
pwd = "ops2026"
for r in rows:
    phone = r[2]
    h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")
    print(f"-- {r[1]}  {phone}")
    print(f"UPDATE user_accounts SET password = '{h}' WHERE phone = '{phone}' AND role = 'OPS';")

conn.close()
