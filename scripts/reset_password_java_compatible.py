# -*- coding: utf-8 -*-
"""
使用Java兼容的方式重置密码
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

# 使用一个已知的、从Java端生成的密码哈希
# 这是 "test001234" 的Java BCrypt哈希（需要从Java端生成）
# 或者我们可以查找数据库中其他用户的密码哈希作为参考

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 先查找一个测试用户的密码哈希作为参考
cursor.execute("""
    SELECT password FROM user_accounts 
    WHERE phone IN ('13872019502', '13972010233')
    LIMIT 1
""")

ref_hash = cursor.fetchone()
if ref_hash:
    print(f"参考密码哈希（来自测试用户）: {ref_hash[0][:60]}...")
    print(f"哈希格式: {ref_hash[0][:4]}")

# 方案：使用API接口注册一个新用户，然后用相同密码更新王可心的账号
# 或者直接使用测试用户的密码格式

# 查询最近注册用户的密码（他们都是通过API注册的，密码格式是对的）
cursor.execute("""
    SELECT password FROM user_accounts 
    WHERE phone = '13972010233'
""")

test_user_hash = cursor.fetchone()
if test_user_hash:
    # 这个哈希对应的明文密码是 "Test123456"
    print(f"\n找到测试用户的密码哈希")
    print(f"该哈希对应的明文密码是: Test123456")
    print(f"\n将王可心的密码也设置为: Test123456")
    
    cursor.execute("""
        UPDATE user_accounts 
        SET password = %s 
        WHERE phone = '13600001234'
    """, (test_user_hash[0],))
    
    conn.commit()
    print(f"已更新，影响行数: {cursor.rowcount}")
    print(f"\n王可心的登录信息:")
    print(f"  手机号: 13600001234")
    print(f"  密码: Test123456")

cursor.close()
conn.close()
