#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试所有场景的报名详情显示"""

import requests
import json

BASE_URL = "http://localhost:6031"

def login(role):
    """登录不同角色"""
    users = {
        "CONTESTANT": {"phone": "13800000001", "name": "张三", "role": "CONTESTANT"},
        "COMMITTEE_ADMIN": {"phone": "13800000041", "name": "CommitteeAdmin A", "role": "COMMITTEE_ADMIN"},
        "REVIEWER": {"phone": "13900000001", "name": "李明华", "role": "REVIEWER"}
    }
    
    url = f"{BASE_URL}/api/auth/login"
    data = users[role]
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result.get("data", {}).get("token")
    return None

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def check_fields(data, scenario):
    """检查字段完整性"""
    print(f"\n【{scenario}】字段检查")
    print("-" * 100)
    
    # 检查基本信息
    registration = data.get("registration", {})
    print(f"\n1. 报名基本信息:")
    print(f"   - ID: {registration.get('id')}")
    print(f"   - 项目名称: {registration.get('projectName')}")
    print(f"   - 组别: {registration.get('groupType')}")
    print(f"   - 状态: {registration.get('status')}")
    
    # 检查机构信息
    institution = data.get("institution", {})
    print(f"\n2. 机构信息:")
    print(f"   - 机构名称: {institution.get('name')}")
    print(f"   - 机构等级: {institution.get('level', '未设置')}")
    print(f"   - 地区: {institution.get('region')}")
    
    # 检查活动信息（重点）
    activity = data.get("activityInfo", {})
    if activity:
        print(f"\n3. 活动信息（10个字段）:")
        print(f"   ✅ 活动主题: {activity.get('theme', '无')}")
        print(f"   ✅ 关键词: {activity.get('keywords', '无')}")
        print(f"   ✅ 主题类型: {activity.get('subjectTypeCode', '无')} ({activity.get('subjectTypeLabel', '无')})")
        print(f"   ✅ 运用手法: {activity.get('methodCode', '无')} ({activity.get('methodLabel', '无')})")
        print(f"   ✅ 改善就医环境: {activity.get('experienceImproveCode', '无')}")
        print(f"   ✅ 医疗质量主题: {activity.get('qualityTopicCode', '无')}")
        print(f"   ✅ 平均工作年限: {activity.get('avgWorkYears', '无')} 年")
        print(f"   ✅ 平均年龄: {activity.get('avgAge', '无')} 岁")
        print(f"   ✅ 是否跨部门: {'是' if activity.get('crossDepartment') else '否'}")
        print(f"   ✅ 是否与数字化/AI相关: {'是' if activity.get('relatedToDigitalAi') else '否'}")
    else:
        print(f"\n3. 活动信息: ❌ 无数据")
    
    # 检查项目摘要（重点）
    summary = data.get("projectSummary", {})
    if summary:
        print(f"\n4. 项目摘要（7个字段）:")
        print(f"   ✅ 主题: {summary.get('theme', '无')[:50]}...")
        print(f"   ✅ 计划: {'有' if summary.get('plan') else '无'}")
        print(f"   ✅ 问题: {'有' if summary.get('problem') else '无'}")
        print(f"   ✅ 行动: {'有' if summary.get('action') else '无'}")
        print(f"   ✅ 成效: {'有' if summary.get('success') else '无'}")
        print(f"   ✅ 讨论: {'有' if summary.get('discussion') else '无'}")
        print(f"   ✅ 运作: {'有' if summary.get('operation') else '无'}")
        print(f"   ✅ 展示: {'有' if summary.get('presentation') else '无'}")
    else:
        print(f"\n4. 项目摘要: ❌ 无数据")
    
    # 检查成员信息
    members = data.get("members", [])
    print(f"\n5. 成员信息: {len(members)} 人")
    
    # 检查材料
    materials = data.get("materials", [])
    print(f"\n6. 材料信息: {len(materials)} 个文件")
    
    return activity is not None and summary is not None

def scenario_1_my_registration():
    """场景1: 参赛者 - 我的报名"""
    print_section("场景1: 参赛者 - 我的报名")
    
    token = login("CONTESTANT")
    if not token:
        print("❌ 登录失败")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取我的报名列表
    url = f"{BASE_URL}/api/registrations/my"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取报名列表失败: HTTP {response.status_code}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return False
    
    registrations = result.get("data", [])
    if not registrations:
        print("⚠️  没有报名数据")
        return False
    
    print(f"\n找到 {len(registrations)} 个报名")
    
    # 查看第一个报名的详情
    reg_id = registrations[0].get("id")
    detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
    detail_response = requests.get(detail_url, headers=headers)
    
    if detail_response.status_code == 200:
        detail_result = detail_response.json()
        if detail_result.get("success"):
            data = detail_result.get("data", {})
            return check_fields(data, "参赛者查看我的报名详情")
    
    return False

