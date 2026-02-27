# -*- coding: utf-8 -*-
"""
检查报名记录的submitted_at字段
"""
import mysql.connector

conn = mysql.connector.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205'
)

cursor = conn.cursor()

# 检查submitted_at字段情况
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN submitted_at IS NULL THEN 1 ELSE 0 END) as null_count,
        SUM(CASE WHEN submitted_at IS NOT NULL THEN 1 ELSE 0 END) as has_value_count
    FROM registrations
""")

stats = cursor.fetchone()
print(f"[统计]")
print(f"  总记录数: {stats[0]}")
print(f"  submitted_at为NULL: {stats[1]}")
print(f"  submitted_at有值: {stats[2]}")

# 查看一些样例数据
print(f"\n[样例数据] (前10条)")
cursor.execute("""
    SELECT id, project_name, submitted_at, created_at, status
    FROM registrations
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"  ID: {row[0]}")
    print(f"    项目名称: {row[1]}")
    print(f"    提交时间: {row[2]}")
    print(f"    创建时间: {row[3]}")
    print(f"    状态: {row[4]}")
    print()

conn.close()
