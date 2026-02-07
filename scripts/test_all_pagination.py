#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面测试所有分页功能
包括：评分排名、入围管理、机构列表
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
    """登录获取token（REVIEWER角色）"""
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

def login_ops():
    """登录获取OPS角色token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Administrator",
        "role": "OPS",
        "institutionId": 1
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"OPS登录失败: {response.status_code}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_rankings_no_pagination(token):
    """测试1：评分排名 - 不分页（兼容性）"""
    print_section("测试1：评分排名 - 不分页（兼容性）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/rankings",
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
                print(f"  首条: rank={data[0].get('rank')}, projectName={data[0].get('projectName')}, avgTotal={data[0].get('avgTotal')}")
            return True
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_rankings_pagination(token):
    """测试2：评分排名 - 分页"""
    print_section("测试2：评分排名 - 分页（第1页，每页3条）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/rankings",
        params={"competitionId": 21, "stage": "BOOK", "page": 1, "size": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  返回类型: {type(data).__name__}")
        
        if isinstance(data, dict):
            print(f"  ✓ 返回对象格式（分页）")
            print(f"\n  分页信息:")
            print(f"    pageNo: {data.get('pageNo')}")
            print(f"    pageSize: {data.get('pageSize')}")
            print(f"    totalCount: {data.get('totalCount')}")
            print(f"    totalPages: {data.get('totalPages')}")
            print(f"    hasNext: {data.get('hasNext')}")
            print(f"    hasPrevious: {data.get('hasPrevious')}")
            print(f"    content数量: {len(data.get('content', []))}")
            
            if len(data.get('content', [])) > 0:
                item = data['content'][0]
                print(f"\n  首条数据: rank={item.get('rank')}, avgTotal={item.get('avgTotal')}")
            
            # 验证：页码正确且content数量<=pageSize
            if data.get('pageNo') == 1 and len(data.get('content', [])) <= 3:
                print(f"\n  ✓ 验证通过")
                return True
            else:
                print(f"\n  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_shortlist_limit_mode(token):
    """测试3：入围管理 - limit模式（兼容性）"""
    print_section("测试3：入围管理 - limit模式（前5名）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/shortlist",
        params={"competitionId": 21, "stage": "BOOK", "limit": 5},
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
                print(f"  首条: rank={data[0].get('rank')}, avgTotal={data[0].get('avgTotal')}")
            
            if len(data) <= 5:
                print(f"\n  ✓ 验证通过：返回不超过5条")
                return True
            else:
                print(f"\n  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_shortlist_pagination(token):
    """测试4：入围管理 - 分页模式"""
    print_section("测试4：入围管理 - 分页模式（第1页，每页2条）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/shortlist",
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
            print(f"    pageNo: {data.get('pageNo')}")
            print(f"    pageSize: {data.get('pageSize')}")
            print(f"    totalCount: {data.get('totalCount')}")
            print(f"    content数量: {len(data.get('content', []))}")
            
            if data.get('pageNo') == 1 and len(data.get('content', [])) == 2:
                print(f"\n  ✓ 验证通过")
                return True
            else:
                print(f"\n  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_shortlist_with_filter(token):
    """测试5：入围管理 - 分数线筛选+分页"""
    print_section("测试5：入围管理 - 分数线筛选（>=80分）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/reviews/shortlist",
        params={"competitionId": 21, "stage": "BOOK", "minAvgTotal": 80, "page": 1, "size": 10},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        
        if isinstance(data, dict):
            content = data.get('content', [])
            print(f"  符合条件的项目数: {data.get('totalCount')}")
            print(f"  当前页项目数: {len(content)}")
            
            # 检查所有项目分数是否>=80
            all_above_80 = all(item.get('avgTotal', 0) >= 80 for item in content)
            if all_above_80:
                print(f"  ✓ 验证通过：所有项目分数都>=80")
                return True
            else:
                print(f"  ✗ 验证失败：有项目分数<80")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_institutions_no_pagination(token):
    """测试6：机构列表 - 不分页（兼容性）"""
    print_section("测试6：机构列表 - 不分页（兼容性）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/institutions",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  返回类型: {type(data).__name__}")
        
        if isinstance(data, list):
            print(f"  ✓ 返回数组格式（兼容旧版）")
            print(f"  机构总数: {len(data)} 个")
            if len(data) > 0:
                print(f"  首条: id={data[0].get('id')}, name={data[0].get('name')}")
            return True
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_institutions_pagination(token):
    """测试7：机构列表 - 分页"""
    print_section("测试7：机构列表 - 分页（第1页，每页5条）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/institutions",
        params={"page": 1, "size": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        print(f"  返回类型: {type(data).__name__}")
        
        if isinstance(data, dict):
            print(f"  ✓ 返回对象格式（分页）")
            print(f"\n  分页信息:")
            print(f"    pageNo: {data.get('pageNo')}")
            print(f"    pageSize: {data.get('pageSize')}")
            print(f"    totalCount: {data.get('totalCount')}")
            print(f"    content数量: {len(data.get('content', []))}")
            
            if data.get('pageNo') == 1 and len(data.get('content', [])) <= 5:
                print(f"\n  ✓ 验证通过")
                return True
            else:
                print(f"\n  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_institutions_with_filter(token):
    """测试8：机构列表 - 筛选+分页"""
    print_section("测试8：机构列表 - 名称筛选（包含'医院'）")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/institutions",
        params={"name": "医院", "page": 1, "size": 10},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ 请求成功")
        
        if isinstance(data, dict):
            content = data.get('content', [])
            print(f"  符合条件的机构数: {data.get('totalCount')}")
            print(f"  当前页机构数: {len(content)}")
            
            # 检查所有机构名称是否包含"医院"
            all_contain_hospital = all('医院' in item.get('name', '') for item in content)
            if all_contain_hospital or len(content) == 0:
                print(f"  ✓ 验证通过：所有机构名称都包含'医院'")
                return True
            else:
                print(f"  ✗ 验证失败：有机构名称不包含'医院'")
                return False
        else:
            print(f"  ✗ 返回格式错误")
            return False
    else:
        print(f"✗ 请求失败：{response.status_code}")
        return False

def test_all_stages(token):
    """测试9：所有评审阶段的评分排名"""
    print_section("测试9：所有评审阶段（BOOK/INTERVIEW/FINAL）")
    
    stages = ["BOOK", "INTERVIEW", "FINAL"]
    results = {}
    
    for stage in stages:
        response = requests.get(
            f"{BASE_URL}/api/admin/reviews/rankings",
            params={"competitionId": 21, "stage": stage, "page": 1, "size": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            if isinstance(data, dict):
                totalCount = data.get('totalCount', 0)
                results[stage] = totalCount
                print(f"  ✓ {stage:12} - 分页正常, 总数: {totalCount}")
            else:
                results[stage] = None
                print(f"  ✗ {stage:12} - 返回格式错误")
        else:
            results[stage] = None
            print(f"  ✗ {stage:12} - 请求失败")
    
    all_passed = all(v is not None for v in results.values())
    if all_passed:
        print(f"\n  ✓ 验证通过：所有阶段都支持分页")
        return True
    else:
        print(f"\n  ✗ 验证失败：部分阶段不支持分页")
        return False

def main():
    print_section("所有分页功能完整测试")
    
    if not wait_for_server():
        print("服务器未启动，测试终止")
        return
    
    try:
        token = login()
        print("✓ 登录成功（REVIEWER）\n")
        
        # 尝试获取OPS token用于机构管理测试
        ops_token = None
        try:
            ops_token = login_ops()
            print("✓ OPS登录成功\n")
        except:
            print("⚠️  OPS登录失败，机构管理测试将跳过\n")
        
        results = []
        results.append(("评分排名-不分页", test_rankings_no_pagination(token)))
        results.append(("评分排名-分页", test_rankings_pagination(token)))
        results.append(("入围管理-limit模式", test_shortlist_limit_mode(token)))
        results.append(("入围管理-分页模式", test_shortlist_pagination(token)))
        results.append(("入围管理-分数筛选", test_shortlist_with_filter(token)))
        
        if ops_token:
            results.append(("机构列表-不分页", test_institutions_no_pagination(ops_token)))
            results.append(("机构列表-分页", test_institutions_pagination(ops_token)))
            results.append(("机构列表-名称筛选", test_institutions_with_filter(ops_token)))
        else:
            print("⚠️  跳过机构管理测试（需要OPS权限）\n")
        
        results.append(("所有评审阶段", test_all_stages(token)))
        
        print_section("测试结果汇总")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"  {status}  {name}")
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！所有分页功能正常工作。")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")
        
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
