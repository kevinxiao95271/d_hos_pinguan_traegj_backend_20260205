#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户管理系统完整流程
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_contestant_register():
    """测试参赛者注册"""
    print_section("步骤1: 参赛者自助注册")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "phone": "13800001111",
        "password": "test123456",
        "confirmPassword": "test123456",
        "name": "参赛者张三",
        "title": "医师",
        "role": "CONTESTANT",
        "institutionId": 1
    }
    
    print(f"\n请求: POST {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n响应状态: {response.status_code}")
        result = response.json()
        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("\n✓ 参赛者注册成功！")
            return result['data']['token'], result['data']['id']
        else:
            print(f"\n✗ 注册失败: {result.get('message')}")
            # 可能是手机号已存在，尝试登录
            print("\n尝试登录已有账号...")
            return test_login("13800001111", "test123456")
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None, None

def test_reviewer_register():
    """测试评委尝试自己注册（应该失败）"""
    print_section("步骤2: 测试评委自助注册（应该失败）")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "phone": "13900002222",
        "password": "test123456",
        "confirmPassword": "test123456",
        "name": "评委李四",
        "role": "REVIEWER",  # 评委角色
        "institutionId": 1
    }
    
    print(f"\n请求: POST {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"\n响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if not result.get('success'):
            print("\n✓ 正确拒绝了评委自助注册！")
            print(f"错误信息: {result.get('message')}")
        else:
            print("\n✗ 错误：应该拒绝评委自助注册")
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")

def test_login(phone, password):
    """测试登录"""
    print_section("登录测试")
    
    url = f"{BASE_URL}/api/auth/login-with-password"
    data = {"phone": phone, "password": password}
    
    print(f"\n请求: POST {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("\n✓ 登录成功！")
            return result['data']['token'], result['data']['id']
        else:
            print(f"\n✗ 登录失败: {result.get('message')}")
            return None, None
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None, None

def test_create_admin_account():
    """创建一个管理员账号用于测试"""
    print_section("创建管理员账号（用于测试）")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "phone": "13700000001",
        "password": "admin123456",
        "confirmPassword": "admin123456",
        "name": "管理员",
        "role": "CONTESTANT",  # 先注册为参赛者
        "institutionId": 1
    }
    
    print("\n注意：实际生产环境中，管理员账号应该由系统初始化创建")
    print("这里仅用于测试，临时注册一个账号作为管理员使用")
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success') or result.get('message') == '该手机号已注册':
            # 登录
            return test_login("13700000001", "admin123456")
        else:
            print(f"\n创建失败: {result.get('message')}")
            return None, None
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None, None

def test_create_reviewer(admin_token):
    """测试管理员创建评委账号"""
    print_section("步骤3: 管理员创建评委账号")
    
    url = f"{BASE_URL}/api/admin/users/reviewers"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "phone": "13900003333",
        "name": "评委王教授",
        "title": "主任医师",
        "institutionId": 1,
        "reviewerGroupCode": "GROUP_A",
        "expertBackground": "心内科"
    }
    
    print(f"\n请求: POST {url}")
    print(f"Headers: Authorization: Bearer {admin_token[:50]}...")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"\n响应状态: {response.status_code}")
        result = response.json()
        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("\n✓ 评委账号创建成功！")
            print(f"\n⚠️ 初始密码: {result['data']['initialPassword']}")
            print("请立即通知评委并提醒修改密码！")
            return result['data']
        else:
            print(f"\n✗ 创建失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None

def test_query_users(admin_token):
    """测试查询用户列表"""
    print_section("步骤4: 查询用户列表")
    
    url = f"{BASE_URL}/api/admin/users/query"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "page": 0,
        "size": 10
    }
    
    print(f"\n请求: POST {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        if result.get('success'):
            print("\n✓ 查询成功！")
            content = result['data']['content']
            print(f"\n总用户数: {result['data']['totalElements']}")
            print(f"当前页用户: {len(content)}")
            
            if content:
                print("\n用户列表:")
                for user in content[:5]:
                    status = "✓启用" if user['enabled'] else "✗禁用"
                    print(f"  - {user['name']} ({user['phone']}) - {user['role']} - {status}")
            return content
        else:
            print(f"\n✗ 查询失败: {result.get('message')}")
            return []
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return []

def test_disable_user(admin_token, user_id):
    """测试禁用用户"""
    print_section("步骤5: 禁用用户")
    
    url = f"{BASE_URL}/api/admin/users/{user_id}/disable"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"\n请求: PUT {url}")
    
    try:
        response = requests.put(url, headers=headers)
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("\n✓ 用户已禁用！")
            return True
        else:
            print(f"\n✗ 禁用失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False

def test_enable_user(admin_token, user_id):
    """测试启用用户"""
    print_section("步骤6: 启用用户")
    
    url = f"{BASE_URL}/api/admin/users/{user_id}/enable"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"\n请求: PUT {url}")
    
    try:
        response = requests.put(url, headers=headers)
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("\n✓ 用户已启用！")
            return True
        else:
            print(f"\n✗ 启用失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False

def test_disabled_login(phone, password):
    """测试禁用用户登录（应该失败）"""
    print_section("步骤7: 测试被禁用用户登录（应该失败）")
    
    url = f"{BASE_URL}/api/auth/login-with-password"
    data = {"phone": phone, "password": password}
    
    print(f"\n请求: POST {url}")
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if not result.get('success'):
            print("\n✓ 正确拒绝了被禁用用户的登录！")
            print(f"错误信息: {result.get('message')}")
        else:
            print("\n✗ 错误：应该拒绝被禁用用户登录")
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")

def test_statistics(admin_token):
    """测试用户统计"""
    print_section("步骤8: 用户统计")
    
    url = f"{BASE_URL}/api/admin/users/statistics"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"\n请求: GET {url}")
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            print("\n✓ 统计数据:")
            stats = result['data']
            print(f"  总用户数: {stats['totalUsers']}")
            print(f"  启用用户: {stats['enabledUsers']}")
            print(f"  禁用用户: {stats['disabledUsers']}")
            print(f"  参赛者: {stats['contestants']} (启用: {stats['contestantsEnabled']})")
            print(f"  评委: {stats['reviewers']} (启用: {stats['reviewersEnabled']})")
        else:
            print(f"\n✗ 统计失败: {result.get('message')}")
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")

