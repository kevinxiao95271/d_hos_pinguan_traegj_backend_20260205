# -*- coding: utf-8 -*-
"""
测试修复后的 label 是否正确返回
"""
import requests
import pymysql

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试修复后的 label 是否正确返回")
print("=" * 100)

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 连接数据库找一条使用 internet_diagnosis 的记录
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

# 测试1: internet_diagnosis (已修复)
print("\n[测试1] internet_diagnosis (已修复的字典项)")
print("-" * 100)

cursor.execute("""
    SELECT r.id, r.project_name, ai.experience_improve_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE ai.experience_improve_code = 'internet_diagnosis'
    LIMIT 1
""")

record = cursor.fetchone()

if record:
    reg_id = record['id']
    print(f"\n  找到记录: registration_id={reg_id}, project={record['project_name'][:50]}")
    print(f"  experience_improve_code: {record['experience_improve_code']}")
    
    # 调用 API
    detail_response = requests.get(
        f"{BASE_URL}/registrations/{reg_id}",
        headers=headers,
        timeout=30
    )
    
    activity_info = detail_response.json()['data'].get('activityInfo', {})
    
    print(f"\n  API 返回:")
    print(f"    experienceImproveCode: {activity_info.get('experienceImproveCode')}")
    print(f"    experienceImproveLabel: {activity_info.get('experienceImproveLabel')}")
    
    expected_label = "互联网诊疗更加可及"
    actual_label = activity_info.get('experienceImproveLabel')
    
    if actual_label == expected_label:
        print(f"\n  [OK] Label 正确: {actual_label}")
    else:
        print(f"\n  [ERROR] Label 错误!")
        print(f"    期望: {expected_label}")
        print(f"    实际: {actual_label}")
else:
    print("\n  [SKIP] 未找到使用 internet_diagnosis 的记录")

# 测试2: experience_improve_20260205144626 (尚未修复)
print(f"\n{'=' * 100}")
print("[测试2] experience_improve_20260205144626 (错误的字典项)")
print("-" * 100)

cursor.execute("""
    SELECT r.id, r.project_name, ai.experience_improve_code
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    WHERE ai.experience_improve_code = 'experience_improve_20260205144626'
    LIMIT 1
""")

record = cursor.fetchone()

if record:
    reg_id = record['id']
    print(f"\n  找到记录: registration_id={reg_id}, project={record['project_name'][:50]}")
    print(f"  experience_improve_code: {record['experience_improve_code']}")
    
    # 调用 API
    detail_response = requests.get(
        f"{BASE_URL}/registrations/{reg_id}",
        headers=headers,
        timeout=30
    )
    
    activity_info = detail_response.json()['data'].get('activityInfo', {})
    
    print(f"\n  API 返回:")
    print(f"    experienceImproveCode: {activity_info.get('experienceImproveCode')}")
    print(f"    experienceImproveLabel: {activity_info.get('experienceImproveLabel')}")
    
    # 这个应该还是错误的
    actual_label = activity_info.get('experienceImproveLabel')
    if actual_label == 'experience_improve 20260205144626':
        print(f"\n  [预期] Label 仍然错误 (待修复): {actual_label}")
    else:
        print(f"\n  [意外] Label 内容: {actual_label}")
else:
    print("\n  [SKIP] 未找到使用 experience_improve_20260205144626 的记录")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

print(f"\n  internet_diagnosis 的修复:")
print(f"    [OK] 字典表已更新为'互联网诊疗更加可及'")
print(f"    需要测试 API 返回是否正确")

print(f"\n  experience_improve_20260205144626 的问题:")
print(f"    [TODO] 仍需处理这8条记录和错误的字典项")

print(f"\n{'=' * 100}")
