#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准备书审测试数据"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("准备书审测试数据")
print("="*80)

# 1. 参赛者登录并创建报名
print("\n[1] 参赛者创建报名")
login = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13900000001",
    "name": "张医生",
    "role": "CONTESTANT"
})

if login.status_code != 200:
    print(f"登录失败: {login.status_code}")
    exit(1)

contestant_token = login.json()['data']['token']
contestant_id = login.json()['data']['id']
print(f"登录成功: ID={contestant_id}")

headers = {
    "Authorization": f"Bearer {contestant_token}",
    "Content-Type": "application/json"
}

# 2. 创建报名
print("\n[2] 创建报名")
reg = requests.post(f"{BASE}/api/registrations", headers=headers, json={
    "competitionId": 21,
    "institutionId": 1,
    "projectName": "优化门诊预约流程品管圈",
    "groupType": "BASIC"
})

if reg.status_code != 200:
    print(f"创建报名失败: {reg.status_code}")
    print(reg.text)
    exit(1)

reg_id = reg.json()['data']['id']
print(f"创建报名成功: ID={reg_id}")

# 3. 提交成员信息
print("\n[3] 提交成员信息")
members_resp = requests.put(f"{BASE}/api/registrations/{reg_id}/members", 
                            headers=headers, json={
    "members": [
        {
            "name": "张三",
            "title": "主管护师",
            "role": "PARTICIPANT",
            "department": "内科"
        },
        {
            "name": "李四",
            "title": "主治医师",
            "role": "PARTICIPANT",
            "department": "外科"
        },
        {
            "name": "王五",
            "title": "副主任护师",
            "role": "MENTOR"
        }
    ]
})

if members_resp.status_code == 200:
    print("提交成员信息成功")
else:
    print(f"提交成员信息失败: {members_resp.status_code}")
    print(members_resp.text)

# 4. 提交活动说明
print("\n[4] 提交活动说明")
activity_resp = requests.put(f"{BASE}/api/registrations/{reg_id}/activity", 
                             headers=headers, json={
    "theme": "提高门诊预约效率",
    "keywords": "门诊,预约,效率,优化",
    "subjectTypeCode": "subject_type_1",
    "methodCode": "PDCA",
    "experienceImproveCode": "experience_1",
    "qualityTopicCode": "quality_topic_1",
    "avgWorkYears": 6,
    "avgAge": 32,
    "crossDepartment": False
})

if activity_resp.status_code == 200:
    print("提交活动说明成功")
else:
    print(f"提交活动说明失败: {activity_resp.status_code}")
    print(activity_resp.text)

# 5. 提交项目总结
print("\n[5] 提交项目总结")
summary_resp = requests.put(f"{BASE}/api/registrations/{reg_id}/summary", 
                            headers=headers, json={
    "theme": "提高门诊预约效率",
    "plan": "通过流程优化和信息化手段，缩短患者预约等待时间，提升患者满意度",
    "problem": "现有预约系统效率低下，患者平均等待30分钟，高峰期甚至超过1小时",
    "action": "1.梳理预约流程，简化操作步骤\n2.优化系统界面，提高易用性\n3.增加预约渠道（微信、APP）\n4.培训工作人员，提升服务质量",
    "result": "预约等待时间从30分钟缩短至10分钟，缩短67%；患者满意度从75%提升至95%；年节省患者等待时间超过10000小时",
    "conclusion": "通过持续改进和团队协作，预约效率显著提升，患者体验明显改善，取得良好的社会效益和经济效益"
})

if summary_resp.status_code == 200:
    print("提交项目总结成功")
else:
    print(f"提交项目总结失败: {summary_resp.status_code}")
    print(summary_resp.text)

# 6. 提交报名
print("\n[6] 提交报名")
submit_resp = requests.post(f"{BASE}/api/registrations/{reg_id}/submit", 
                           headers=headers)

if submit_resp.status_code == 200:
    print("提交报名成功，状态变为SUBMITTED")
else:
    print(f"提交报名失败: {submit_resp.status_code}")
    print(submit_resp.text)

# 7. 组委会登录
print("\n[7] 组委会登录")
committee_login = requests.post(f"{BASE}/api/auth/login", json={
    "phone": "13800000009",
    "name": "组委会",
    "role": "COMMITTEE"
})

if committee_login.status_code != 200:
    print(f"组委会登录失败: {committee_login.status_code}")
    # 尝试用OPS角色
    committee_login = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000001",
        "name": "系统管理员",
        "role": "OPS"
    })

committee_token = committee_login.json()['data']['token']
print(f"组委会登录成功")

# 8. 获取评委ID（李明华）
print("\n[8] 获取评委列表")
committee_headers = {
    "Authorization": f"Bearer {committee_token}",
    "Content-Type": "application/json"
}

reviewers_resp = requests.get(f"{BASE}/api/admin/reviewers", 
                             headers=committee_headers)

if reviewers_resp.status_code == 200:
    reviewers = reviewers_resp.json()['data']
    reviewer = reviewers[0] if reviewers else None
    if reviewer:
        reviewer_id = reviewer['id']
        print(f"选择评委: {reviewer['name']} (ID={reviewer_id})")
    else:
        print("没有可用的评委")
        exit(1)
else:
    print(f"获取评委列表失败: {reviewers_resp.status_code}")
    print("使用默认评委ID: 3")
    reviewer_id = 3

# 9. 分配评审任务
print("\n[9] 分配评审任务")
task_resp = requests.post(f"{BASE}/api/reviews/tasks", 
                         headers=committee_headers, json={
    "registrationId": reg_id,
    "reviewerId": reviewer_id,
    "stage": "BOOK_REVIEW"
})

if task_resp.status_code == 200:
    task = task_resp.json()['data']
    task_id = task['id']
    print(f"分配任务成功: 任务ID={task_id}")
else:
    print(f"分配任务失败: {task_resp.status_code}")
    print(task_resp.text)

print("\n" + "="*80)
print("测试数据准备完成！")
print("="*80)
print(f"\n报名ID: {reg_id}")
print(f"评委ID: {reviewer_id}")
print(f"任务ID: {task_id if task_resp.status_code == 200 else '未创建'}")
print("\n评委可以用以下账号登录测试:")
print("手机号: 13800000021")
print("姓名: 李明华")
print("角色: REVIEWER")
print("\n然后调用以下API:")
print(f"1. GET /api/reviews/my-tasks - 查看任务列表")
print(f"2. GET /api/registrations/{reg_id} - 查看报名详情")
print(f"3. POST /api/reviews/scores - 提交评分")
