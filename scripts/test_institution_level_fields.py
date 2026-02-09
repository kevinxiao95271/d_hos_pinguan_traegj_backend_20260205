#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试机构等级字段是否返回"""

import requests
import json

BASE_URL = "http://localhost:6031/api"

def login(phone, name, role):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": phone,
        "name": name,
        "role": role
    })
    if response.status_code == 200:
        return response.json()['data']['token']
    else:
        print(f"登录失败: {response.text}")
        return None

def test_registration_detail(token, registration_id):
    """测试报名详情API - GET /api/registrations/{id}"""
    print(f"\n{'='*60}")
    print(f"测试 API 1: GET /api/registrations/{registration_id}")
    print(f"{'='*60}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations/{registration_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()['data']
        institution = data.get('institution', {})
        
        print(f"✓ API调用成功")
        print(f"机构信息:")
        print(f"  - 机构名称: {institution.get('name')}")
        print(f"  - 机构等级: {institution.get('level')}")
        
        if institution.get('level'):
            print(f"✅ institutionLevel字段已返回: {institution.get('level')}")
            return True
        else:
            print(f"❌ institutionLevel字段缺失或为空")
            return False
    else:
        print(f"✗ API调用失败: {response.status_code}")
        print(f"  {response.text}")
        return False

def test_my_registrations(token):
    """测试我的报名列表API - GET /api/registrations/my"""
    print(f"\n{'='*60}")
    print(f"测试 API 2: GET /api/registrations/my")
    print(f"{'='*60}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/registrations/my", headers=headers)
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✓ API调用成功，返回 {len(data)} 条记录")
        
        if len(data) > 0:
            first_item = data[0]
            print(f"第一条记录:")
            print(f"  - 项目名称: {first_item.get('projectName')}")
            print(f"  - 机构名称: {first_item.get('institutionName')}")
            print(f"  - 机构等级: {first_item.get('institutionLevel')}")
            
            if first_item.get('institutionLevel'):
                print(f"✅ institutionLevel字段已返回: {first_item.get('institutionLevel')}")
                return True
            else:
                print(f"❌ institutionLevel字段缺失或为空")
                return False
        else:
            print(f"⚠️  无数据，无法验证")
            return None
    else:
        print(f"✗ API调用失败: {response.status_code}")
        print(f"  {response.text}")
        return False

def test_admin_filter(token, competition_id=23):
    """测试书审分组列表API - GET /api/admin/registrations/filter"""
    print(f"\n{'='*60}")
    print(f"测试 API 3: GET /api/admin/registrations/filter")
    print(f"{'='*60}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        params={"competitionId": competition_id},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✓ API调用成功，返回 {len(data)} 条记录")
        
        if len(data) > 0:
            first_item = data[0]
            print(f"第一条记录:")
            print(f"  - 项目名称: {first_item.get('projectName')}")
            print(f"  - 机构名称: {first_item.get('institutionName')}")
            print(f"  - 机构等级: {first_item.get('institutionLevel')}")
            
            if first_item.get('institutionLevel'):
                print(f"✅ institutionLevel字段已返回: {first_item.get('institutionLevel')}")
                return True
            else:
                print(f"❌ institutionLevel字段缺失或为空")
                return False
        else:
            print(f"⚠️  无数据，无法验证")
            return None
    else:
        print(f"✗ API调用失败: {response.status_code}")
        print(f"  {response.text}")
        return False

def test_review_tasks(token):
    """测试评委任务列表API - GET /api/reviews/my-tasks"""
    print(f"\n{'='*60}")
    print(f"测试 API 4: GET /api/reviews/my-tasks")
    print(f"{'='*60}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reviews/my-tasks", headers=headers)
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✓ API调用成功，返回 {len(data)} 条记录")
        
        if len(data) > 0:
            first_item = data[0]
            print(f"第一条记录:")
            print(f"  - 项目名称: {first_item.get('projectName')}")
            print(f"  - 机构名称: {first_item.get('institutionName')}")
            print(f"  - 机构等级: {first_item.get('institutionLevel')}")
            
            if first_item.get('institutionLevel'):
                print(f"✅ institutionLevel字段已返回: {first_item.get('institutionLevel')}")
                return True
            else:
                print(f"❌ institutionLevel字段缺失或为空")
                return False
        else:
            print(f"⚠️  无数据，无法验证")
            return None
    else:
        print(f"✗ API调用失败: {response.status_code}")
        print(f"  {response.text}")
        return False

def main():
    print("="*60)
    print("机构等级字段测试")
    print("="*60)
    
    results = {}
    
    # 测试1: 参赛者 - 报名详情
    print("\n场景1: 参赛者查看报名详情")
    contestant_token = login("13800000001", "张三", "CONTESTANT")
    if contestant_token:
        results['registration_detail'] = test_registration_detail(contestant_token, 119)
    
    # 测试2: 参赛者 - 我的报名列表
    print("\n场景2: 参赛者查看我的报名列表")
    if contestant_token:
        results['my_registrations'] = test_my_registrations(contestant_token)
    
    # 测试3: 管理员 - 书审分组列表
    print("\n场景3: 管理员查看书审分组列表")
    admin_token = login("13900000001", "管理员", "COMMITTEE")
    if admin_token:
        results['admin_filter'] = test_admin_filter(admin_token)
    
    # 测试4: 评委 - 评委任务列表
    print("\n场景4: 评委查看任务列表")
    reviewer_token = login("13700000001", "李明华", "REVIEWER")
    if reviewer_token:
        results['review_tasks'] = test_review_tasks(reviewer_token)
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    for api, result in results.items():
        status = "✅ 通过" if result else ("❌ 失败" if result is False else "⚠️  无数据")
        print(f"{api}: {status}")
    
    all_passed = all(r is True for r in results.values() if r is not None)
    if all_passed:
        print(f"\n🎉 所有API测试通过！机构等级字段已正确返回")
    else:
        print(f"\n⚠️  部分API测试失败或无数据")

if __name__ == '__main__':
    main()
