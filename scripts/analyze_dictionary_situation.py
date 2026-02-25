# -*- coding: utf-8 -*-
"""
分析字典数据现状
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

print("=" * 100)
print("字典数据现状分析")
print("=" * 100)

# 1. 检查dictionary_items表是否存在
print("\n[1] 检查dictionary_items表")
cursor.execute("SHOW TABLES LIKE 'dictionary_items'")
dict_table = cursor.fetchone()

if dict_table:
    print("  状态: 存在")
    cursor.execute("SELECT COUNT(*) FROM dictionary_items")
    count = cursor.fetchone()[0]
    print(f"  记录数: {count}")
else:
    print("  状态: 不存在 (已被删除)")

# 2. 检查dictionary_items_discard表
print("\n[2] 检查dictionary_items_discard表")
cursor.execute("SHOW TABLES LIKE 'dictionary_items_discard'")
discard_table = cursor.fetchone()

if discard_table:
    print("  状态: 存在")
    cursor.execute("SELECT COUNT(*) FROM dictionary_items_discard")
    count = cursor.fetchone()[0]
    print(f"  记录数: {count}")
    
    cursor.execute("SELECT type, COUNT(*) FROM dictionary_items_discard GROUP BY type")
    types = cursor.fetchall()
    print("\n  按类型统计:")
    for t in types:
        print(f"    {t[0]:<30} {t[1]:>3} 条")
else:
    print("  状态: 不存在")

# 3. 检查前端正在使用的字典类型
print("\n[3] 前端正在调用的字典类型")
required_types = [
    'method',
    'subject_type', 
    'experience_improve',
    'quality_topic'
]

print("  根据前端错误信息，正在调用:")
for t in required_types:
    print(f"    - GET /api/dictionaries/{t}")

# 4. 检查dictionary_items_discard是否包含这些类型
print("\n[4] dictionary_items_discard 是否包含所需类型")
if discard_table:
    for t in required_types:
        cursor.execute("SELECT COUNT(*) FROM dictionary_items_discard WHERE type = %s", (t,))
        count = cursor.fetchone()[0]
        status = "✓ 有数据" if count > 0 else "✗ 无数据"
        print(f"    {t:<30} {count:>3} 条  {status}")

# 5. 检查Java代码中是否还有DictionaryController
print("\n[5] 检查Java Controller文件")
import os
controller_path = r"d:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\src\main\java\com\trae\pinguan\web\DictionaryController.java"
if os.path.exists(controller_path):
    print(f"  DictionaryController.java: 存在")
else:
    print(f"  DictionaryController.java: 不存在 (已被删除)")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("总结")
print("=" * 100)
print("\n现状:")
print("  - dictionary_items 表: 不存在 (我已删除)")
print("  - dictionary_items_discard 表: 存在 (110条完整数据)")
print("  - DictionaryController API: 不存在 (我已删除)")
print("  - 前端: 正在调用 /api/dictionaries/* 接口 → 404错误")
print("\n解决方案选项:")
print("  方案1: 恢复DictionaryController，让它读取 dictionary_items_discard 表")
print("  方案2: 将 dictionary_items_discard 重命名为 dictionary_items，恢复Controller")
print("  方案3: 创建新的API读取 discard 表，保持表名不变")
print("  方案4: 前端改为使用其他数据源")
