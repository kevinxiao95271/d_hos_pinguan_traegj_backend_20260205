# -*- coding: utf-8 -*-
"""
重置用户密码
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

# 要设置的新密码
new_password = "test001234"
phone = "13600001234"

# 生成BCrypt密码哈希
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 更新密码
cursor.execute("""
    UPDATE user_accounts 
    SET password = %s 
    WHERE phone = %s
""", (password_hash, phone))

conn.commit()

print(f"已重置用户密码:")
print(f"  手机号: {phone}")
print(f"  新密码: {new_password}")
print(f"  影响行数: {cursor.rowcount}")

cursor.close()
conn.close()
