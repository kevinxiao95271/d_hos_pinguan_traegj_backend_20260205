#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试登录接口"""

import requests
import json
import time

BASE_URL = "http://localhost:6031"

print("=" * 80)
print("登录接口快速测试")
print("=" * 80)

# 测试登录
print("\n测试: POST /api/auth/login")
print("-" * 80)

login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}

print(f"请求数据: {json.dumps(login_data, ensure_ascii=False)}")
print(f"开始时间: {time.strftime('%H:%M:%S')}")

start_time = time.time()

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        timeout=10  # 10秒超时
    )
    
    elapsed = time.time() - start_time
    
    print(f"结束时间: {time.strftime('%H:%M:%S')}")
    print(f"耗时: {elapsed:.2f}秒")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n响应数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        if data.get('success'):
            token = data['data']['token']
            print(f"\n✓ 登录成功")
            print(f"Token (前50字符): {token[:50]}...")
            
            # 测试使用token
            print(f"\n测试: 使用Token调用接口")
            print("-" * 80)
            
            headers = {"Authorization": f"Bearer {token}"}
            test_start = time.time()
            
            test_response = requests.get(
                f"{BASE_URL}/api/admin/reviews/tasks",
                params={"competitionId": 21, "stage": "BOOK"},
                headers=headers,
                timeout=10
            )
            
            test_elapsed = time.time() - test_start
            
            print(f"耗时: {test_elapsed:.2f}秒")
            print(f"状态码: {test_response.status_code}")
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                if test_data.get('success'):
                    tasks = test_data.get('data', [])
                    print(f"✓ 接口调用成功，返回 {len(tasks)} 条任务")
                else:
                    print(f"✗ 接口返回失败: {test_data.get('message')}")
            else:
                print(f"✗ 接口调用失败")
        else:
            print(f"\n✗ 登录失败: {data.get('message')}")
    else:
        print(f"\n✗ 请求失败")
        print(f"响应: {response.text}")
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"\n✗ 请求超时 (>{elapsed:.2f}秒)")
    print("可能原因:")
    print("  1. 数据库查询阻塞")
    print("  2. 数据库连接池耗尽")
    print("  3. 后端代码存在死锁")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n✗ 异常 ({elapsed:.2f}秒): {str(e)}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
