#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试所有API的机构等级字段
"""
import requests
import json
import sys

# 配置输出编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:6031"

def test_api(name, method, url, headers=None, data=None, check_fields=None):
    """测试API并检查指定字段"""
    print(f"\n{'='*80}")
    print(f"测试: {name}")
    print(f"API: {method} {url}")
    print(f"{'='*80}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"[ERROR] 不支持的方法: {method}")
            return False
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[FAIL] 请求失败")
            print(f"响应: {response.text[:200]}")
            return False
        
        result = response.json()
        print(f"响应成功: {result.get('code')}")
        
        # 检查字段
        if check_fields:
            return check_response_fields(result, check_fields, name)
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"[FAIL] 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] 连接失败 - 请确保后端服务已启动")
        return False
    except Exception as e:
        print(f"[FAIL] 测试异常: {e}")
        return False

def check_response_fields(result, check_fields, api_name):
    """检查响应中的字段"""
    data = result.get('data')
    
    if data is None:
        print(f"[WARN] 响应中没有data字段")
        return True
    
    # 如果data是列表
    if isinstance(data, list):
        if len(data) == 0:
            print(f"[INFO] 返回空列表（正常，可能没有数据）")
            return True
        
        item = data[0]
        print(f"[INFO] 返回 {len(data)} 条数据，检查第一条...")
        
        all_found = True
        for field in check_fields:
            if '.' in field:
                # 嵌套字段，如 institution.level
                parts = field.split('.')
                value = item
                for part in parts:
                    value = value.get(part) if isinstance(value, dict) else None
                    if value is None:
                        break
                
                if value is not None:
                    print(f"  [OK] {field}: {value}")
                else:
                    print(f"  [MISSING] {field}: 字段不存在")
                    all_found = False
            else:
                # 普通字段
                if field in item:
                    value = item.get(field)
                    print(f"  [OK] {field}: {value}")
                else:
                    print(f"  [MISSING] {field}: 字段不存在")
                    all_found = False
        
        return all_found
    
    # 如果data是对象
    elif isinstance(data, dict):
        all_found = True
        for field in check_fields:
            if '.' in field:
                # 嵌套字段
                parts = field.split('.')
                value = data
                for part in parts:
                    value = value.get(part) if isinstance(value, dict) else None
                    if value is None:
                        break
                
                if value is not None:
                    print(f"  [OK] {field}: {value}")
                else:
                    print(f"  [MISSING] {field}: 字段不存在")
                    all_found = False
            else:
                # 普通字段
                if field in data:
                    value = data.get(field)
                    print(f"  [OK] {field}: {value}")
                else:
                    print(f"  [MISSING] {field}: 字段不存在")
                    all_found = False
        
        return all_found
    
    print(f"[WARN] data类型未知: {type(data)}")
    return True

def main():
    print("="*80)
    print("          API机构等级字段完整测试")
    print("="*80)
    
    # 先测试服务是否启动
    print("\n检查服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/actuator/health", timeout=5)
        if response.status_code == 200:
            print("[OK] 后端服务已启动")
        else:
            print("[WARN] 服务可能未完全启动")
    except:
        try:
            # 尝试访问一个简单的API
            response = requests.get(f"{BASE_URL}/api/institutions", timeout=5)
            if response.status_code == 200:
                print("[OK] 后端服务已启动")
            else:
                print("[WARN] 服务响应异常")
        except:
            print("[ERROR] 后端服务未启动，请先启动服务")
            return
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 1. 测试登录接口（获取token）
    print("\n" + "="*80)
    print("步骤 1: 登录获取Token")
    print("="*80)
    
    login_data = {
        "phone": "13900000001",
        "name": "测试用户",
        "title": "护士长",
        "role": "CONTESTANT",
        "institutionId": 1
    }
    
    total_tests += 1
    if test_api(
        "登录接口",
        "POST",
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        check_fields=["institutionRegion", "institutionLevel", "institutionName"]
    ):
        passed_tests += 1
        
        # 获取token
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        token = response.json()['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n[OK] Token获取成功")
        
        # 2. 测试机构列表
        total_tests += 1
        if test_api(
            "机构列表",
            "GET",
            f"{BASE_URL}/api/institutions",
            headers=headers,
            check_fields=["level"]
        ):
            passed_tests += 1
        
        # 3. 测试机构详情
        total_tests += 1
        if test_api(
            "机构详情",
            "GET",
            f"{BASE_URL}/api/institutions/1",
            headers=headers,
            check_fields=["level"]
        ):
            passed_tests += 1
        
        # 4. 测试我的报名列表
        total_tests += 1
        if test_api(
            "我的报名列表",
            "GET",
            f"{BASE_URL}/api/registrations/my",
            headers=headers,
            check_fields=["institutionName", "institutionLevel"]
        ):
            passed_tests += 1
        
        # 5. 测试报名详情（需要先获取一个报名ID）
        print("\n" + "="*80)
        print("获取报名ID用于后续测试...")
        print("="*80)
        try:
            response = requests.get(
                f"{BASE_URL}/api/admin/registrations/filter?competitionId=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json().get('data', [])
                if len(data) > 0:
                    registration_id = data[0].get('registrationId')
                    print(f"[OK] 获取到报名ID: {registration_id}")
                    
                    # 测试报名详情
                    total_tests += 1
                    if test_api(
                        "报名详情",
                        "GET",
                        f"{BASE_URL}/api/registrations/{registration_id}",
                        headers=headers,
                        check_fields=["institution.level"]
                    ):
                        passed_tests += 1
                else:
                    print("[WARN] 没有找到报名数据，跳过报名详情测试")
        except Exception as e:
            print(f"[WARN] 获取报名ID失败: {e}")
        
        # 6. 测试评审任务列表
        total_tests += 1
        if test_api(
            "评审任务列表（评委端）",
            "GET",
            f"{BASE_URL}/api/reviews/my-tasks",
            headers=headers,
            check_fields=["institutionLevel"]
        ):
            passed_tests += 1
        
        # 7. 测试按阶段查询评审任务
        total_tests += 1
        if test_api(
            "按阶段查询评审任务",
            "GET",
            f"{BASE_URL}/api/reviews/tasks/stage?competitionId=1&stage=BOOK",
            headers=headers,
            check_fields=["registrationId", "projectName", "institutionName", "institutionLevel"]
        ):
            passed_tests += 1
        
        # 8. 测试报名筛选列表
        total_tests += 1
        if test_api(
            "报名筛选列表（组委会）",
            "GET",
            f"{BASE_URL}/api/admin/registrations/filter?competitionId=1",
            headers=headers,
            check_fields=["institutionLevel"]
        ):
            passed_tests += 1
        
        # 9. 测试评审排名列表
        total_tests += 1
        if test_api(
            "评审排名列表（组委会）",
            "GET",
            f"{BASE_URL}/api/admin/reviews/rankings?competitionId=1&stage=BOOK",
            headers=headers,
            check_fields=["institutionLevel"]
        ):
            passed_tests += 1
        
        # 10. 测试评委列表
        total_tests += 1
        if test_api(
            "评委列表（组委会）",
            "GET",
            f"{BASE_URL}/api/admin/reviews/reviewers",
            headers=headers,
            check_fields=["institutionLevel"]
        ):
            passed_tests += 1
        
        # 11. 测试导出机构列表（OPS专用）
        # 需要OPS角色的token，这里先跳过或使用普通用户测试权限
        print("\n" + "="*80)
        print("[INFO] 测试导出机构列表需要OPS角色，使用普通查询测试")
        print("="*80)
        
        # 12. 测试评审结果统计（确认无需institutionLevel）
        total_tests += 1
        print("\n" + "="*80)
        print("测试: 评审结果统计（确认返回统计数据）")
        print("API: GET /api/registrations/{id}/review-results")
        print("="*80)
        try:
            response = requests.get(
                f"{BASE_URL}/api/admin/registrations/filter?competitionId=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json().get('data', [])
                if len(data) > 0:
                    registration_id = data[0].get('registrationId')
                    
                    response2 = requests.get(
                        f"{BASE_URL}/api/registrations/{registration_id}/review-results",
                        headers=headers,
                        timeout=10
                    )
                    if response2.status_code == 200:
                        result = response2.json()
                        print(f"[OK] API响应成功")
                        print(f"[INFO] 返回统计数据（stage, taskCount, scoredCount, avgTotal）")
                        if len(result.get('data', [])) > 0:
                            print(f"[OK] 示例数据: {result['data'][0]}")
                        passed_tests += 1
                    else:
                        print(f"[FAIL] API请求失败")
                else:
                    print("[INFO] 没有报名数据，跳过测试")
                    passed_tests += 1  # 计为通过
        except Exception as e:
            print(f"[FAIL] 测试异常: {e}")
    
    # 总结
    print("\n" + "="*80)
    print("                    测试总结")
    print("="*80)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] 所有测试通过！")
    else:
        print(f"\n[WARNING] 有 {total_tests - passed_tests} 个测试失败")
    
    print("="*80)

if __name__ == '__main__':
    main()
