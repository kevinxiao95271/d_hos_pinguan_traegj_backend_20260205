# -*- coding: utf-8 -*-
"""
查询账号信息
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
print("账号信息查询")
print("=" * 100)

# 查询组委会账号（COMMITTEE_ADMIN 或 OPS）
print("\n[1] 组委会账号:")
print("-" * 100)
cursor.execute("""
    SELECT 
        id, 
        phone, 
        name, 
        role,
        enabled,
        institution_id
    FROM user_accounts 
    WHERE role IN ('COMMITTEE_ADMIN', 'OPS')
    ORDER BY id
""")

committee_accounts = cursor.fetchall()
if committee_accounts:
    for acc in committee_accounts:
        print(f"ID: {acc[0]}")
        print(f"  手机号: {acc[1]}")
        print(f"  姓名: {acc[2]}")
        print(f"  角色: {acc[3]}")
        print(f"  启用: {acc[4]}")
        print(f"  机构ID: {acc[5]}")
        print(f"  说明: 密码需要通过注册流程设置，或由管理员重置")
        print()
else:
    print("  未找到组委会账号")

# 查询王可心账号
print("\n[2] 王可心账号:")
print("-" * 100)
cursor.execute("""
    SELECT 
        u.id, 
        u.phone, 
        u.name, 
        u.role,
        u.enabled,
        u.institution_id,
        i.name as institution_name
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.name LIKE '%王可心%'
    ORDER BY u.id
""")

wangkexin_accounts = cursor.fetchall()
if wangkexin_accounts:
    for acc in wangkexin_accounts:
        print(f"ID: {acc[0]}")
        print(f"  手机号: {acc[1]}")
        print(f"  姓名: {acc[2]}")
        print(f"  角色: {acc[3]}")
        print(f"  启用: {acc[4]}")
        print(f"  机构ID: {acc[5]}")
        print(f"  机构名: {acc[6]}")
        print(f"  说明: 密码已加密存储，无法直接查看")
        print()
else:
    print("  未找到王可心账号")

# 查询所有用户（最近20个）
print("\n[3] 最近注册的20个账号:")
print("-" * 100)
cursor.execute("""
    SELECT 
        id, 
        phone, 
        name, 
        role,
        enabled,
        created_at
    FROM user_accounts 
    ORDER BY id DESC
    LIMIT 20
""")

recent_accounts = cursor.fetchall()
print(f"{'ID':<5} {'手机号':<15} {'姓名':<20} {'角色':<20} {'启用':<10} {'创建时间'}")
print("-" * 100)
for acc in recent_accounts:
    print(f"{acc[0]:<5} {acc[1]:<15} {acc[2]:<20} {acc[3]:<20} {str(acc[4]):<10} {str(acc[5])}")

print("\n" + "=" * 100)
print("说明：")
print("1. 密码使用 BCrypt 加密存储，无法直接查看明文")
print("2. 如需重置密码，建议：")
print("   - 使用忘记密码功能（如已实现）")
print("   - 或由管理员通过后台重置")
print("3. 测试环境常用密码: Test123456 或 Admin123456")
print("=" * 100)

cursor.close()
conn.close()
