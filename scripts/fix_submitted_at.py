# -*- coding: utf-8 -*-
"""
修复测试数据的submitted_at字段
对于状态为SUBMITTED的报名，补充submitted_at时间
"""
import pymysql
from datetime import datetime, timedelta
import random

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
print("修复报名记录的submitted_at字段")
print("=" * 80)

# 1. 统计当前情况
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN submitted_at IS NULL AND status = 'SUBMITTED' THEN 1 ELSE 0 END) as need_fix,
        SUM(CASE WHEN submitted_at IS NOT NULL THEN 1 ELSE 0 END) as has_value
    FROM registrations
""")

stats = cursor.fetchone()
print(f"\n[当前状态]")
print(f"  总报名数: {stats[0]}")
print(f"  需要修复(SUBMITTED但submitted_at为空): {stats[1]}")
print(f"  已有submitted_at: {stats[2]}")

if stats[1] == 0:
    print("\n无需修复，所有SUBMITTED状态的报名都有submitted_at!")
    cursor.close()
    conn.close()
    exit(0)

# 2. 获取需要修复的报名
cursor.execute("""
    SELECT id, created_at
    FROM registrations
    WHERE status = 'SUBMITTED' AND submitted_at IS NULL
    ORDER BY id
""")

records = cursor.fetchall()
print(f"\n[开始修复] 共 {len(records)} 条记录...")

updated_count = 0
for record in records:
    reg_id = record[0]
    created_at = record[1]
    
    # submitted_at应该在created_at之后的几分钟到几小时内
    # 随机生成一个合理的提交时间
    minutes_after_create = random.randint(5, 60 * 24)  # 5分钟到24小时之间
    submitted_at = created_at + timedelta(minutes=minutes_after_create)
    
    cursor.execute("""
        UPDATE registrations
        SET submitted_at = %s
        WHERE id = %s
    """, (submitted_at, reg_id))
    
    updated_count += 1
    if updated_count % 10 == 0:
        print(f"  已更新 {updated_count}/{len(records)} 条...")

conn.commit()
print(f"\n[完成] 成功更新 {updated_count} 条报名的submitted_at字段")

# 3. 验证结果
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN submitted_at IS NULL AND status = 'SUBMITTED' THEN 1 ELSE 0 END) as still_null,
        SUM(CASE WHEN submitted_at IS NOT NULL AND status = 'SUBMITTED' THEN 1 ELSE 0 END) as has_value
    FROM registrations
""")

stats = cursor.fetchone()
print(f"\n[验证结果]")
print(f"  总报名数: {stats[0]}")
print(f"  SUBMITTED状态但submitted_at仍为空: {stats[1]}")
print(f"  SUBMITTED状态且有submitted_at: {stats[2]}")

if stats[1] == 0:
    print("\n[OK] 所有SUBMITTED状态的报名都已有submitted_at!")
else:
    print(f"\n[WARN] 仍有 {stats[1]} 条SUBMITTED状态的报名没有submitted_at")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
