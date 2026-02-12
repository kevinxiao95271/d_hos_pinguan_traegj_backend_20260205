#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用curl测试评分接口"""

import subprocess
import json

BASE_URL = "http://localhost:6031"

# 1. 登录
print("1. 登录...")
login_cmd = f'''curl -s -X POST "{BASE_URL}/api/auth/login" -H "Content-Type: application/json" -d '{{"phone":"13800000006","name":"李明华","title":"主任医师","role":"REVIEWER","institutionId":2,"expertBackground":"MEDICAL"}}\''''

result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
login_data = json.loads(result.stdout)

if login_data.get('success'):
    token = login_data['data']['token']
    print(f"✓ 登录成功, Token: {token[:50]}...")
    
    # 2. 提交评分
    print("\n2. 提交评分...")
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
    
    score_json = json.dumps(score_data)
    score_cmd = f'''curl -s -X POST "{BASE_URL}/api/reviews/scores" -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d '{score_json}\''''
    
    print(f"请求: POST /api/reviews/scores")
    print(f"数据: {json.dumps(score_data, ensure_ascii=False, indent=2)}")
    
    result = subprocess.run(score_cmd, shell=True, capture_output=True, text=True)
    print(f"\n响应: {result.stdout}")
    
    try:
        response_data = json.loads(result.stdout)
        if response_data.get('success'):
            print(f"\n✓ 评分提交成功")
        else:
            print(f"\n✗ 评分提交失败: {response_data.get('message')}")
    except:
        print(f"\n✗ 响应解析失败")
else:
    print(f"✗ 登录失败")