def scenario_2_admin_book_review():
    """场景2: 组委会管理员 - 书审分组项目列表"""
    print_section("场景2: 组委会管理员 - 书审分组项目列表")
    
    token = login("COMMITTEE_ADMIN")
    if not token:
        print("❌ 登录失败")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取分组项目列表
    url = f"{BASE_URL}/api/admin/registrations/grouped?competitionId=23"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取分组列表失败: HTTP {response.status_code}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return False
    
    groups = result.get("data", [])
    if not groups:
        print("⚠️  没有分组数据")
        return False
    
    print(f"\n找到 {len(groups)} 个分组")
    
    # 获取第一个分组的第一个项目
    first_group = groups[0]
    items = first_group.get("items", [])
    if not items:
        print("⚠️  分组中没有项目")
        return False
    
    reg_id = items[0].get("id")
    print(f"\n查看项目ID: {reg_id}")
    
    # 查看项目详情
    detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
    detail_response = requests.get(detail_url, headers=headers)
    
    if detail_response.status_code == 200:
        detail_result = detail_response.json()
        if detail_result.get("success"):
            data = detail_result.get("data", {})
            return check_fields(data, "组委会管理员查看书审分组项目详情")
    
    return False

def scenario_3_admin_filter():
    """场景3: 组委会管理员 - 分组项目列表（筛选）"""
    print_section("场景3: 组委会管理员 - 分组项目列表（筛选）")
    
    token = login("COMMITTEE_ADMIN")
    if not token:
        print("❌ 登录失败")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取筛选项目列表
    url = f"{BASE_URL}/api/admin/registrations/filter?competitionId=23"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取项目列表失败: HTTP {response.status_code}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return False
    
    registrations = result.get("data", [])
    if not registrations:
        print("⚠️  没有项目数据")
        return False
    
    print(f"\n找到 {len(registrations)} 个项目")
    
    # 查看第一个项目的详情
    reg_id = registrations[0].get("id")
    print(f"\n查看项目ID: {reg_id}")
    
    detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
    detail_response = requests.get(detail_url, headers=headers)
    
    if detail_response.status_code == 200:
        detail_result = detail_response.json()
        if detail_result.get("success"):
            data = detail_result.get("data", {})
            return check_fields(data, "组委会管理员查看筛选项目详情")
    
    return False

def scenario_4_reviewer_tasks():
    """场景4: 评委 - 查看分派的评审任务"""
    print_section("场景4: 评委 - 查看分派的评审任务")
    
    token = login("REVIEWER")
    if not token:
        print("❌ 登录失败")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取评审任务列表
    url = f"{BASE_URL}/api/reviews/my-tasks?competitionId=23"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取任务列表失败: HTTP {response.status_code}")
        return False
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return False
    
    tasks = result.get("data", [])
    if not tasks:
        print("⚠️  没有评审任务")
        return False
    
    print(f"\n找到 {len(tasks)} 个评审任务")
    
    # 查看第一个任务的项目详情
    task = tasks[0]
    reg_id = task.get("registrationId")
    print(f"\n查看任务关联的项目ID: {reg_id}")
    
    detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
    detail_response = requests.get(detail_url, headers=headers)
    
    if detail_response.status_code == 200:
        detail_result = detail_response.json()
        if detail_result.get("success"):
            data = detail_result.get("data", {})
            return check_fields(data, "评委查看评审任务项目详情")
    
    return False

def main():
    """主函数"""
    print("\n" + "=" * 100)
    print("报名详情字段完整性测试 - 所有场景")
    print("=" * 100)
    
    results = []
    
    # 场景1: 参赛者 - 我的报名
    results.append(("场景1: 参赛者 - 我的报名", scenario_1_my_registration()))
    
    # 场景2: 组委会管理员 - 书审分组项目列表
    results.append(("场景2: 组委会管理员 - 书审分组项目列表", scenario_2_admin_book_review()))
    
    # 场景3: 组委会管理员 - 分组项目列表（筛选）
    results.append(("场景3: 组委会管理员 - 分组项目列表", scenario_3_admin_filter()))
    
    # 场景4: 评委 - 查看分派的评审任务
    results.append(("场景4: 评委 - 查看评审任务", scenario_4_reviewer_tasks()))
    
    # 汇总结果
    print_section("测试结果汇总")
    for scenario, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {scenario}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 所有场景测试通过！")
    else:
        print("\n⚠️  部分场景测试失败，请检查数据或接口")

if __name__ == "__main__":
    main()
