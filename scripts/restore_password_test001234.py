# -*- coding: utf-8 -*-
"""
恢复王可心的密码为 test001234
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

# 从之前备份的密码哈希恢复
# test001234 的哈希是: $2b$12$Vj2Ed8Ktm8CnZ3C9wpgvr.1YqNpJNOnXwZNYj/aw8SYtz15Ft67aK

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 查询当前密码
cursor.execute("SELECT password FROM user_accounts WHERE phone = '13600001234'")
current = cursor.fetchone()
print(f"当前密码哈希: {current[0][:60]}...")

# 恢复为原密码
original_hash = "$2b$12$Vj2Ed8Ktm8CnZ3C9wpgvr.1YqNpJNOnXwZNYj/aw8SYtz15Ft67aK"

cursor.execute("""
    UPDATE user_accounts 
    SET password = %s 
    WHERE phone = '13600001234'
""", (original_hash,))

conn.commit()

print(f"\n已恢复密码为原值")
print(f"  手机号: 13600001234")
print(f"  密码: test001234")
print(f"  影响行数: {cursor.rowcount}")

cursor.close()
conn.close()
