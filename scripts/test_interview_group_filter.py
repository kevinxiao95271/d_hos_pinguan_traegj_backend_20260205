# -*- coding: utf-8 -*-
"""
测试面谈分组只返回进阶组（ADVANCED）
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
print("测试面谈分组 - 仅返回进阶组（ADVANCED）")
print("=" * 100)

# 1. 检查数据库中各组别的统计
print("\n[步骤1] 检查数据库中各组别的统计...")

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        group_type,
        status,
        COUNT(*) as count
    FROM registrations
    GROUP BY group_type, status
    ORDER BY group_type, status
""")

print("\n[数据库统计 - 按组别和状态]")
db_stats = {}
for row in cursor.fetchall():
    group_type, status, count = row
    key = f"{group_type}_{status}"
    db_stats[key] = count
    print(f"  {group_type} + {status}: {count} 条")

# 统计SUBMITTED状态的各组别数量
cursor.execute("""
    SELECT 
        group_type,
        COUNT(*) as count
    FROM registrations
    WHERE status = 'SUBMITTED'
    GROUP BY group_type
    ORDER BY group_type
""")

print("\n[数据库统计 - SUBMITTED状态]")
submitted_by_type = {}
for row in cursor.fetchall():
    group_type, count = row
    submitted_by_type[group_type] = count
    print(f"  {group_type}: {count} 条")

cursor.close()
conn.close()

# 2. 登录
print("\n[步骤2] 登录...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 3. 测试面谈分组API
print("\n" + "=" * 100)
print("[步骤3] 测试面谈分组API (/admin/registrations/interview-groups)")
print("=" * 100)

interview_response = requests.get(
    f"{BASE_URL}/admin/registrations/interview-groups",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

if interview_response.status_code != 200:
    print(f"[ERROR] 请求失败: {interview_response.status_code}")
    print(interview_response.text)
    exit(1)

groups = interview_response.json()['data']

print(f"\n[API返回结果]")
print(f"  分组数: {len(groups)}")

# 统计所有返回的记录
all_items = []
for group in groups:
    all_items.extend(group['items'])

print(f"  总记录数: {len(all_items)}")

# 按 groupType 统计
type_count = {}
for item in all_items:
    group_type = item['groupType']
    type_count[group_type] = type_count.get(group_type, 0) + 1

print(f"\n[返回记录的组别分布]")
for group_type, count in sorted(type_count.items()):
    print(f"  {group_type}: {count} 条")

# 4. 验证是否只包含ADVANCED
print("\n" + "=" * 100)
print("[步骤4] 验证结果")
print("=" * 100)

basic_count = type_count.get('BASIC', 0)
comprehensive_count = type_count.get('COMPREHENSIVE', 0)
advanced_count = type_count.get('ADVANCED', 0)

print(f"\n[组别验证]")
print(f"  BASIC (基层组): {basic_count} 条")
print(f"  COMPREHENSIVE (综合组): {comprehensive_count} 条")
print(f"  ADVANCED (进阶组): {advanced_count} 条")

if basic_count == 0 and comprehensive_count == 0:
    print(f"\n  [OK] 基层组和综合组已正确过滤！")
else:
    print(f"\n  [ERROR] 仍包含基层组或综合组的记录！")

# 验证数量是否匹配
expected_count = submitted_by_type.get('ADVANCED', 0)
if advanced_count == expected_count:
    print(f"\n[数量验证]")
    print(f"  数据库中ADVANCED+SUBMITTED: {expected_count} 条")
    print(f"  API返回ADVANCED: {advanced_count} 条")
    print(f"  [OK] 数量完全匹配！")
else:
    print(f"\n[数量验证]")
    print(f"  数据库中ADVANCED+SUBMITTED: {expected_count} 条")
    print(f"  API返回ADVANCED: {advanced_count} 条")
    print(f"  [WARN] 数量不匹配")

# 5. 显示分组详情
print("\n" + "=" * 100)
print("[步骤5] 分组详情")
print("=" * 100)

for group in groups:
    print(f"\n分组: {group['groupCode']}")
    print(f"  记录数: {len(group['items'])}")
    if group['items']:
        first_item = group['items'][0]
        print(f"  示例记录:")
        print(f"    - ID: {first_item['registrationId']}")
        print(f"    - 项目: {first_item['projectName'][:40]}...")
        print(f"    - 机构: {first_item['institutionName'][:30]}...")
        print(f"    - 组别: {first_item['groupType']}")

# 6. 总结
print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)

if basic_count == 0 and comprehensive_count == 0 and advanced_count == expected_count:
    print(f"\n[SUCCESS] 面谈分组过滤功能正常！")
    print(f"  - 只返回ADVANCED (进阶组): {advanced_count} 条")
    print(f"  - 过滤掉BASIC (基层组): {submitted_by_type.get('BASIC', 0)} 条")
    print(f"  - 过滤掉COMPREHENSIVE (综合组): {submitted_by_type.get('COMPREHENSIVE', 0)} 条")
    print(f"  - 与数据库数据完全匹配")
else:
    print(f"\n[FAILED] 面谈分组过滤功能异常！")
    if basic_count > 0:
        print(f"  - 仍包含 {basic_count} 条基层组记录")
    if comprehensive_count > 0:
        print(f"  - 仍包含 {comprehensive_count} 条综合组记录")
    if advanced_count != expected_count:
        print(f"  - 进阶组数量不匹配")

print("\n" + "=" * 100)
