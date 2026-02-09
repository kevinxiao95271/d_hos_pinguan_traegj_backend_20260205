#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

print("=== 检查 competition_group 字段的值 ===\n")

# 查看所有不同的组别值
cursor.execute("SELECT DISTINCT competition_group, COUNT(*) as count FROM pinguan_his_data GROUP BY competition_group ORDER BY count DESC")
groups = cursor.fetchall()

print("数据库中的组别分布：")
for group, count in groups:
    print(f"  '{group}': {count} 条")

print("\n=== 测试查询 ===\n")

# 测试精确匹配
test_values = ['综合组', '基层组', '进阶组', '基层组(基层组积分方式同综合组)']

for value in test_values:
    cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE competition_group = %s", (value,))
    count = cursor.fetchone()[0]
    print(f"精确匹配 '{value}': {count} 条")

cursor.close()
conn.close()
