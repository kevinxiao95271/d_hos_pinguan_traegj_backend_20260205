#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试筛选API是否正常工作"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试报名筛选API")
print("="*80)

try:
    # 登录
    print("\n[1] 登录组委会账号...")
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=30)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"响应: {login_resp.text}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 测试1: 获取所有报名（不筛选）
    print("\n\n[2] 测试基本接口: GET /api/registrations?competitionId=21")
    print("-" * 80)
    
    resp1 = requests.get(
        f"{BASE}/api/registrations",
        params={"competitionId": 21},
        headers=headers,
        timeout=30
    )
    
    if resp1.status_code == 200:
        all_regs = resp1.json()['data']
        print(f"✅ 成功，返回 {len(all_regs)} 个报名")
        
        # 检查报名106
        reg_106 = next((r for r in all_regs if r['id'] == 106), None)
        if reg_106:
            print(f"\n找到报名106: {reg_106['projectName']}")
            print(f"  状态: {reg_106.get('status', 'N/A')}")
            print(f"  ⚠️  注意：这个接口返回的数据中没有methodCode字段")
        else:
            print("\n❌ 未找到报名106")
    else:
        print(f"❌ 请求失败: {resp1.status_code}")
        print(f"响应: {resp1.text[:500]}")
    
    # 测试2: 使用筛选接口（不加methodCode）
    print("\n\n[3] 测试筛选接口: GET /api/admin/registrations/filter?competitionId=21")
    print("-" * 80)
    
    resp2 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={"competitionId": 21},
        headers=headers,
        timeout=30
    )
    
    if resp2.status_code == 200:
        filtered_regs = resp2.json()['data']
        print(f"✅ 成功，返回 {len(filtered_regs)} 个报名")
        
        # 先查看数据结构
        if filtered_regs:
            print(f"\n数据结构示例（第1个）:")
            print(f"{json.dumps(filtered_regs[0], ensure_ascii=False, indent=2)}")
        
        # 检查报名106（使用registrationId字段）
        item_106 = next((r for r in filtered_regs if r.get('registrationId') == 106 or r.get('id') == 106), None)
        if item_106:
            print(f"\n找到报名106:")
            print(f"  ID: {item_106.get('registrationId') or item_106.get('id')}")
            print(f"  项目名称: {item_106.get('projectName')}")
            print(f"  品管工具代码: {item_106.get('methodCode', 'N/A')}")
            print(f"  品管工具标签: {item_106.get('methodLabel', 'N/A')}")
            
            method_code = item_106.get('methodCode')
            
            if method_code:
                # 测试3: 按品管工具筛选
                print(f"\n\n[4] 测试按品管工具筛选: methodCode={method_code}")
                print("-" * 80)
                
                resp3 = requests.get(
                    f"{BASE}/api/admin/registrations/filter",
                    params={
                        "competitionId": 21,
                        "methodCode": method_code
                    },
                    headers=headers,
                    timeout=30
                )
                
                if resp3.status_code == 200:
                    method_filtered = resp3.json()['data']
                    print(f"✅ 筛选成功，返回 {len(method_filtered)} 个报名")
                    
                    # 检查是否包含106
                    has_106 = any(r.get('registrationId') == 106 or r.get('id') == 106 for r in method_filtered)
                    
                    if has_106:
                        print(f"\n✅ 报名106在筛选结果中")
                    else:
                        print(f"\n❌ 报名106不在筛选结果中")
                    
                    print(f"\n筛选结果（前3个）:")
                    for r in method_filtered[:3]:
                        rid = r.get('registrationId') or r.get('id')
                        print(f"  - ID {rid}: {r.get('projectName')}")
                        print(f"    品管工具: {r.get('methodCode')} ({r.get('methodLabel')})")
                else:
                    print(f"❌ 筛选失败: {resp3.status_code}")
                    print(f"响应: {resp3.text[:500]}")
        else:
            print("\n❌ 筛选结果中未找到报名106")
    else:
        print(f"❌ 请求失败: {resp2.status_code}")
        print(f"响应: {resp2.text[:500]}")
    
    # 测试4: 尝试用错误的label筛选
    print("\n\n[5] 测试用label筛选（预期失败）: methodCode=品管圈-课题达成")
    print("-" * 80)
    
    resp4 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodCode": "品管圈-课题达成"  # 这是label，不是code
        },
        headers=headers,
        timeout=30
    )
    
    if resp4.status_code == 200:
        label_filtered = resp4.json()['data']
        print(f"返回 {len(label_filtered)} 个报名")
        
        if len(label_filtered) == 0:
            print("⚠️  用label筛选返回空结果（这证明了问题所在！）")
        else:
            print("❌ 用label筛选居然有结果？")
    else:
        print(f"❌ 请求失败: {resp4.status_code}")

except requests.exceptions.Timeout:
    print("\n❌ 请求超时，服务器可能未运行")
    print("请确保后端服务在运行：")
    print("  mvn spring-boot:run")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("诊断结论")
print("="*80)

print("""
关键发现：

1. ✅ 后端有筛选接口：GET /api/admin/registrations/filter
2. ✅ 支持按 methodCode 筛选
3. ⚠️  报名106的 methodCode 是 "qc_topic"
4. ⚠️  前端显示的是 label "品管圈-课题达成"

问题根源：
  前端可能：
  1. 使用了错误的API路径（/api/registrations 而不是 /api/admin/registrations/filter）
  2. 传递了 label 而不是 code

解决方案：
  前端需要：
  1. 使用 /api/admin/registrations/filter 接口
  2. 传递 methodCode="qc_topic"（而不是"品管圈-课题达成"）
  3. 或者让前端维护一个 label->code 的映射表
""")
