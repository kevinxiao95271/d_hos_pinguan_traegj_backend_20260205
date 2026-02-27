# -*- coding: utf-8 -*-
"""
验证管理员账号登录
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("验证管理员账号登录")
print("=" * 100)

test_accounts = [
    {
        'description': '赛事组委会',
        'phone': '13800000127',
        'password': 'committee2026',
        'expected_role': 'COMMITTEE_ADMIN'
    },
    {
        'description': '系统运维',
        'phone': '13800000005',
        'password': 'ops2026',
        'expected_role': 'OPS'
    }
]

results = []

for account in test_accounts:
    print(f"\n[测试] {account['description']}")
    print("-" * 100)
    print(f"  手机号: {account['phone']}")
    print(f"  密码: {account['password']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-with-password",
            json={
                "phone": account['phone'],
                "password": account['password']
            },
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 处理可能的响应包装
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], dict):
                    token_data = data['data']
                elif 'token' in data:
                    token_data = {'token': data['token']}
                else:
                    token_data = data
            else:
                token_data = {}
            
            token = token_data.get('token', 'N/A')
            
            print(f"  登录成功！")
            print(f"  Token: {token[:30] if token != 'N/A' else 'N/A'}...")
            
            # 验证token有效性（调用需要认证的接口）
            if token != 'N/A':
                headers = {"Authorization": f"Bearer {token}"}
                
                # 尝试获取用户信息
                me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"  用户信息获取成功:")
                    
                    # 处理响应包装
                    if isinstance(me_data, dict) and 'data' in me_data:
                        user_info = me_data['data']
                    else:
                        user_info = me_data
                    
                    if isinstance(user_info, dict):
                        print(f"    姓名: {user_info.get('name', 'N/A')}")
                        print(f"    角色: {user_info.get('role', 'N/A')}")
                        print(f"    手机: {user_info.get('phone', 'N/A')}")
                else:
                    print(f"  用户信息获取失败: {me_response.status_code}")
            
            results.append({
                'description': account['description'],
                'phone': account['phone'],
                'password': account['password'],
                'status': 'success',
                'token': token[:30] if token != 'N/A' else 'N/A'
            })
            
        else:
            print(f"  登录失败！")
            print(f"  响应: {response.text}")
            
            results.append({
                'description': account['description'],
                'phone': account['phone'],
                'password': account['password'],
                'status': 'failed',
                'error': response.text
            })
            
    except Exception as e:
        print(f"  请求异常: {str(e)}")
        results.append({
            'description': account['description'],
            'phone': account['phone'],
            'password': account['password'],
            'status': 'error',
            'error': str(e)
        })

# 输出测试总结
print("\n" + "=" * 100)
print("登录测试总结")
print("=" * 100)

success_count = sum(1 for r in results if r['status'] == 'success')
print(f"\n成功: {success_count}/{len(results)}")

for result in results:
    status_icon = "[OK]" if result['status'] == 'success' else "[FAIL]"
    print(f"{status_icon} {result['description']}: {result['phone']}")

print("\n" + "=" * 100)
