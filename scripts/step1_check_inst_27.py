#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤1: 查看机构ID=27的信息"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

DB_CONFIG = {
    'host': '1.94.176.95',
    'user': 'wjx',
    'password': 'kevinxiao',
    'database': 'pinguan_db',
    'charset': 'utf8mb4',
    'port': 3306
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

print("查看机构ID=27:")
cursor.execute("SELECT id, name, credit_code FROM institutions WHERE id = 27")
inst = cursor.fetchone()
if inst:
    print(f"ID={inst['id']}, Name={inst['name']}, CreditCode={inst['credit_code']}")
else:
    print("不存在")

print("\n查看该机构的报名数量:")
cursor.execute("SELECT COUNT(*) as cnt FROM registrations WHERE institution_id = 27")
print(f"报名数量: {cursor.fetchone()['cnt']}")

print("\n查看该机构的用户数量:")
cursor.execute("SELECT COUNT(*) as cnt FROM user_accounts WHERE institution_id = 27")
print(f"用户数量: {cursor.fetchone()['cnt']}")

cursor.close()
conn.close()
