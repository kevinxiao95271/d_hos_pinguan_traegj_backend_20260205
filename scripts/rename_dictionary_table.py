# -*- coding: utf-8 -*-
"""
重命名 dictionary_items_discard 为 dictionary_items
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

print("=" * 80)
print("重命名字典表")
print("=" * 80)

# 1. 检查目标表是否已存在
print("\n[1] 检查表状态...")
cursor.execute("SHOW TABLES LIKE 'dictionary_items'")
target_exists = cursor.fetchone()

cursor.execute("SHOW TABLES LIKE 'dictionary_items_discard'")
source_exists = cursor.fetchone()

if target_exists:
    print("  dictionary_items: 已存在")
    cursor.execute("SELECT COUNT(*) FROM dictionary_items")
    count = cursor.fetchone()[0]
    print(f"    记录数: {count}")
    
    if count > 0:
        print("\n警告: 目标表已存在且有数据！")
        print("需要先删除 dictionary_items 表才能重命名")
        
        cursor.execute("DROP TABLE dictionary_items")
        print("  已删除 dictionary_items 表")
else:
    print("  dictionary_items: 不存在 (可以安全重命名)")

if source_exists:
    print("  dictionary_items_discard: 存在")
    cursor.execute("SELECT COUNT(*) FROM dictionary_items_discard")
    count = cursor.fetchone()[0]
    print(f"    记录数: {count}")
else:
    print("  dictionary_items_discard: 不存在")
    print("\n错误: 源表不存在，无法重命名！")
    cursor.close()
    conn.close()
    exit(1)

# 2. 执行重命名
print("\n[2] 执行重命名...")
try:
    cursor.execute("RENAME TABLE dictionary_items_discard TO dictionary_items")
    conn.commit()
    print("  重命名成功！")
except Exception as e:
    print(f"  重命名失败: {e}")
    conn.rollback()
    cursor.close()
    conn.close()
    exit(1)

# 3. 验证结果
print("\n[3] 验证结果...")
cursor.execute("SHOW TABLES LIKE 'dictionary_items'")
if cursor.fetchone():
    print("  dictionary_items: 存在")
    
    cursor.execute("SELECT COUNT(*) FROM dictionary_items")
    count = cursor.fetchone()[0]
    print(f"    记录数: {count}")
    
    cursor.execute("SELECT type, COUNT(*) FROM dictionary_items GROUP BY type ORDER BY type")
    types = cursor.fetchall()
    print("\n  数据分布:")
    for t in types:
        print(f"    {t[0]:<30} {t[1]:>3} 条")
    
    # 检查索引
    cursor.execute("SHOW INDEX FROM dictionary_items")
    indexes = cursor.fetchall()
    print(f"\n  索引:")
    seen_keys = set()
    for idx in indexes:
        key_name = idx[2]
        if key_name not in seen_keys:
            seen_keys.add(key_name)
            if idx[1] == 0:  # 唯一索引
                print(f"    [UNIQUE] {key_name}")
            else:
                print(f"    [INDEX]  {key_name}")
else:
    print("  dictionary_items: 不存在")
    print("\n错误: 重命名后的表不存在！")

cursor.execute("SHOW TABLES LIKE 'dictionary_items_discard'")
if cursor.fetchone():
    print("  dictionary_items_discard: 仍然存在（异常）")
else:
    print("  dictionary_items_discard: 已消失（正常）")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("表重命名完成！")
print("=" * 80)
