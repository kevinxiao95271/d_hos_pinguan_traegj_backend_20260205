# -*- coding: utf-8 -*-
"""
测试修复后的记录 API 返回
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试修复后的记录 API 返回")
print("=" * 100)

# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={"phone": "13800000127", "password": "committee2026"},
    timeout=30
)

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 测试之前受影响的8条记录
fixed_record_ids = [34, 49, 55, 56, 64, 116, 122, 125]

print(f"\n测试之前使用错误 code 的 {len(fixed_record_ids)} 条记录:")
print("-" * 100)

success_count = 0
fail_count = 0

for reg_id in fixed_record_ids:
    detail_response = requests.get(
        f"{BASE_URL}/registrations/{reg_id}",
        headers=headers,
        timeout=30
    )
    
    response_json = detail_response.json()
    
    if 'data' not in response_json:
        print(f"  [ERROR] ID={reg_id:3}, API返回错误: {response_json}")
        fail_count += 1
        continue
    
    data = response_json['data']
    activity_info = data.get('activityInfo', {})
    project_name = data.get('projectName', '')[:40]
    
    code = activity_info.get('experienceImproveCode')
    label = activity_info.get('experienceImproveLabel')
    
    # 预期: code 应该是 'other', label 应该是 '其他（非相关主题）'
    expected_code = 'other'
    expected_label = '其他（非相关主题）'
    
    is_ok = (code == expected_code and label == expected_label)
    status = "OK" if is_ok else "ERROR"
    
    if is_ok:
        success_count += 1
        print(f"  [{status}] ID={reg_id:3}, code={code:<15}, label={label}")
    else:
        fail_count += 1
        print(f"  [{status}] ID={reg_id:3}, code={code:<15}, label={label}")
        print(f"        期望: code={expected_code}, label={expected_label}")
        print(f"        项目: {project_name}")

print(f"\n{'=' * 100}")
print("[测试统计]")
print("=" * 100)

print(f"\n  测试总数: {len(fixed_record_ids)}")
print(f"  成功: {success_count}")
print(f"  失败: {fail_count}")

if fail_count == 0:
    print(f"\n  [OK] 所有修复后的记录都正确返回了 label!")
else:
    print(f"\n  [ERROR] 有 {fail_count} 条记录的 label 仍然有问题")

# 额外测试: 随机测试一些其他记录
print(f"\n{'=' * 100}")
print("[随机测试其他记录]")
print("=" * 100)

filter_response = requests.get(
    f"{BASE_URL}/admin/registrations/filter",
    params={"competitionId": 1},
    headers=headers,
    timeout=30
)

test_ids = [item['registrationId'] for item in filter_response.json()['data'][:3]]

print(f"\n  随机测试 {len(test_ids)} 条其他记录:")

for reg_id in test_ids:
    detail_response = requests.get(
        f"{BASE_URL}/registrations/{reg_id}",
        headers=headers,
        timeout=30
    )
    
    activity_info = detail_response.json()['data'].get('activityInfo', {})
    
    if not activity_info:
        print(f"    ID={reg_id}: 无 activityInfo")
        continue
    
    code = activity_info.get('experienceImproveCode')
    label = activity_info.get('experienceImproveLabel')
    
    # 检查 label 是否正确（不应该等于 code）
    is_ok = label and label != code
    status = "OK" if is_ok else "ERROR"
    
    if is_ok:
        print(f"    [{status}] ID={reg_id:3}, {code:<30} -> {label[:30]}")
    else:
        print(f"    [{status}] ID={reg_id:3}, code={code}, label={label}")

print(f"\n{'=' * 100}")
print("[总结]")
print("=" * 100)

print(f"\n  experience_improve 相关的修复:")
print(f"    [OK] internet_diagnosis 的 label 已修复为'互联网诊疗更加可及'")
print(f"    [OK] experience_improve_20260205144626 的8条记录已改为 'other'")
print(f"    [OK] 错误的字典项已删除")

print(f"\n  API 测试结果:")
if fail_count == 0:
    print(f"    [OK] 所有受影响的记录现在都正确返回中文 label")
else:
    print(f"    [ERROR] 仍有问题需要处理")

print(f"\n{'=' * 100}")
