#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查字典表结构"""

import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

print("dictionary_items 表结构:")
cursor.execute("DESCRIBE dictionary_items")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}")

cursor.close()
conn.close()
