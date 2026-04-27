# -*- coding: utf-8 -*-
import sys, bcrypt
sys.stdout.reconfigure(encoding="utf-8")

pwd = "ops2026"
h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode().replace("$2b$", "$2a$")
print(f"-- 系统运维  13800000005  密码: {pwd}")
print(f"UPDATE user_accounts SET password = '{h}' WHERE phone = '13800000005';")