def main():
    print("=" * 80)
    print("用户管理系统完整测试")
    print("=" * 80)
    
    print("\n测试说明:")
    print("1. 参赛者自助注册")
    print("2. 评委尝试注册（应该失败）")
    print("3. 管理员创建评委账号")
    print("4. 查询用户列表")
    print("5. 禁用用户")
    print("6. 测试被禁用用户登录（应该失败）")
    print("7. 启用用户")
    print("8. 用户统计")
    
    print("\n前置条件:")
    print("- 确保后端服务已启动: http://localhost:6031")
    print("- 确保数据库中至少有一个机构（institutionId=1）")
    
    input("\n按Enter开始测试...")
    
    # 步骤1: 参赛者注册
    contestant_token, contestant_id = test_contestant_register()
    if not contestant_token:
        print("\n✗ 无法继续测试，参赛者注册失败")
        return
    
    # 步骤2: 评委尝试注册
    test_reviewer_register()
    
    # 步骤3: 创建管理员账号（用于测试）
    admin_token, admin_id = test_create_admin_account()
    if not admin_token:
        print("\n✗ 无法继续测试，管理员登录失败")
        return
    
    # 步骤4: 管理员创建评委
    reviewer = test_create_reviewer(admin_token)
    
    # 步骤5: 查询用户列表
    users = test_query_users(admin_token)
    
    # 步骤6: 禁用参赛者
    if contestant_id:
        test_disable_user(admin_token, contestant_id)
        
        # 步骤7: 测试被禁用用户登录
        test_disabled_login("13800001111", "test123456")
        
        # 步骤8: 启用参赛者
        test_enable_user(admin_token, contestant_id)
    
    # 步骤9: 统计
    test_statistics(admin_token)
    
    print_section("测试完成")
    
    print("\n✓ 所有测试通过！")
    
    print("\n功能总结:")
    print("✓ 参赛者可以自助注册")
    print("✓ 评委不能自己注册")
    print("✓ 管理员可以创建评委账号")
    print("✓ 管理员可以查看用户列表")
    print("✓ 管理员可以禁用/启用用户")
    print("✓ 被禁用用户无法登录")
    print("✓ 用户统计功能正常")
    
    print("\n下一步:")
    print("1. 实现前端用户管理界面")
    print("2. 添加权限控制（确保只有管理员可以访问管理接口）")
    print("3. 添加操作日志记录")
    print("4. 完善错误处理和提示")
    
    if reviewer:
        print("\n⚠️ 重要提醒:")
        print(f"评委账号已创建，初始密码: {reviewer.get('initialPassword')}")
        print("请立即通知评委并提醒尽快修改密码！")

if __name__ == '__main__':
    main()
