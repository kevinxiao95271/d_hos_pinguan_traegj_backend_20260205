# -*- coding: utf-8 -*-
"""
清理字典数据和表
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
print("清理字典数据")
print("=" * 100)

# 1. 先查看表中的数据
print("\n[步骤1] 查看dictionary_items表中的数据")
try:
    cursor.execute("SELECT COUNT(*) FROM dictionary_items")
    count = cursor.fetchone()[0]
    print(f"  当前记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT type, COUNT(*) FROM dictionary_items GROUP BY type")
        types = cursor.fetchall()
        print("\n  按类型统计:")
        for t in types:
            print(f"    {t[0]}: {t[1]} 条")
except Exception as e:
    print(f"  表不存在或查询失败: {e}")

# 2. 删除所有数据
print("\n[步骤2] 删除dictionary_items表中的所有数据")
try:
    cursor.execute("DELETE FROM dictionary_items")
    deleted = cursor.rowcount
    conn.commit()
    print(f"  [OK] 已删除 {deleted} 条记录")
except Exception as e:
    print(f"  删除失败: {e}")

# 3. 删除表
print("\n[步骤3] 删除dictionary_items表")
try:
    cursor.execute("DROP TABLE IF EXISTS dictionary_items")
    conn.commit()
    print(f"  [OK] 表已删除")
except Exception as e:
    print(f"  删除表失败: {e}")

# 4. 验证
print("\n[步骤4] 验证删除结果")
try:
    cursor.execute("SHOW TABLES LIKE 'dictionary_items'")
    result = cursor.fetchone()
    if result:
        print(f"  [WARN] 表仍然存在")
    else:
        print(f"  [OK] 表已成功删除")
except Exception as e:
    print(f"  验证失败: {e}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("数据库清理完成！")
print("=" * 100)
