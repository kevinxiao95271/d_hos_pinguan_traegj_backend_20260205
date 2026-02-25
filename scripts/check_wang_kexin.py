# -*- coding: utf-8 -*-
"""
检查王可心的账号信息
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

cursor.execute("""
    SELECT id, name, phone, password_hash, role, enabled 
    FROM accounts 
    WHERE phone = '13600001234' OR name = '王可心'
""")

result = cursor.fetchone()

if result:
    print(f"ID: {result[0]}")
    print(f"姓名: {result[1]}")
    print(f"手机: {result[2]}")
    print(f"密码哈希: {result[3][:50]}...")
    print(f"角色: {result[4]}")
    print(f"启用: {result[5]}")
else:
    print("未找到用户")

cursor.close()
conn.close()
