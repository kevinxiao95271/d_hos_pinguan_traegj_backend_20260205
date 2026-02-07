#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
所有分页API完整测试
验证5个API的分页功能
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
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Manager",
        "role": "OPS",
        "institutionId": 1
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"登录失败: {response.status_code}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_api_pagination(api_name, url, params_no_page, params_with_page, token):
    """通用分页测试"""
    print(f"【{api_name}】")
    print(f"URL: {url}")
    
    # 测试不分页
    print("\n  1️⃣  不分页查询...")
    response = requests.get(url, params=params_no_page, headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        data = response.json()["data"]
        data_type = type(data).__name__
        
        if isinstance(data, list):
            print(f"     ✓ 返回类型: {data_type} (数组)")
            print(f"     ✓ 数据量: {len(data)} 条")
            total_count = len(data)
        else:
            print(f"     ✗ 返回类型错误: {data_type}（应该是list）")
            return False
    else:
        print(f"     ✗ 请求失败: {response.status_code}")
        return False
    
    # 获取size参数
    page_size = params_with_page.get('size', 20)
    
    # 测试分页（第1页）
    print(f"\n  2️⃣  分页查询（第1页，size={page_size}）...")
    response = requests.get(url, params=params_with_page, headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        data = response.json()["data"]
        data_type = type(data).__name__
        
        if isinstance(data, dict):
            print(f"     ✓ 返回类型: {data_type} (对象)")
            print(f"     ✓ pageNo: {data.get('pageNo')}")
            print(f"     ✓ pageSize: {data.get('pageSize')}")
            print(f"     ✓ totalCount: {data.get('totalCount')}")
            print(f"     ✓ totalPages: {data.get('totalPages')}")
            print(f"     ✓ content数量: {len(data.get('content', []))}")
            
            # 验证
            if (data.get('pageNo') == 1 and 
                data.get('pageSize') == page_size and
                data.get('totalCount') == total_count):
                print(f"\n     ✅ 验证通过")
                return True
            else:
                print(f"\n     ✗ 验证失败（期望pageSize={page_size}，totalCount={total_count}）")
                return False
        else:
            print(f"     ✗ 返回类型错误: {data_type}（应该是dict）")
            return False
    else:
        print(f"     ✗ 请求失败: {response.status_code}")
        if response.status_code >= 500:
            try:
                print(f"     错误详情: {response.json()}")
            except:
                pass
        return False

def test_rankings(token):
    """测试1：评分排名列表（书审/面谈/决赛）"""
    print_section("测试1：评分排名列表分页")
    
    stages = {
        "BOOK": "书审阶段",
        "INTERVIEW": "面谈阶段",
        "FINAL": "决赛阶段"
    }
    
    results = []
    for stage_code, stage_name in stages.items():
        print(f"\n▶️  {stage_name}")
        
        result = test_api_pagination(
            api_name=f"{stage_name} - 评分排名",
            url=f"{BASE_URL}/api/admin/reviews/rankings",
            params_no_page={"competitionId": 21, "stage": stage_code},
            params_with_page={"competitionId": 21, "stage": stage_code, "page": 1, "size": 2},
            token=token
        )
        results.append(result)
    
    return all(results)

def test_shortlist(token):
    """测试2：入围管理列表"""
    print_section("测试2：入围管理列表分页")
    
    return test_api_pagination(
        api_name="入围管理",
        url=f"{BASE_URL}/api/admin/reviews/shortlist",
        params_no_page={"competitionId": 21, "stage": "BOOK"},
        params_with_page={"competitionId": 21, "stage": "BOOK", "page": 1, "size": 2},
        token=token
    )

def test_institutions(token):
    """测试3：机构管理列表"""
    print_section("测试3：机构管理列表分页")
    
    return test_api_pagination(
        api_name="机构管理",
        url=f"{BASE_URL}/api/admin/institutions",
        params_no_page={},
        params_with_page={"page": 1, "size": 5},
        token=token
    )

def test_review_tasks(token):
    """测试4：评审任务列表（已有分页）"""
    print_section("测试4：评审任务列表分页（已有）")
    
    return test_api_pagination(
        api_name="评审任务列表",
        url=f"{BASE_URL}/api/reviews/tasks/stage",
        params_no_page={"competitionId": 21, "stage": "BOOK"},
        params_with_page={"competitionId": 21, "stage": "BOOK", "page": 1, "size": 2},
        token=token
    )

def test_registrations(token):
    """测试5：报名筛选列表（已有分页）"""
    print_section("测试5：报名筛选列表分页（已有）")
    
    return test_api_pagination(
        api_name="报名筛选",
        url=f"{BASE_URL}/api/admin/registrations/filter",
        params_no_page={"competitionId": 21},
        params_with_page={"competitionId": 21, "page": 1, "size": 5},
        token=token
    )

def main():
    print_section("所有分页API完整测试")
    
    if not wait_for_server():
        print("服务器未启动，测试终止")
        return
    
    try:
        token = login()
        print("✓ 登录成功（OPS角色）\n")
        
        results = []
        
        # 测试所有API
        results.append(("评分排名列表", test_rankings(token)))
        results.append(("入围管理列表", test_shortlist(token)))
        results.append(("机构管理列表", test_institutions(token)))
        results.append(("评审任务列表", test_review_tasks(token)))
        results.append(("报名筛选列表", test_registrations(token)))
        
        # 汇总结果
        print_section("测试结果汇总")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print("API分页功能测试结果:\n")
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status}  {name}")
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("\n🎉 所有API分页功能测试通过！")
            print("\n已支持分页的API列表：")
            print("  1. GET /api/admin/reviews/rankings - 评分排名（书审/面谈/决赛）")
            print("  2. GET /api/admin/reviews/shortlist - 入围管理列表")
            print("  3. GET /api/admin/institutions - 机构管理列表")
            print("  4. GET /api/reviews/tasks/stage - 评审任务列表")
            print("  5. GET /api/admin/registrations/filter - 报名筛选列表")
        else:
            print(f"\n⚠️  有 {total - passed} 个API测试失败，请检查。")
        
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
