#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
DB_CONFIG = {'host': '1.94.176.95', 'user': 'wjx', 'password': 'kevinxiao', 'database': 'pinguan_db', 'charset': 'utf8mb4', 'port': 3306}
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
conn.commit()
print("外键检查已禁用")
cursor.close()
conn.close()
