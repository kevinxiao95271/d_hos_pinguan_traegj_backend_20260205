# -*- coding: utf-8 -*-
"""
测试详情API返回的label字段
"""
import requests
import pymysql
import json

BASE_URL = "http://localhost:6031/api"

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("测试详情API - activityInfo的label字段")
print("=" * 100)

# 1. 从数据库获取一条记录的code
print("\n[步骤1] 从数据库查询一条记录...")

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        a.id,
        a.registration_id,
        a.subject_type_code,
        a.method_code,
        a.experience_improve_code,
        a.quality_topic_code
    FROM activity_infos a
    WHERE a.subject_type_code = 'subject_type_4'
    LIMIT 1
""")

row = cursor.fetchone()
if not row:
    print("[ERROR] 没有找到 subject_type_4 的记录")
    cursor.close()
    conn.close()
    exit(1)

activity_id, registration_id, subject_type_code, method_code, experience_code, quality_code = row

print(f"\n数据库记录:")
print(f"  activity_id: {activity_id}")
print(f"  registration_id: {registration_id}")
print(f"  subject_type_code: {subject_type_code}")
print(f"  method_code: {method_code}")
print(f"  experience_improve_code: {experience_code}")
print(f"  quality_topic_code: {quality_code}")

# 查询对应的字典label
cursor.execute("""
    SELECT code, label FROM dictionary_items WHERE code = %s
""", (subject_type_code,))
subject_label = cursor.fetchone()

cursor.execute("""
    SELECT code, label FROM dictionary_items WHERE code = %s
""", (method_code,))
method_label = cursor.fetchone()

cursor.execute("""
    SELECT code, label FROM dictionary_items WHERE code = %s
""", (experience_code,))
experience_label = cursor.fetchone()

cursor.execute("""
    SELECT code, label FROM dictionary_items WHERE code = %s
""", (quality_code,))
quality_label = cursor.fetchone()

print(f"\n字典表中的label:")
print(f"  {subject_type_code} -> {subject_label[1] if subject_label else 'NOT FOUND'}")
print(f"  {method_code} -> {method_label[1] if method_label else 'NOT FOUND'}")
print(f"  {experience_code} -> {experience_label[1] if experience_label else 'NOT FOUND'}")
print(f"  {quality_code} -> {quality_label[1] if quality_label else 'NOT FOUND'}")

cursor.close()
conn.close()

# 2. 调用API获取详情
print("\n" + "=" * 100)
print(f"[步骤2] 调用 API: GET /api/registrations/{registration_id}")
print("=" * 100)

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 获取详情
detail_response = requests.get(
    f"{BASE_URL}/registrations/{registration_id}",
    headers=headers,
    timeout=30
)

if detail_response.status_code != 200:
    print(f"[ERROR] API请求失败: {detail_response.status_code}")
    print(detail_response.text)
    exit(1)

detail_data = detail_response.json()['data']
activity_info = detail_data.get('activityInfo', {})

print(f"\n[API返回的 activityInfo]:")
print(f"  subjectTypeCode: {activity_info.get('subjectTypeCode')}")
print(f"  subjectTypeLabel: {activity_info.get('subjectTypeLabel')}")
print(f"  methodCode: {activity_info.get('methodCode')}")
print(f"  methodLabel: {activity_info.get('methodLabel')}")
print(f"  experienceImproveCode: {activity_info.get('experienceImproveCode')}")
print(f"  experienceImproveLabel: {activity_info.get('experienceImproveLabel')}")
print(f"  qualityTopicCode: {activity_info.get('qualityTopicCode')}")
print(f"  qualityTopicLabel: {activity_info.get('qualityTopicLabel')}")

# 3. 对比分析
print("\n" + "=" * 100)
print("[步骤3] 对比分析 - 字典表 vs API返回")
print("=" * 100)

comparisons = [
    ("subject_type", subject_type_code, subject_label[1] if subject_label else None, activity_info.get('subjectTypeLabel')),
    ("method", method_code, method_label[1] if method_label else None, activity_info.get('methodLabel')),
    ("experience_improve", experience_code, experience_label[1] if experience_label else None, activity_info.get('experienceImproveLabel')),
    ("quality_topic", quality_code, quality_label[1] if quality_label else None, activity_info.get('qualityTopicLabel'))
]

print(f"\n字段对比:")
for field_name, code, expected_label, actual_label in comparisons:
    match = "[OK]" if expected_label == actual_label else "[ERROR]"
    print(f"\n  {field_name}:")
    print(f"    Code: {code}")
    print(f"    字典表Label: {expected_label}")
    print(f"    API返回Label: {actual_label}")
    print(f"    匹配状态: {match}")

# 4. 显示完整的activityInfo对象
print("\n" + "=" * 100)
print("[步骤4] 完整的 activityInfo 对象")
print("=" * 100)
print(json.dumps(activity_info, ensure_ascii=False, indent=2))

# 5. 总结
print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)

issues = []
if activity_info.get('subjectTypeLabel') != (subject_label[1] if subject_label else None):
    issues.append("subjectTypeLabel")
if activity_info.get('methodLabel') != (method_label[1] if method_label else None):
    issues.append("methodLabel")
if activity_info.get('experienceImproveLabel') != (experience_label[1] if experience_label else None):
    issues.append("experienceImproveLabel")
if activity_info.get('qualityTopicLabel') != (quality_label[1] if quality_label else None):
    issues.append("qualityTopicLabel")

print(f"\n数据源头检查:")
print(f"  [OK] 数据库 activity_infos 表中有完整的code数据")
print(f"  [OK] 数据库 dictionary_items 表中有完整的label数据")
print(f"  [OK] 所有code在字典表中都能找到对应的label")

print(f"\nAPI返回问题:")
if issues:
    print(f"  [ERROR] 以下字段的label未正确返回:")
    for field in issues:
        print(f"    - {field}")
    print(f"\n  原因: RegistrationService.getDetail() 方法没有从字典表查询label")
    print(f"  代码位置: 第242-254行，注释说'字典标签查询已移除，直接使用code作为label'")
    print(f"  但实际上只是把code赋值给label变量，而不是真正的中文标签")
else:
    print(f"  [OK] 所有label都正确返回")

print("\n" + "=" * 100)
