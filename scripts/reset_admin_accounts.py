# -*- coding: utf-8 -*-
"""
重置管理员账号密码（组委会、运维）
"""
import pymysql
import bcrypt

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
print("重置管理员账号密码")
print("=" * 100)

# 1. 查询所有管理员账号
print("\n[1] 查询现有管理员账号...")
cursor.execute("""
    SELECT id, name, phone, role, enabled 
    FROM user_accounts 
    WHERE role IN ('COMMITTEE', 'OPS', 'ADMIN')
    ORDER BY role
""")

admins = cursor.fetchall()

if not admins:
    print("未找到管理员账号！")
    cursor.close()
    conn.close()
    exit(1)

print(f"\n找到 {len(admins)} 个管理员账号:")
for admin in admins:
    print(f"  ID:{admin[0]:>3} | {admin[1]:<15} | {admin[2]:<15} | {admin[3]:<12} | 启用:{admin[4]}")

# 2. 准备重置的账号和密码
reset_accounts = [
    {
        'role': 'COMMITTEE_ADMIN',
        'new_password': 'committee2026',
        'description': '赛事组委会'
    },
    {
        'role': 'OPS',
        'new_password': 'ops2026',
        'description': '系统运维'
    }
]

print("\n[2] 开始重置密码...")

reset_results = []

for account_config in reset_accounts:
    role = account_config['role']
    new_password = account_config['new_password']
    description = account_config['description']
    
    print(f"\n  [{description}] 角色: {role}")
    
    # 查询该角色的账号
    cursor.execute("SELECT id, name, phone FROM user_accounts WHERE role = %s", (role,))
    account = cursor.fetchone()
    
    if not account:
        print(f"    未找到 {role} 角色的账号")
        continue
    
    account_id = account[0]
    account_name = account[1]
    account_phone = account[2]
    
    print(f"    账号: {account_name} ({account_phone})")
    print(f"    新密码: {new_password}")
    
    # 使用bcrypt生成密码哈希
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"    密码哈希: {password_hash[:50]}...")
    
    # 更新密码（user_accounts表使用password字段）
    cursor.execute("""
        UPDATE user_accounts 
        SET password = %s
        WHERE id = %s
    """, (password_hash, account_id))
    
    conn.commit()
    print(f"    状态: 密码已更新")
    
    # 确保账号启用
    cursor.execute("UPDATE user_accounts SET enabled = 1 WHERE id = %s", (account_id,))
    conn.commit()
    print(f"    状态: 账号已启用")
    
    reset_results.append({
        'description': description,
        'role': role,
        'name': account_name,
        'phone': account_phone,
        'password': new_password
    })

# 3. 验证更新
print("\n[3] 验证密码更新...")
for result in reset_results:
    cursor.execute("""
        SELECT password, enabled 
        FROM user_accounts 
        WHERE phone = %s
    """, (result['phone'],))
    
    verify = cursor.fetchone()
    if verify:
        # 验证bcrypt哈希
        is_valid = bcrypt.checkpw(result['password'].encode('utf-8'), verify[0].encode('utf-8'))
        status = "验证通过" if is_valid else "验证失败"
        enabled_status = "已启用" if verify[1] else "已禁用"
        print(f"  {result['description']}: {status}, {enabled_status}")
    else:
        print(f"  {result['description']}: 未找到账号")

cursor.close()
conn.close()

# 4. 输出测试账号信息
print("\n" + "=" * 100)
print("管理员账号测试信息")
print("=" * 100)

for result in reset_results:
    print(f"\n【{result['description']}】")
    print(f"  角色: {result['role']}")
    print(f"  姓名: {result['name']}")
    print(f"  手机: {result['phone']}")
    print(f"  密码: {result['password']}")
    print(f"  登录API: POST /api/auth/login-with-password")
    print(f"  请求体: {{'phone': '{result['phone']}', 'password': '{result['password']}'}}")

print("\n" + "=" * 100)
print("密码重置完成！")
print("=" * 100)
