# -*- coding: utf-8 -*-
import sys, bcrypt
sys.stdout.reconfigure(encoding="utf-8")

def make_hash_2a(pwd: str) -> str:
    # 强制使用 $2a$ 前缀（Spring Security 兼容）
    raw = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    return raw.decode().replace("$2b$", "$2a$")

experts = [
    ("吕娜",   "13588426741", "9aF4eXAh"),
    ("陈志良", "13567534846", "VSJ7fNzn"),
]

print("=" * 60)
for name, phone, pwd in experts:
    h = make_hash_2a(pwd)
    print(f"{name}  {phone}  密码: {pwd}")
    print(f"  hash: {h}")
print("=" * 60)
print()
print("-- SQL")
for name, phone, pwd in experts:
    h = make_hash_2a(pwd)
    print(f"-- {name}  密码: {pwd}")
    print(f"UPDATE user_accounts SET password = '{h}' WHERE phone = '{phone}' AND name = '{name}';")
    print()
