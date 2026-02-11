#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试孙丽娟登录"""

import requests

BASE_URL = "http://localhost:6031"

def test_login():
    account = {
        'phone': '13800002569',
        'name': '孙丽娟',
        'role': 'REVIEWER'
    }
    
    print("=" * 60)
    print("测试孙丽娟评委账号登录")
    print("=" * 60)
    
    print(f"\n账号信息:")
    print(f"  手机号: {account['phone']}")
    print(f"  姓名: {account['name']}")
    print(f"  角色: {account['role']}")
    
    print(f"\n正在登录...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json=account)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result['data']
            print(f"\n✅ 登录成功!")
            print(f"  ID: {data.get('id')}")
            print(f"  姓名: {data.get('name')}")
            print(f"  角色: {data.get('role')}")
            print(f"  职称: {data.get('title')}")
            print(f"  Token: {data.get('token')[:50]}...")
            
            # 测试查询任务
            token = data.get('token')
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"\n测试查询评审任务...")
            response = requests.get(f"{BASE_URL}/api/reviews/my-tasks", headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    tasks = result['data']
                    print(f"✅ 查询成功: {len(tasks)} 个任务")
                else:
                    print(f"❌ 查询失败: {result.get('message')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
            
            return True
        else:
            print(f"\n❌ 登录失败: {result.get('message')}")
    else:
        print(f"\n❌ 请求失败")
    
    return False

if __name__ == '__main__':
    test_login()
