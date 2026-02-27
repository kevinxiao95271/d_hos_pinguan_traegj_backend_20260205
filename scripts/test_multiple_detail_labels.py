# -*- coding: utf-8 -*-
"""
测试多条记录的详情API label字段
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试多条记录的详情API label字段")
print("=" * 100)

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 获取几条不同的记录ID
filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

registration_ids = [item['registrationId'] for item in filter_response.json()['data'][:5]]

print(f"\n测试 {len(registration_ids)} 条记录:")
print(f"Registration IDs: {registration_ids}")

success_count = 0
fail_count = 0

for reg_id in registration_ids:
    print(f"\n{'=' * 100}")
    print(f"[记录 {reg_id}]")
    print(f"{'=' * 100}")
    
    detail_response = requests.get(
        f"{BASE_URL}/registrations/{reg_id}",
        headers=headers,
        timeout=30
    )
    
    activity_info = detail_response.json()['data'].get('activityInfo', {})
    
    if not activity_info:
        print("  [SKIP] 无 activityInfo 数据")
        continue
    
    # 检查每个label字段
    labels_to_check = [
        ('subjectType', activity_info.get('subjectTypeCode'), activity_info.get('subjectTypeLabel')),
        ('method', activity_info.get('methodCode'), activity_info.get('methodLabel')),
        ('experienceImprove', activity_info.get('experienceImproveCode'), activity_info.get('experienceImproveLabel')),
        ('qualityTopic', activity_info.get('qualityTopicCode'), activity_info.get('qualityTopicLabel'))
    ]
    
    record_ok = True
    
    for field_name, code, label in labels_to_check:
        if code:  # 只检查有code值的字段
            # 判断label是否正确（不应该等于code）
            is_ok = label and label != code
            status = 'OK' if is_ok else 'ERROR'
            
            if is_ok:
                # 显示简短信息
                print(f"  {field_name}: [{status}] {code} -> {label[:20]}{'...' if len(label) > 20 else ''}")
            else:
                # 错误时显示完整信息
                print(f"  {field_name}: [{status}] code={code}, label={label}")
                record_ok = False
    
    if record_ok:
        success_count += 1
        print(f"\n  [结果] OK - 所有label字段正确")
    else:
        fail_count += 1
        print(f"\n  [结果] ERROR - 有label字段返回了code值")

print(f"\n{'=' * 100}")
print(f"[汇总统计]")
print(f"{'=' * 100}")
print(f"\n  测试总数: {len(registration_ids)}")
print(f"  成功: {success_count}")
print(f"  失败: {fail_count}")

if fail_count == 0:
    print(f"\n  [OK] 所有记录的label字段都正确返回中文标签！")
else:
    print(f"\n  [ERROR] 仍有 {fail_count} 条记录的label字段有问题")

print(f"\n{'=' * 100}")
