# -*- coding: utf-8 -*-
"""
测试草稿过滤功能 - 验证草稿不会出现在分组列表中
"""
import requests
import pymysql

BASE_URL = "http://localhost:6031/api"

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("测试草稿过滤功能")
print("=" * 100)

# 1. 检查数据库状态
print("\n[步骤1] 检查数据库状态...")

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        status,
        COUNT(*) as count
    FROM registrations
    GROUP BY status
    ORDER BY status
""")

print("\n[数据库统计]")
db_stats = {}
for row in cursor.fetchall():
    status, count = row
    db_stats[status] = count
    print(f"  {status}: {count} 条")

cursor.close()
conn.close()

# 2. 登录获取token
print("\n[步骤2] 登录...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 3. 测试筛选列表API (书审和面谈分组列表)
print("\n" + "=" * 100)
print("[步骤3] 测试筛选列表API (/admin/registrations/filter)")
print("=" * 100)

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

items = filter_response.json()['data']

print(f"\n[API返回结果]")
print(f"  总记录数: {len(items)}")

# 统计返回的记录中草稿数量
draft_items = [item for item in items if item.get('submittedAt') is None]
submitted_items = [item for item in items if item.get('submittedAt') is not None]

print(f"  返回记录中有submittedAt的: {len(submitted_items)}")
print(f"  返回记录中无submittedAt的: {len(draft_items)}")

# 4. 测试面谈分组API
print("\n" + "=" * 100)
print("[步骤4] 测试面谈分组API (/admin/registrations/interview-groups)")
print("=" * 100)

interview_response = requests.get(
    f"{BASE_URL}/admin/registrations/interview-groups",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

groups = interview_response.json()['data']
total_items = sum(len(group['items']) for group in groups)

print(f"\n[API返回结果]")
print(f"  分组数: {len(groups)}")
print(f"  总记录数: {total_items}")

# 检查是否有草稿
all_items = []
for group in groups:
    all_items.extend(group['items'])

draft_in_groups = [item for item in all_items if item.get('submittedAt') is None]
print(f"  草稿记录数: {len(draft_in_groups)}")

# 5. 验证结果
print("\n" + "=" * 100)
print("[步骤5] 验证结果")
print("=" * 100)

print(f"\n[数据库对比]")
print(f"  数据库DRAFT状态: {db_stats.get('DRAFT', 0)} 条")
print(f"  数据库SUBMITTED状态: {db_stats.get('SUBMITTED', 0)} 条")

print(f"\n[筛选列表API]")
print(f"  应该返回: {db_stats.get('SUBMITTED', 0)} 条 (仅SUBMITTED)")
print(f"  实际返回: {len(items)} 条")

if len(items) == db_stats.get('SUBMITTED', 0):
    print(f"  [OK] 完全匹配！")
else:
    print(f"  [WARN] 数量不匹配")

if len(draft_items) == 0:
    print(f"  [OK] 没有草稿记录！")
else:
    print(f"  [ERROR] 仍有 {len(draft_items)} 条草稿记录")
    print(f"  草稿ID列表: {[item['registrationId'] for item in draft_items[:10]]}")

print(f"\n[面谈分组API]")
print(f"  应该返回: {db_stats.get('SUBMITTED', 0)} 条 (仅SUBMITTED)")
print(f"  实际返回: {total_items} 条")

if total_items == db_stats.get('SUBMITTED', 0):
    print(f"  [OK] 完全匹配！")
else:
    print(f"  [WARN] 数量不匹配")

if len(draft_in_groups) == 0:
    print(f"  [OK] 没有草稿记录！")
else:
    print(f"  [ERROR] 仍有 {len(draft_in_groups)} 条草稿记录")

# 6. 总结
print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)

if len(draft_items) == 0 and len(draft_in_groups) == 0:
    print(f"\n[SUCCESS] 草稿过滤功能正常！")
    print(f"  - 筛选列表API: 只返回SUBMITTED状态 (OK)")
    print(f"  - 面谈分组API: 只返回SUBMITTED状态 (OK)")
    print(f"  - 总共过滤掉: {db_stats.get('DRAFT', 0)} 条草稿记录")
else:
    print(f"\n[FAILED] 草稿过滤功能异常！")
    print(f"  - 筛选列表API中有 {len(draft_items)} 条草稿")
    print(f"  - 面谈分组API中有 {len(draft_in_groups)} 条草稿")

print("\n" + "=" * 100)
