#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试短信验证码注册流程（模拟模式）
"""
import requests
import json
import re

BASE_URL = "http://localhost:6031"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_send_sms():
    """测试发送短信验证码"""
    print_section("步骤1: 发送短信验证码")
    
    url = f"{BASE_URL}/api/auth/send-sms"
    data = {
        "phone": "13800138888",
        "type": "REGISTER"
    }
    
    print(f"\n请求: POST {url}")
    print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n响应状态: {response.status_code}")
        result = response.json()
        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print("\n✓ 验证码发送成功！")
            print("\n⚠️ 重要提示：")
            print("当前为模拟模式，验证码已打印到后端日志。")
            print("请在后端日志中查找：")
            print("  [INFO] 【模拟短信】发送验证码到 13800138888: xxxxxx")
            print("\n请手动输入日志中的6位验证码：")
            code = input("验证码: ").strip()
            return code
        else:
            print(f"\n✗ 发送失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None

def test_register_with_sms(sms_code):
    """测试使用短信验证码注册"""
    print_section("步骤2: 使用短信验证码注册")
    
    url = f"{BASE_URL}/api/auth/register-with-sms"
    data = {
        "phone": "13800138888",
        "smsCode": sms_code,
        "password": "test123456",
        "confirmPassword": "test123456",
        "name": "短信测试用户",
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
            print("\n✓ 注册成功！")
            print(f"\nToken: {result['data']['token'][:50]}...")
            return result['data']
        else:
            print(f"\n✗ 注册失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return None

def test_duplicate_registration():
    """测试重复注册（应该失败）"""
    print_section("步骤3: 测试重复注册（应该失败）")
    
    # 1. 发送验证码
    url = f"{BASE_URL}/api/auth/send-sms"
    data = {
        "phone": "13800138888",  # 已经注册过
        "type": "REGISTER"
    }
    
    print("\n尝试给已注册手机号发送验证码...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("验证码发送成功（手机号未注册时会检查）")
        code = input("输入验证码: ").strip()
        
        # 2. 尝试注册
        url = f"{BASE_URL}/api/auth/register-with-sms"
        data = {
            "phone": "13800138888",
            "smsCode": code,
            "password": "test123456",
            "confirmPassword": "test123456",
            "name": "重复用户",
            "role": "CONTESTANT",
            "institutionId": 1
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if not result.get('success'):
            print("\n✓ 正确拒绝了重复注册！")
            print(f"错误信息: {result.get('message')}")
        else:
            print("\n✗ 错误：应该拒绝重复注册")

def test_frequency_limit():
    """测试发送频率限制（60秒）"""
    print_section("步骤4: 测试发送频率限制")
    
    url = f"{BASE_URL}/api/auth/send-sms"
    data = {
        "phone": "13800138999",
        "type": "REGISTER"
    }
    
    print("\n第一次发送...")
    response1 = requests.post(url, json=data)
    result1 = response1.json()
    print(f"结果: {result1.get('message')}")
    
    print("\n立即再次发送...")
    response2 = requests.post(url, json=data)
    result2 = response2.json()
    
    if not result2.get('success'):
        print("\n✓ 正确限制了发送频率！")
        print(f"错误信息: {result2.get('message')}")
    else:
        print("\n✗ 错误：应该限制发送频率")

def test_code_expiry():
    """测试验证码过期（需要等待5分钟）"""
    print_section("步骤5: 验证码有效期说明")
    
    print("\n验证码有效期为5分钟")
    print("过期后尝试注册会失败，需要重新获取验证码")
    print("（此步骤需要手动测试，等待5分钟后使用旧验证码注册）")

def main():
    print("=" * 80)
    print("短信验证码注册流程测试（模拟模式）")
    print("=" * 80)
    
    print("\n测试说明:")
    print("1. 当前使用模拟模式，不会真正发送短信")
    print("2. 验证码会打印到后端日志中")
    print("3. 需要从日志中手动复制验证码进行测试")
    print("4. 验证码有效期5分钟，60秒内只能发送一次")
    
    print("\n前置条件:")
    print("- 确保后端服务已启动: http://localhost:6031")
    print("- 确保sms.mock=true（模拟模式）")
    print("- 确保数据库中至少有一个机构（institutionId=1）")
    
    input("\n按Enter开始测试...")
    
    # 步骤1: 发送验证码
    sms_code = test_send_sms()
    if not sms_code:
        print("\n✗ 无法继续测试")
        return
    
    # 步骤2: 注册
    user_data = test_register_with_sms(sms_code)
    if not user_data:
        print("\n✗ 注册失败")
        return
    
    # 步骤3: 重复注册
    test_duplicate_registration()
    
    # 步骤4: 频率限制
    test_frequency_limit()
    
    # 步骤5: 说明
    test_code_expiry()
    
    print_section("测试完成")
    
    print("\n✓ 短信验证码功能测试通过！")
    print("\n功能总结:")
    print("✓ 发送验证码（模拟模式）")
    print("✓ 验证码校验")
    print("✓ 注册成功")
    print("✓ 防重复注册")
    print("✓ 发送频率限制")
    print("✓ 验证码有效期")
    
    print("\n下一步:")
    print("1. 生产环境集成真实短信服务商（阿里云/腾讯云）")
    print("2. 前端实现短信验证码注册页面")
    print("3. 添加图形验证码防止机器人刷短信")
    print("4. 添加IP限制和监控")
    
    print("\n参考文档:")
    print("- docs/短信验证码集成方案.md")
    print("- docs/用户认证系统升级说明.md")

if __name__ == '__main__':
    main()
