# -*- coding: utf-8 -*-
"""
对比不同API接口返回的label字段情况
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("对比不同API的label字段实现")
print("=" * 100)

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 1. 测试筛选列表API
print("\n[API 1] 筛选列表API: /admin/registrations/filter")
print("=" * 100)

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

filter_items = filter_response.json()['data']
if filter_items:
    first_filter = filter_items[0]
    print(f"\n第一条记录的label字段:")
    print(f"  registrationId: {first_filter.get('registrationId')}")
    print(f"  subjectTypeCode: {first_filter.get('subjectTypeCode')}")
    print(f"  subjectTypeLabel: {first_filter.get('subjectTypeLabel')}")
    print(f"  methodCode: {first_filter.get('methodCode')}")
    print(f"  methodLabel: {first_filter.get('methodLabel')}")
    
    # 检查label是否是中文
    subject_label = first_filter.get('subjectTypeLabel', '')
    method_label = first_filter.get('methodLabel', '')
    
    # 简单判断：如果包含中文字符或者label与code不同，说明是正确的
    is_subject_ok = subject_label and (subject_label != first_filter.get('subjectTypeCode'))
    is_method_ok = method_label and (method_label != first_filter.get('methodCode'))
    
    print(f"\n  Label状态:")
    print(f"    subjectTypeLabel: {'OK (有中文标签)' if is_subject_ok else 'ERROR (是code值)'}")
    print(f"    methodLabel: {'OK (有中文标签)' if is_method_ok else 'ERROR (是code值)'}")
    
    # 这个接口只返回了2个label，检查是否有其他label字段
    print(f"\n  包含的label字段:")
    for key in first_filter.keys():
        if 'Label' in key or 'label' in key:
            print(f"    - {key}: {first_filter[key]}")

# 2. 测试详情API
print("\n" + "=" * 100)
print("[API 2] 详情API: /api/registrations/{id}")
print("=" * 100)

# 获取第一条记录的ID
registration_id = filter_items[0]['registrationId'] if filter_items else 117

detail_response = requests.get(
    f"{BASE_URL}/registrations/{registration_id}",
    headers=headers,
    timeout=30
)

detail_data = detail_response.json()['data']
activity_info = detail_data.get('activityInfo', {})

print(f"\nactivityInfo 的所有label字段:")
print(f"  subjectTypeCode: {activity_info.get('subjectTypeCode')}")
print(f"  subjectTypeLabel: {activity_info.get('subjectTypeLabel')}")
print(f"  methodCode: {activity_info.get('methodCode')}")
print(f"  methodLabel: {activity_info.get('methodLabel')}")
print(f"  experienceImproveCode: {activity_info.get('experienceImproveCode')}")
print(f"  experienceImproveLabel: {activity_info.get('experienceImproveLabel')}")
print(f"  qualityTopicCode: {activity_info.get('qualityTopicCode')}")
print(f"  qualityTopicLabel: {activity_info.get('qualityTopicLabel')}")

# 检查每个label是否正确
labels = [
    ('subjectType', activity_info.get('subjectTypeCode'), activity_info.get('subjectTypeLabel')),
    ('method', activity_info.get('methodCode'), activity_info.get('methodLabel')),
    ('experienceImprove', activity_info.get('experienceImproveCode'), activity_info.get('experienceImproveLabel')),
    ('qualityTopic', activity_info.get('qualityTopicCode'), activity_info.get('qualityTopicLabel'))
]

print(f"\n  Label状态:")
for field_name, code, label in labels:
    if code and label:
        is_ok = label != code  # 如果label不等于code，说明做了转换
        status = 'OK (有中文标签)' if is_ok else 'ERROR (是code值)'
        print(f"    {field_name}Label: {status}")
        if not is_ok:
            print(f"      code={code}, label={label}")

# 3. 对比分析
print("\n" + "=" * 100)
print("[对比分析]")
print("=" * 100)

print(f"\n接口1: 筛选列表API (/admin/registrations/filter)")
print(f"  返回的label字段数: 2个 (subjectTypeLabel, methodLabel)")
print(f"  Label正确性: {'OK' if is_subject_ok and is_method_ok else 'ERROR'}")
print(f"  实现方式: 使用 getLabel() 方法查询字典表")

print(f"\n接口2: 详情API (/api/registrations/{{id}})")
print(f"  返回的label字段数: 4个 (subjectTypeLabel, methodLabel, experienceImproveLabel, qualityTopicLabel)")

error_count = 0
for field_name, code, label in labels:
    if code and label and label == code:
        error_count += 1

print(f"  Label正确性: {'ERROR' if error_count > 0 else 'OK'}")
print(f"  Label错误数: {error_count}/4")
print(f"  实现方式: 直接使用code作为label (未查询字典表)")

# 4. 问题定位
print("\n" + "=" * 100)
print("[问题定位]")
print("=" * 100)

print(f"\n发现的不一致:")
print(f"  1. filterRegistrations() 方法:")
print(f"     - 使用了 getLabel() 方法 (OK)")
print(f"     - 但只处理了 2 个字段 (subjectTypeLabel, methodLabel)")
print(f"     - 缺少: experienceImproveLabel, qualityTopicLabel")
print(f"")
print(f"  2. getDetail() 方法:")
print(f"     - 没有使用 getLabel() 方法 (ERROR)")
print(f"     - 直接把 code 赋值给 label")
print(f"     - 影响 4 个字段 (subjectTypeLabel, methodLabel, experienceImproveLabel, qualityTopicLabel)")
print(f"")
print(f"  3. StatsService 的方法:")
print(f"     - 应该是使用了 getLabel() (需要验证)")

# 5. 检查 RegistrationFilterItem 是否有其他label字段
print("\n" + "=" * 100)
print("[RegistrationFilterItem 字段结构]")
print("=" * 100)

if filter_items:
    print(f"\n包含的所有字段:")
    for key in sorted(first_filter.keys()):
        print(f"  - {key}")

print("\n" + "=" * 100)
print("[总结]")
print("=" * 100)

print(f"\n问题根源:")
print(f"  1. getDetail() 方法没有使用 getLabel() 查询")
print(f"  2. filterRegistrations() 方法只处理了部分label字段")
print(f"  3. 两个方法的实现不一致，导致'杂音'")

print(f"\n需要修复的方法:")
print(f"  1. getDetail() - 4个label字段全部需要修复")
print(f"  2. filterRegistrations() - 可能需要补充其他label字段（如果前端需要）")

print("\n" + "=" * 100)
