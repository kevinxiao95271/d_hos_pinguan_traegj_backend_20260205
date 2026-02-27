# -*- coding: utf-8 -*-
"""
生成Java jbcrypt兼容的密码hash
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
print("生成Java jbcrypt兼容的密码hash")
print("=" * 100)

# jbcrypt 0.4 支持 $2a$ 版本
# Python bcrypt 生成的 $2b$ 可能不兼容

accounts = [
    {
        'phone': '13800000127',
        'password': 'committee2026',
        'name': '组委会'
    },
    {
        'phone': '13800000005',
        'password': 'ops2026',
        'name': '运维'
    }
]

for account in accounts:
    print(f"\n[{account['name']}]")
    print(f"  手机号: {account['phone']}")
    print(f"  密码: {account['password']}")
    
    # 生成密码hash（$2b$版本）
    password_hash = bcrypt.hashpw(account['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"  生成的hash (2b): {password_hash}")
    print(f"    前缀: {password_hash[:7]}")
    
    # 将 $2b$ 替换为 $2a$ (Java jbcrypt 0.4 兼容格式)
    password_hash_2a = password_hash.replace('$2b$', '$2a$')
    
    print(f"  转换后hash (2a): {password_hash_2a}")
    print(f"    前缀: {password_hash_2a[:7]}")
    
    # 验证两个版本
    verify_2b = bcrypt.checkpw(account['password'].encode('utf-8'), password_hash.encode('utf-8'))
    verify_2a = bcrypt.checkpw(account['password'].encode('utf-8'), password_hash_2a.encode('utf-8'))
    
    print(f"  验证 ($2b$): {verify_2b}")
    print(f"  验证 ($2a$): {verify_2a}")
    
    # 更新数据库
    print(f"  更新数据库...")
    cursor.execute("""
        UPDATE user_accounts 
        SET password = %s
        WHERE phone = %s
    """, (password_hash_2a, account['phone']))
    
    conn.commit()
    print(f"  [完成] 已使用 $2a$ 版本更新")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("密码hash已更新为Java兼容格式")
print("=" * 100)
print("\n说明:")
print("  - Python bcrypt 生成 $2b$ 版本")
print("  - Java jbcrypt 0.4 支持 $2a$ 版本")  
print("  - 已将所有密码hash从 $2b$ 转换为 $2a$")
print("  - 现在应该可以正常登录了")
print("\n" + "=" * 100)
