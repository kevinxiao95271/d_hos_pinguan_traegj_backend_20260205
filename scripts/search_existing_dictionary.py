# -*- coding: utf-8 -*-
"""
搜索是否存在其他字典数据表
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
print("搜索数据库中的字典相关表")
print("=" * 100)

# 查找所有表名
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("\n所有表:")
print("-" * 100)
for table in tables:
    table_name = table[0]
    print(f"  {table_name}")

# 查找包含dictionary/dict/option/选项等关键词的表
print("\n\n字典相关的表:")
print("-" * 100)
dict_tables = [t[0] for t in tables if 'dict' in t[0].lower() or 'option' in t[0].lower() or 'item' in t[0].lower()]

if dict_tables:
    for table_name in dict_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} 条记录")
        
        if count > 0 and count < 200:  # 如果记录数不太多，显示一些样例
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            
            # 获取列名
            cursor.execute(f"DESC {table_name}")
            cols = cursor.fetchall()
            col_names = [col[0] for col in cols]
            
            print(f"\n    {table_name} 表结构和样例数据:")
            print(f"    列: {', '.join(col_names)}")
            
            for row in rows:
                print(f"    样例: {dict(zip(col_names, row))}")
else:
    print("  未找到相关表")

# 检查activity_info表中实际使用的字典代码
print("\n\n" + "=" * 100)
print("检查activity_info表中实际使用的字典代码")
print("=" * 100)

cursor.execute("DESC activity_info")
columns = cursor.fetchall()

code_fields = [col[0] for col in columns if 'code' in col[0].lower()]

print(f"\nactivity_info表中的code字段: {code_fields}")

for field in code_fields:
    print(f"\n{field} 的不重复值:")
    cursor.execute(f"SELECT DISTINCT {field} FROM activity_info WHERE {field} IS NOT NULL AND {field} != '' LIMIT 20")
    values = cursor.fetchall()
    if values:
        for val in values:
            print(f"  - {val[0]}")
    else:
        print("  (无数据)")

cursor.close()
conn.close()
