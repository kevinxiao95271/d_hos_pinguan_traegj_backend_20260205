#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试评分接口"""

import requests
import json
import traceback

BASE_URL = "http://localhost:6031"

try:
    # 1. 登录
    print("1. 登录评审专家...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800000006",
        "name": "李明华",
        "title": "主任医师",
        "role": "REVIEWER",
        "institutionId": 2,
        "expertBackground": "MEDICAL"
    }, timeout=5)
    
    print(f"登录状态码: {login_resp.status_code}")
    login_data = login_resp.json()
    
    if not login_data.get('success'):
        print(f"登录失败: {login_data}")
        exit(1)
    
    token = login_data['data']['token']
    print(f"✓ 登录成功")
    
    # 2. 提交评分
    print("\n2. 提交评分...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    score_data = {
        "reviewTaskId": 115,
        "plan": 10.0,
        "problem": 10.0,
        "action": 10.0,
        "success": 10.0,
        "review": 10.0,
        "operation": 10.0,
        "presentation": 10.0,
        "highlight": "项目计划清晰",
        "weakness": "数据分析不够深入"
    }
    
    print(f"请求数据: {json.dumps(score_data, ensure_ascii=False)}")
    
    score_resp = requests.post(
        f"{BASE_URL}/api/reviews/scores",
        json=score_data,
        headers=headers,
        timeout=5
    )
    
    print(f"评分状态码: {score_resp.status_code}")
    print(f"评分响应: {score_resp.text}")
    
    if score_resp.status_code == 200:
        score_result = score_resp.json()
        if score_result.get('success'):
            print(f"\n✓ 评分提交成功!")
            print(f"评分详情: {json.dumps(score_result['data'], ensure_ascii=False, indent=2)}")
        else:
            print(f"\n✗ 评分失败: {score_result.get('message')}")
    else:
        print(f"\n✗ HTTP {score_resp.status_code} 错误")
        
except Exception as e:
    print(f"\n✗ 异常: {str(e)}")
    traceback.print_exc()
