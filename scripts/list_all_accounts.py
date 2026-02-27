# -*- coding: utf-8 -*-
"""
列出所有账号和角色类型
"""
import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

print("=" * 100)
print("所有账号列表")
print("=" * 100)

# 1. 查询所有角色类型
cursor.execute("SELECT DISTINCT role FROM user_accounts ORDER BY role")
roles = cursor.fetchall()

print(f"\n系统中的所有角色类型:")
for role in roles:
    print(f"  - {role[0]}")

# 2. 按角色分组统计
print(f"\n按角色分组统计:")
cursor.execute("""
    SELECT role, COUNT(*) as count
    FROM user_accounts
    GROUP BY role
    ORDER BY role
""")
role_counts = cursor.fetchall()

for rc in role_counts:
    print(f"  {rc[0]:<15} {rc[1]:>3} 个账号")

# 3. 列出所有非普通参赛者的账号
print(f"\n所有管理类账号详情:")
print("-" * 100)

cursor.execute("""
    SELECT id, name, phone, role, enabled, created_at
    FROM user_accounts
    WHERE role != 'CONTESTANT'
    ORDER BY role, id
""")

special_accounts = cursor.fetchall()

if special_accounts:
    for acc in special_accounts:
        status = "启用" if acc[4] else "禁用"
        print(f"ID:{acc[0]:>3} | {acc[1]:<20} | {acc[2]:<15} | {acc[3]:<15} | {status:<4} | {acc[5]}")
else:
    print("没有找到管理类账号")

# 4. 列出部分普通参赛者账号
print(f"\n部分普通参赛者账号 (前5个):")
print("-" * 100)

cursor.execute("""
    SELECT id, name, phone, enabled, created_at
    FROM user_accounts
    WHERE role = 'CONTESTANT'
    ORDER BY created_at DESC
    LIMIT 5
""")

contestants = cursor.fetchall()
for acc in contestants:
    status = "启用" if acc[3] else "禁用"
    print(f"ID:{acc[0]:>3} | {acc[1]:<20} | {acc[2]:<15} | {status:<4} | {acc[4]}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
