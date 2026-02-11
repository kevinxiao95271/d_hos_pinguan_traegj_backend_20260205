#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PostgreSQL迁移后的端到端API测试"""

import requests
import json

BASE_URL = "http://localhost:6031"

# 测试账号（混淆后的手机号）
TEST_ACCOUNTS = {
    'contestants': [
        {'phone': '13799999112', 'name': '王建国', 'role': 'CONTESTANT'},
        {'phone': '13966000890', 'name': '参赛者1', 'role': 'CONTESTANT'},
        {'phone': '13965999231', 'name': '参赛者2', 'role': 'CONTESTANT'},
        {'phone': '13966000430', 'name': '参赛者3', 'role': 'CONTESTANT'},
        {'phone': '13965999424', 'name': '参赛者4', 'role': 'CONTESTANT'},
    ],
    'reviewers': [
        {'phone': '13900000001', 'name': '王建国', 'role': 'REVIEWER'},
        {'phone': '13800000084', 'name': '李明华', 'role': 'REVIEWER'},
        {'phone': '13800000406', 'name': 'Reviewer B', 'role': 'REVIEWER'},
    ],
    'admins': [
        {'phone': '13800000127', 'name': 'CommitteeAdmin A', 'role': 'COMMITTEE_ADMIN'},
        {'phone': '13799999971', 'name': 'CommitteeAdmin B', 'role': 'COMMITTEE_ADMIN'},
    ],
    'ops': [
        {'phone': '13800000005', 'name': 'OPS User 1', 'role': 'OPS'},
        {'phone': '13800000027', 'name': 'OPS User 2', 'role': 'OPS'},
    ]
}

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_login(account):
    """测试登录"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=account)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            return result['data']['token']
    return None

def test_contestant_apis():
    """测试参赛者API"""
    print_section("【场景1】参赛者功能测试")
    
    account = TEST_ACCOUNTS['contestants'][0]
    print(f"\n使用账号: {account['name']} ({account['phone']})")
    
    # 1. 登录
    print("\n1. 登录...")
    token = test_login(account)
    if not token:
        print("❌ 登录失败")
        return False
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 查询我的报名
    print("\n2. 查询我的报名...")
    response = requests.get(f"{BASE_URL}/api/registrations/my", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            registrations = result['data']
            print(f"✅ 查询成功: {len(registrations)} 个报名")
            if registrations:
                reg = registrations[0]
                print(f"   项目: {reg.get('projectName')}")
                print(f"   机构: {reg.get('institutionName')}")
                return True
        else:
            print(f"❌ 查询失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    return False

def test_reviewer_apis():
    """测试评委API"""
    print_section("【场景2】评委功能测试")
    
    account = TEST_ACCOUNTS['reviewers'][0]
    print(f"\n使用账号: {account['name']} ({account['phone']})")
    
    # 1. 登录
    print("\n1. 登录...")
    token = test_login(account)
    if not token:
        print("❌ 登录失败")
        return False
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 查询我的评审任务
    print("\n2. 查询我的评审任务...")
    response = requests.get(f"{BASE_URL}/api/reviews/my-tasks", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            tasks = result['data']
            print(f"✅ 查询成功: {len(tasks)} 个任务")
            if tasks:
                task = tasks[0]
                print(f"   项目: {task.get('projectName')}")
                print(f"   机构: {task.get('institutionName')}")
                print(f"   状态: {task.get('status')}")
            return True
        else:
            print(f"❌ 查询失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    return False

def test_admin_apis():
    """测试组委会管理员API"""
    print_section("【场景3】组委会管理员功能测试")
    
    account = TEST_ACCOUNTS['admins'][0]
    print(f"\n使用账号: {account['name']} ({account['phone']})")
    
    # 1. 登录
    print("\n1. 登录...")
    token = test_login(account)
    if not token:
        print("❌ 登录失败")
        return False
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 查询报名统计
    print("\n2. 查询报名统计...")
    response = requests.get(f"{BASE_URL}/api/admin/stats/summary?competitionId=21", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            stats = result['data']
            print(f"✅ 查询成功")
            print(f"   赛事: {stats.get('competitionName')}")
            print(f"   报名数: {stats.get('registrationCount')}")
            print(f"   评委数: {stats.get('reviewerCount')}")
            print(f"   平均Plan分: {stats.get('avgPlan')}")
            
            # 验证新增字段
            if 'methodCounts' in stats:
                print(f"   品管工具分布: {len(stats['methodCounts'])} 种")
            if 'leaderTitleCounts' in stats:
                print(f"   负责人职称分布: {len(stats['leaderTitleCounts'])} 种")
            
            return True
        else:
            print(f"❌ 查询失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    return False

def test_data_integrity():
    """测试数据完整性"""
    print_section("【场景4】数据完整性测试")
    
    account = TEST_ACCOUNTS['admins'][0]
    token = test_login(account)
    if not token:
        print("❌ 登录失败")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 测试小数分值
    print("\n1. 测试小数分值支持...")
    response = requests.get(f"{BASE_URL}/api/admin/stats/summary?competitionId=21", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            stats = result['data']
            avg_plan = stats.get('avgPlan')
            if isinstance(avg_plan, (int, float)):
                print(f"✅ 小数分值正常: avgPlan = {avg_plan} (类型: {type(avg_plan).__name__})")
            else:
                print(f"❌ 小数分值异常: {avg_plan}")
                return False
    
    # 2. 测试机构等级字段
    print("\n2. 测试机构等级字段...")
    response = requests.get(f"{BASE_URL}/api/admin/registrations/filter?competitionId=21&stage=BOOK", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            items = result['data']
            if items:
                item = items[0]
                if 'institutionLevel' in item:
                    print(f"✅ 机构等级字段存在: {item.get('institutionLevel')}")
                else:
                    print("⚠️  机构等级字段不存在")
    
    # 3. 测试项目负责人职称统计
    print("\n3. 测试项目负责人职称统计...")
    response = requests.get(f"{BASE_URL}/api/admin/stats/summary?competitionId=21", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            stats = result['data']
            if 'leaderTitleCounts' in stats:
                title_counts = stats['leaderTitleCounts']
                print(f"✅ 职称统计字段存在: {len(title_counts)} 种职称")
                # 显示前3个
                for i, (title, count) in enumerate(list(title_counts.items())[:3]):
                    print(f"   {title}: {count}")
            else:
                print("❌ 职称统计字段不存在")
                return False
    
    return True

def test_all_logins():
    """测试所有账号登录"""
    print_section("【场景5】所有账号登录测试")
    
    all_success = True
    
    for role_name, accounts in TEST_ACCOUNTS.items():
        print(f"\n测试 {role_name}:")
        for account in accounts:
            token = test_login(account)
            status = "✅" if token else "❌"
            print(f"  {status} {account['name']:<20} ({account['phone']})")
            if not token:
                all_success = False
    
    return all_success

def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("PostgreSQL迁移后 - 端到端API测试")
    print("=" * 80)
    
    print("\n测试账号清单:")
    print(f"  参赛者: {len(TEST_ACCOUNTS['contestants'])} 个")
    print(f"  评委: {len(TEST_ACCOUNTS['reviewers'])} 个")
    print(f"  组委会管理员: {len(TEST_ACCOUNTS['admins'])} 个")
    print(f"  系统维护员: {len(TEST_ACCOUNTS['ops'])} 个")
    
    results = []
    
    # 执行测试
    results.append(("所有账号登录", test_all_logins()))
    results.append(("参赛者功能", test_contestant_apis()))
    results.append(("评委功能", test_reviewer_apis()))
    results.append(("组委会管理员功能", test_admin_apis()))
    results.append(("数据完整性", test_data_integrity()))
    
    # 总结
    print_section("测试总结")
    
    print(f"\n{'测试项':<30} {'结果':<10}")
    print("-" * 42)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:<30} {status:<10}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print("-" * 42)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！PostgreSQL迁移成功！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
