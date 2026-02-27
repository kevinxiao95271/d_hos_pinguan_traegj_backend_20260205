# -*- coding: utf-8 -*-
"""
验证submitted_at字段的数据完整性
1. 检查数据库中submitted_at为空的记录
2. 对比API返回的submittedAt为空的记录
3. 验证是否一致
"""
import pymysql
import requests

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("验证 submitted_at 字段数据完整性")
print("=" * 100)

# 1. 检查数据库
print("\n[步骤1] 检查数据库中的submitted_at字段...")

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 统计数据库情况
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN submitted_at IS NULL THEN 1 ELSE 0 END) as null_count,
        SUM(CASE WHEN submitted_at IS NOT NULL THEN 1 ELSE 0 END) as has_value_count
    FROM registrations
""")

stats = cursor.fetchone()
print(f"\n[数据库统计]")
print(f"  总记录数: {stats[0]}")
print(f"  submitted_at为NULL: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
print(f"  submitted_at有值: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")

# 按状态统计
cursor.execute("""
    SELECT 
        status,
        COUNT(*) as total,
        SUM(CASE WHEN submitted_at IS NULL THEN 1 ELSE 0 END) as null_count,
        SUM(CASE WHEN submitted_at IS NOT NULL THEN 1 ELSE 0 END) as has_value_count
    FROM registrations
    GROUP BY status
    ORDER BY status
""")

print(f"\n[按状态分类统计]")
for row in cursor.fetchall():
    status, total, null_count, has_value = row
    print(f"  {status}:")
    print(f"    总数: {total}")
    print(f"    submitted_at为NULL: {null_count}")
    print(f"    submitted_at有值: {has_value}")

# 获取submitted_at为NULL的记录ID
cursor.execute("""
    SELECT id, project_name, status, created_at
    FROM registrations
    WHERE submitted_at IS NULL
    ORDER BY id
""")

db_null_records = cursor.fetchall()
db_null_ids = set([row[0] for row in db_null_records])

print(f"\n[数据库中submitted_at为NULL的记录]")
print(f"  共 {len(db_null_ids)} 条")
print(f"  前10条ID: {sorted(list(db_null_ids))[:10]}")

# 2. 检查API返回
print("\n" + "=" * 100)
print("[步骤2] 检查API返回的submittedAt字段...")

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

if login_response.status_code != 200:
    print(f"[ERROR] 登录失败")
    cursor.close()
    conn.close()
    exit(1)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 获取筛选列表
filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

if filter_response.status_code != 200:
    print(f"[ERROR] API请求失败")
    cursor.close()
    conn.close()
    exit(1)

items = filter_response.json()['data']

print(f"\n[API返回统计]")
print(f"  总记录数: {len(items)}")

api_null_items = [item for item in items if item.get('submittedAt') is None]
api_has_value_items = [item for item in items if item.get('submittedAt') is not None]

print(f"  submittedAt为null: {len(api_null_items)} ({len(api_null_items)/len(items)*100:.1f}%)")
print(f"  submittedAt有值: {len(api_has_value_items)} ({len(api_has_value_items)/len(items)*100:.1f}%)")

api_null_ids = set([item['registrationId'] for item in api_null_items])

print(f"\n[API中submittedAt为null的记录]")
print(f"  共 {len(api_null_ids)} 条")
print(f"  前10条ID: {sorted(list(api_null_ids))[:10]}")

# 3. 对比验证
print("\n" + "=" * 100)
print("[步骤3] 对比验证 - 数据库 vs API")
print("=" * 100)

# 检查是否完全一致
if db_null_ids == api_null_ids:
    print(f"\n[OK] 完全一致！")
    print(f"  数据库和API返回的submittedAt为空的记录ID完全相同")
else:
    print(f"\n[WARN] 存在差异！")
    
    # 找出差异
    only_in_db = db_null_ids - api_null_ids
    only_in_api = api_null_ids - db_null_ids
    
    if only_in_db:
        print(f"\n  数据库中为NULL但API中有值的记录: {len(only_in_db)} 条")
        print(f"    ID列表: {sorted(list(only_in_db))[:20]}")
    
    if only_in_api:
        print(f"\n  API中为null但数据库中有值的记录: {len(only_in_api)} 条")
        print(f"    ID列表: {sorted(list(only_in_api))[:20]}")

# 4. 详细分析空值记录
print("\n" + "=" * 100)
print("[步骤4] 分析submitted_at为空的记录特征")
print("=" * 100)

print(f"\n[数据库中为NULL的记录详情] (前10条)")
for i, row in enumerate(db_null_records[:10], 1):
    id, project_name, status, created_at = row
    print(f"\n  {i}. ID={id}")
    print(f"     项目名称: {project_name[:50]}...")
    print(f"     状态: {status}")
    print(f"     创建时间: {created_at}")

# 检查是否都是DRAFT状态
draft_count = sum(1 for row in db_null_records if row[2] == 'DRAFT')
submitted_count = sum(1 for row in db_null_records if row[2] == 'SUBMITTED')

print(f"\n[submitted_at为NULL的记录状态分布]")
print(f"  DRAFT状态: {draft_count} 条 ({draft_count/len(db_null_records)*100:.1f}%)")
print(f"  SUBMITTED状态: {submitted_count} 条 ({submitted_count/len(db_null_records)*100:.1f}%)")

if submitted_count > 0:
    print(f"\n[WARNING] 存在 {submitted_count} 条SUBMITTED状态但submitted_at为NULL的异常记录！")
    
    # 列出这些异常记录
    cursor.execute("""
        SELECT id, project_name, status, created_at
        FROM registrations
        WHERE submitted_at IS NULL AND status = 'SUBMITTED'
        ORDER BY id
    """)
    
    abnormal_records = cursor.fetchall()
    print(f"\n[异常记录详情]:")
    for i, row in enumerate(abnormal_records[:10], 1):
        id, project_name, status, created_at = row
        print(f"\n  {i}. ID={id}")
        print(f"     项目名称: {project_name[:50]}...")
        print(f"     状态: {status}")
        print(f"     创建时间: {created_at}")
        print(f"     [问题] SUBMITTED状态但submitted_at为NULL")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)
print(f"\n数据库统计:")
print(f"  - 总记录: {stats[0]} 条")
print(f"  - submitted_at为NULL: {stats[1]} 条")
print(f"  - submitted_at有值: {stats[2]} 条")

print(f"\nAPI返回统计:")
print(f"  - 总记录: {len(items)} 条")
print(f"  - submittedAt为null: {len(api_null_items)} 条")
print(f"  - submittedAt有值: {len(api_has_value_items)} 条")

print(f"\n一致性验证:")
if db_null_ids == api_null_ids:
    print(f"  [OK] API返回与数据库完全一致")
else:
    print(f"  [WARN] 存在差异，需要进一步检查")

print("\n" + "=" * 100)
