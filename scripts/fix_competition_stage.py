# -*- coding: utf-8 -*-
"""
修复赛事阶段
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

# 更新赛事阶段
cursor.execute("UPDATE competitions SET stage = 'REGISTER' WHERE id = 1")
conn.commit()

print(f"已更新赛事阶段为 REGISTER, 影响行数: {cursor.rowcount}")

cursor.close()
conn.close()
