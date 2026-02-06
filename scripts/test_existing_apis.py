#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试现有API接口是否正常工作
"""

import requests
import json
import sys
import io

# Windows UTF-8编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def test_api(method, path, description, token=None, data=None):
    """测试单个API"""
    print(f"\n{'='*80}")
    print(f"测试: {description}")
    print(f"{method} {path}")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            resp = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
        elif method == 'POST':
            headers['Content-Type'] = 'application/json'
            resp = requests.post(f"{BASE_URL}{path}", headers=headers, json=data, timeout=10)
        else:
            print(f"不支持的方法: {method}")
            return None
        
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"成功: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data')
                if isinstance(data, list):
                    print(f"返回数据: 列表，共 {len(data)} 项")
                    if len(data) > 0:
                        print(f"第一项: {json.dumps(data[0], ensure_ascii=False, indent=2)[:200]}...")
                elif isinstance(data, dict):
                    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                else:
                    print(f"返回数据: {data}")
                return result
            else:
                print(f"失败消息: {result.get('message')}")
        else:
            print(f"HTTP错误: {resp.text[:200]}")
        
        return None
        
    except Exception as e:
        print(f"异常: {e}")
        return None

# 开始测试
print("="*80)
print("API接口测试")
print("="*80)

# 1. 测试登录 - 使用现有用户
print("\n" + "="*80)
print("【第1步】测试登录")
print("="*80)

login_result = test_api('POST', '/api/auth/login', '管理员登录', data={
    "phone": "13800000009",
    "name": "Committee",
    "title": "Title",
    "role": "COMMITTEE"
})

token = None
if login_result and login_result.get('success'):
    token = login_result['data'].get('token')
    print(f"\n[OK] 登录成功，获得token")
else:
    print("\n[FAIL] 登录失败")

if not token:
    print("\n无法继续测试，因为没有获得token")
    exit(1)

# 2. 测试查询机构列表
print("\n" + "="*80)
print("【第2步】测试查询机构列表")
print("="*80)
test_api('GET', '/api/institutions', '查询机构列表', token=token)

# 3. 测试查询赛事列表
print("\n" + "="*80)
print("【第3步】测试查询赛事列表")
print("="*80)
test_api('GET', '/api/competitions', '查询赛事列表', token=token)

# 4. 测试查询字典配置
print("\n" + "="*80)
print("【第4步】测试查询字典配置")
print("="*80)
test_api('GET', '/api/dictionaries/method', '查询品管工具字典', token=token)

# 5. 测试查询报名列表
print("\n" + "="*80)
print("【第5步】测试查询报名列表")
print("="*80)
test_api('GET', '/api/admin/registrations/filter?competitionId=21', '查询赛事21的报名列表', token=token)

# 6. 测试查询报名详情
print("\n" + "="*80)
print("【第6步】测试查询报名详情")
print("="*80)
test_api('GET', '/api/registrations/106', '查询报名106的详情', token=token)

# 7. 测试查询用户列表（评审专家）
print("\n" + "="*80)
print("【第7步】测试查询评审专家列表")
print("="*80)
test_api('GET', '/api/admin/reviewers', '查询评审专家列表', token=token)

# 8. 测试统计接口
print("\n" + "="*80)
print("【第8步】测试统计接口")
print("="*80)
test_api('GET', '/api/admin/stats/summary', '查询统计数据', token=token)

print("\n" + "="*80)
print("测试完成")
print("="*80)
