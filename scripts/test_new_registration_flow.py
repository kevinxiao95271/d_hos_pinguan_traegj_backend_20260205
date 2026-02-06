#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试新报名流程：创建、填写、提交"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
from datetime import datetime

BASE = "http://localhost:6031"

print("="*80)
print("测试完整报名流程")
print("="*80)

# 使用一个新的测试账号
test_phone = f"139{datetime.now().strftime('%H%M%S')}"  # 生成唯一手机号
test_name = f"测试参赛者-{datetime.now().strftime('%H%M%S')}"

print(f"\n[1] 注册/登录新账号")
print("-" * 80)
print(f"手机号: {test_phone}")
print(f"姓名: {test_name}")

try:
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": test_phone,
        "name": test_name,
        "role": "CONTESTANT",
        "institutionId": 1  # 浙江大学医学院附属第一医院
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"响应: {login_resp.text}")
        exit(1)
    
    login_data = login_resp.json()['data']
    token = login_data['token']
    user_id = login_data['id']
    
    print(f"✅ 登录成功")
    print(f"   用户ID: {user_id}")
    print(f"   姓名: {login_data['name']}")
    print(f"   机构: {login_data.get('institutionName', '未设置')}")
    
except Exception as e:
    print(f"❌ 登录异常: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. 创建报名
print(f"\n[2] 创建报名（草稿状态）")
print("-" * 80)

try:
    create_resp = requests.post(f"{BASE}/api/registrations", json={
        "competitionId": 21,  # 2026浙江品管大赛（现在可报名）
        "projectName": "智能导诊系统优化项目",
        "groupType": "COMPREHENSIVE",
        "institutionId": 1
    }, headers=headers, timeout=10)
    
    if create_resp.status_code != 200:
        print(f"❌ 创建失败: {create_resp.status_code}")
        print(f"响应: {create_resp.text}")
        exit(1)
    
    registration = create_resp.json()['data']
    registration_id = registration['id']
    
    print(f"✅ 创建成功")
    print(f"   报名ID: {registration_id}")
    print(f"   项目名称: {registration['projectName']}")
    print(f"   状态: {registration['status']}")
    
except Exception as e:
    print(f"❌ 创建异常: {e}")
    exit(1)

# 3. 更新项目基本信息
print(f"\n[3] 更新项目基本信息")
print("-" * 80)

try:
    update_resp = requests.put(f"{BASE}/api/registrations/{registration_id}", json={
        "projectName": "智能导诊系统优化与患者满意度提升",
        "groupType": "COMPREHENSIVE",
        "institutionId": 1
    }, headers=headers, timeout=10)
    
    if update_resp.status_code != 200:
        print(f"❌ 更新失败: {update_resp.status_code}")
        print(f"响应: {update_resp.text}")
        exit(1)
    
    print(f"✅ 更新成功")
    print(f"   项目名称已更新")
    
except Exception as e:
    print(f"❌ 更新异常: {e}")
    exit(1)

# 4. 添加成员信息
print(f"\n[4] 添加成员信息")
print("-" * 80)

try:
    members_resp = requests.put(f"{BASE}/api/registrations/{registration_id}/members", json={
        "registrationId": registration_id,
        "members": [
            {
                "name": "王主任",
                "title": "主任医师",
                "department": "门诊部",
                "role": "MENTOR"
            },
            {
                "name": "李护士长",
                "title": "主管护师",
                "department": "门诊部",
                "role": "PARTICIPANT"
            },
            {
                "name": "张医生",
                "title": "主治医师",
                "department": "门诊部",
                "role": "PARTICIPANT"
            }
        ]
    }, headers=headers, timeout=10)
    
    if members_resp.status_code != 200:
        print(f"❌ 添加成员失败: {members_resp.status_code}")
        print(f"响应: {members_resp.text}")
        exit(1)
    
    members = members_resp.json()['data']
    print(f"✅ 添加成员成功")
    print(f"   共 {len(members)} 名成员")
    for m in members:
        print(f"   - {m['name']} ({m['role']}) - {m['title']}")
    
except Exception as e:
    print(f"❌ 添加成员异常: {e}")
    exit(1)

# 5. 填写活动说明
print(f"\n[5] 填写活动说明")
print("-" * 80)

try:
    activity_resp = requests.put(f"{BASE}/api/registrations/{registration_id}/activity", json={
        "registrationId": registration_id,
        "theme": "提高门诊导诊效率，提升患者就医体验",
        "keywords": "智能导诊,患者满意度,流程优化",
        "subjectTypeCode": "subject_type_1",
        "methodCode": "PDCA",
        "experienceImproveCode": "experience_1",
        "qualityTopicCode": "quality_topic_1",
        "avgWorkYears": 8,
        "avgAge": 35,
        "crossDepartment": False
    }, headers=headers, timeout=10)
    
    if activity_resp.status_code != 200:
        print(f"❌ 填写活动说明失败: {activity_resp.status_code}")
        print(f"响应: {activity_resp.text[:500]}")
        exit(1)
    
    print(f"✅ 填写活动说明成功")
    
except Exception as e:
    print(f"❌ 填写活动说明异常: {e}")
    exit(1)

# 6. 查看报名详情
print(f"\n[6] 查看完整报名信息")
print("-" * 80)

try:
    detail_resp = requests.get(f"{BASE}/api/registrations/{registration_id}", headers=headers, timeout=10)
    
    if detail_resp.status_code != 200:
        print(f"❌ 获取详情失败: {detail_resp.status_code}")
        exit(1)
    
    detail_data = detail_resp.json()['data']
    reg = detail_data.get('registration', {})
    members = detail_data.get('members', [])
    activity = detail_data.get('activity', {})
    
    print(f"✅ 报名详情:")
    print(f"   报名ID: {reg.get('id')}")
    print(f"   项目名称: {reg.get('projectName')}")
    print(f"   组别: {reg.get('groupType')}")
    print(f"   状态: {reg.get('status')}")
    print(f"   成员数: {len(members)}")
    if activity:
        print(f"   主题: {activity.get('theme', 'N/A')}")
        print(f"   关键词: {activity.get('keywords', 'N/A')}")
    
except Exception as e:
    print(f"❌ 获取详情异常: {e}")
    exit(1)

# 7. 提交报名
print(f"\n[7] 提交报名")
print("-" * 80)

confirm = input("是否提交报名？提交后将无法修改 (y/n): ")
if confirm.lower() == 'y':
    try:
        submit_resp = requests.post(
            f"{BASE}/api/registrations/{registration_id}/submit", 
            headers=headers, 
            timeout=10
        )
        
        if submit_resp.status_code != 200:
            print(f"❌ 提交失败: {submit_resp.status_code}")
            print(f"响应: {submit_resp.text}")
            exit(1)
        
        submitted_reg = submit_resp.json()['data']
        print(f"✅ 提交成功")
        print(f"   状态: {submitted_reg['status']}")
        print(f"   提交时间: {submitted_reg.get('submittedAt', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        exit(1)
else:
    print("跳过提交，保持草稿状态")

# 8. 最终报名列表
print(f"\n[8] 查看我的报名列表")
print("-" * 80)

try:
    my_resp = requests.get(f"{BASE}/api/registrations/my", headers=headers, timeout=10)
    
    if my_resp.status_code != 200:
        print(f"❌ 获取报名列表失败: {my_resp.status_code}")
        exit(1)
    
    registrations = my_resp.json()['data']
    print(f"✅ 共 {len(registrations)} 个报名:")
    for r in registrations:
        print(f"   - ID {r['id']}: {r['projectName']} - {r['status']}")
    
except Exception as e:
    print(f"❌ 获取报名列表异常: {e}")
    exit(1)

print("\n" + "="*80)
print("测试完成！")
print("="*80)
print(f"\n📋 测试账号信息:")
print(f"   手机号: {test_phone}")
print(f"   姓名: {test_name}")
print(f"   报名ID: {registration_id}")
print(f"\n💡 提示: 您可以使用此账号登录前端查看报名详情")
