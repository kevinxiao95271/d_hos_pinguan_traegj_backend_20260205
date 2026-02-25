# -*- coding: utf-8 -*-
"""
检查王可心的密码并测试验证
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

# 查询王可心的信息
cursor.execute("""
    SELECT id, phone, name, password, enabled
    FROM user_accounts 
    WHERE phone = '13600001234'
""")

user = cursor.fetchone()

if user:
    print(f"用户信息:")
    print(f"  ID: {user[0]}")
    print(f"  手机号: {user[1]}")
    print(f"  姓名: {user[2]}")
    print(f"  密码哈希: {user[3][:60]}...")
    print(f"  启用状态: {user[4]}")
    
    # 测试密码验证
    stored_hash = user[3]
    test_password = "test001234"
    
    try:
        if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
            print(f"\n  [OK] 密码验证成功！密码是: {test_password}")
        else:
            print(f"\n  [FAIL] 密码验证失败")
            
            # 尝试其他常见密码
            common_passwords = ["Test123456", "Admin123456", "123456", "test123"]
            for pwd in common_passwords:
                if bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8')):
                    print(f"  [OK] 正确密码是: {pwd}")
                    break
    except Exception as e:
        print(f"\n  [ERROR] 密码验证异常: {e}")
else:
    print("未找到该用户")

cursor.close()
conn.close()
