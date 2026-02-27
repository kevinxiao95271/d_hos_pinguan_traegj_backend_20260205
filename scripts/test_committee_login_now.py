# -*- coding: utf-8 -*-
"""
测试组委会登录
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试组委会账号登录")
print("=" * 100)

test_data = {
    "phone": "13800000127",
    "password": "committee2026"
}

print(f"\n请求数据:")
print(json.dumps(test_data, ensure_ascii=False, indent=2))

print(f"\n发送登录请求...")

try:
    response = requests.post(
        f"{BASE_URL}/auth/login-with-password",
        json=test_data,
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"\n响应内容:")
    print(response.text)
    
    if response.status_code == 200:
        print(f"\n[成功] 登录成功！")
        
        try:
            data = response.json()
            print(f"\n解析后的数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 提取token
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], dict):
                    token = data['data'].get('token', 'N/A')
                    user_name = data['data'].get('name', 'N/A')
                    user_role = data['data'].get('role', 'N/A')
                elif 'token' in data:
                    token = data['token']
                    user_name = data.get('name', 'N/A')
                    user_role = data.get('role', 'N/A')
                else:
                    token = 'N/A'
                    user_name = 'N/A'
                    user_role = 'N/A'
                
                print(f"\n提取的信息:")
                print(f"  Token: {token[:40] if token != 'N/A' else 'N/A'}...")
                print(f"  姓名: {user_name}")
                print(f"  角色: {user_role}")
        except:
            pass
    else:
        print(f"\n[失败] 登录失败")
        
except Exception as e:
    print(f"\n[异常] 请求失败: {str(e)}")

print("\n" + "=" * 100)
