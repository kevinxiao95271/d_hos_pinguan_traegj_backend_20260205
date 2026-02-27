# -*- coding: utf-8 -*-
"""
检查500错误记录的状态
"""
import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("=" * 100)
print("检查500错误记录的状态")
print("=" * 100)

error_ids = [34, 49, 55, 56, 64, 116, 122, 125]

cursor.execute(f"""
    SELECT id, project_name, status, submitted_at
    FROM registrations
    WHERE id IN ({','.join(map(str, error_ids))})
    ORDER BY id
""")

records = cursor.fetchall()

print(f"\n  500错误记录的状态:")
print(f"  {'ID':<6} {'Status':<12} {'SubmittedAt':<25} {'Project'}")
print(f"  {'-' * 100}")

draft_count = 0
submitted_count = 0

for record in records:
    status = record['status']
    submitted_at = str(record['submitted_at']) if record['submitted_at'] else 'NULL'
    project = record['project_name'][:40]
    
    print(f"  {record['id']:<6} {status:<12} {submitted_at:<25} {project}")
    
    if status == 'DRAFT':
        draft_count += 1
    elif status == 'SUBMITTED':
        submitted_count += 1

print(f"\n{'=' * 100}")
print("[统计]")
print("=" * 100)

print(f"\n  总数: {len(records)}")
print(f"  DRAFT 状态: {draft_count}")
print(f"  SUBMITTED 状态: {submitted_count}")

if draft_count == len(records):
    print(f"\n  [发现] 所有500错误的记录都是 DRAFT 状态！")
    print(f"\n  可能原因:")
    print(f"    DRAFT 状态的记录可能缺少某些必需数据")
    print(f"    或者某些字段在 DRAFT 状态下为 NULL，导致 NullPointerException")
else:
    print(f"\n  [发现] 不是所有错误记录都是 DRAFT 状态")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
