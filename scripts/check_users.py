# -*- coding: utf-8 -*-
"""
查询已有用户
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

# 查询所有用户
cursor.execute("""
    SELECT 
        u.id, 
        u.phone, 
        u.name, 
        u.role,
        u.institution_id,
        i.name as institution_name
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    ORDER BY u.id DESC
    LIMIT 10
""")

users = cursor.fetchall()

print("最近10个用户:")
print("-" * 100)
for user in users:
    print(f"ID: {user[0]}, 手机: {user[1]}, 姓名: {user[2]}, 角色: {user[3]}, 机构ID: {user[4]}, 机构: {user[5]}")

cursor.close()
conn.close()
