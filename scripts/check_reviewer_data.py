#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查评审专家数据"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'pinguan_new',
    'user': 'postgres',
    'password': 'postgres'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("=" * 80)
print("检查评审专家数据")
print("=" * 80)

# 1. 检查机构ID=2是否存在
print("\n1. 检查机构ID=2:")
cursor.execute("SELECT id, name, code FROM institutions WHERE id = 2")
inst = cursor.fetchone()
if inst:
    print(f"✓ 机构存在: {inst['name']} (code: {inst['code']})")
else:
    print(f"✗ 机构ID=2不存在!")

# 2. 检查评审专家账号
print("\n2. 检查评审专家账号 (phone=13800000006):")
cursor.execute("""
    SELECT id, phone, name, title, role, institution_id, expert_background
    FROM user_accounts 
    WHERE phone = '13800000006'
""")
user = cursor.fetchone()
if user:
    print(f"✓ 用户存在:")
    print(f"  ID: {user['id']}")
    print(f"  姓名: {user['name']}")
    print(f"  角色: {user['role']}")
    print(f"  机构ID: {user['institution_id']}")
    print(f"  专业背景: {user['expert_background']}")
else:
    print(f"✗ 用户不存在")

# 3. 列出所有评审专家
print("\n3. 所有评审专家账号:")
cursor.execute("""
    SELECT u.id, u.phone, u.name, u.role, u.institution_id, i.name as institution_name
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.id
    LIMIT 10
""")
reviewers = cursor.fetchall()
if reviewers:
    for r in reviewers:
        print(f"  ID:{r['id']} {r['name']} ({r['phone']}) - 机构:{r['institution_name'] or 'NULL'}")
else:
    print(f"  没有评审专家账号")

# 4. 检查可用的机构
print("\n4. 前10个机构:")
cursor.execute("SELECT id, name FROM institutions ORDER BY id LIMIT 10")
institutions = cursor.fetchall()
for inst in institutions:
    print(f"  ID:{inst['id']} {inst['name']}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
