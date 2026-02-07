#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分页功能测试
验证页码从1开始，并返回正确的分页信息
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:6031"

def wait_for_server():
    """等待服务器启动"""
    print("等待服务器启动...")
    for i in range(15):
        try:
            response = requests.get(f"{BASE_URL}/api/competitions", timeout=3)
            if response.status_code in [200, 401]:
                print(f"✓ 服务器已启动 (尝试 {i+1}/15)\n")
                return True
        except:
            pass
        time.sleep(4)
    print("✗ 服务器启动超时\n")
    return False

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800138001",
        "name": "Li Minghua",
        "title": "Professor",
        "role": "REVIEWER",
        "institutionId": 2
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"登录失败: {response.status_code}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_no_pagination(token):
    """测试1：不分页（兼容旧版）"""
    print_section("测试1：不分页查询 - 兼容性测试")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  返回类型: {type(data).__name__}")
        
        if isinstance(data, list):
            print(f"  ✓ 返回数组格式（兼容旧版）")
            print(f"  数据量: {len(data)} 条")
            if len(data) > 0:
                print(f"  首条数据包含字段: {', '.join(data[0].keys())}")
            return True
        else:
            print(f"  ✗ 返回格式错误，应该是数组")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_first_page(token):
    """测试2：第1页（页码从1开始）"""
    print_section("测试2：分页查询 - 第1页（pageNo=1）")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK", "page": 1, "size": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  返回类型: {type(data).__name__}")
        
        if isinstance(data, dict):
            print(f"  ✓ 返回对象格式（分页）")
            print(f"\n  分页信息:")
            print(f"    pageNo: {data.get('pageNo')} {'✓ 正确（从1开始）' if data.get('pageNo') == 1 else '✗ 错误'}")
            print(f"    pageSize: {data.get('pageSize')}")
            print(f"    totalCount: {data.get('totalCount')}")
            print(f"    totalPages: {data.get('totalPages')}")
            print(f"    hasNext: {data.get('hasNext')}")
            print(f"    hasPrevious: {data.get('hasPrevious')}")
            print(f"    content数量: {len(data.get('content', []))}")
            
            # 验证
            if data.get('pageNo') == 1 and len(data.get('content', [])) == 2:
                print(f"\n  ✓ 验证通过：页码正确，返回2条数据")
                return True
            else:
                print(f"\n  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 返回格式错误，应该是对象")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_second_page(token):
    """测试3：第2页"""
    print_section("测试3：分页查询 - 第2页（pageNo=2）")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK", "page": 2, "size": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"\n  分页信息:")
        print(f"    pageNo: {data.get('pageNo')} {'✓ 正确' if data.get('pageNo') == 2 else '✗ 错误'}")
        print(f"    pageSize: {data.get('pageSize')}")
        print(f"    totalCount: {data.get('totalCount')}")
        print(f"    content数量: {len(data.get('content', []))}")
        print(f"    hasPrevious: {data.get('hasPrevious')} {'✓ 正确（有上一页）' if data.get('hasPrevious') else '✗ 错误'}")
        
        if data.get('pageNo') == 2 and data.get('hasPrevious'):
            print(f"\n  ✓ 验证通过")
            return True
        else:
            print(f"\n  ✗ 验证失败")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_registration_filter_pagination(token):
    """测试4：报名筛选分页"""
    print_section("测试4：报名筛选 - 分页查询")
    
    # 不分页
    response1 = requests.get(
        f"{BASE_URL}/api/admin/registrations/filter",
        params={"competitionId": 21},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 分页
    response2 = requests.get(
        f"{BASE_URL}/api/admin/registrations/filter",
        params={"competitionId": 21, "page": 1, "size": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]
        
        print(f"不分页:")
        print(f"  返回类型: {type(data1).__name__}")
        print(f"  数据量: {len(data1)} 条")
        
        print(f"\n分页（第1页，每页5条）:")
        print(f"  返回类型: {type(data2).__name__}")
        if isinstance(data2, dict):
            print(f"  pageNo: {data2.get('pageNo')}")
            print(f"  pageSize: {data2.get('pageSize')}")
            print(f"  totalCount: {data2.get('totalCount')}")
            print(f"  content数量: {len(data2.get('content', []))}")
        
        if isinstance(data1, list) and isinstance(data2, dict) and data2.get('pageNo') == 1:
            print(f"\n  ✓ 验证通过：兼容性良好")
            return True
        else:
            print(f"\n  ✗ 验证失败")
            return False
    else:
        print(f"✗ 请求失败")
        return False

def test_page_zero_should_be_first_page(token):
    """测试5：page=0应该被当作第1页"""
    print_section("测试5：边界测试 - page=0")
    
    response = requests.get(
        f"{BASE_URL}/api/reviews/tasks/stage",
        params={"competitionId": 21, "stage": "BOOK", "page": 0, "size": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  pageNo: {data.get('pageNo')}")
        print(f"  说明: page=0 被当作第1页")
        
        if data.get('pageNo') == 1:
            print(f"  ✓ 验证通过：page=0 自动转换为 page=1")
            return True
        else:
            print(f"  ✗ 验证失败")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def main():
    print_section("分页功能完整测试")
    
    if not wait_for_server():
        print("服务器未启动，测试终止")
        return
    
    try:
        token = login()
        print("✓ 登录成功\n")
        
        results = []
        results.append(("不分页查询", test_no_pagination(token)))
        results.append(("第1页查询", test_first_page(token)))
        results.append(("第2页查询", test_second_page(token)))
        results.append(("报名筛选分页", test_registration_filter_pagination(token)))
        results.append(("边界测试page=0", test_page_zero_should_be_first_page(token)))
        
        print_section("测试结果汇总")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"  {status}  {name}")
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！分页功能正常工作。")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")
        
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
