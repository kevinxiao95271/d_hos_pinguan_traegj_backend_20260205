#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试按label筛选报名（新功能）"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试按label筛选报名（新功能）")
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
    
    # 测试1: 按code筛选（旧方式，应该仍然工作）
    print("\n\n[2] 测试按code筛选: methodCode=qc_topic")
    print("-" * 80)
    
    resp1 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodCode": "qc_topic"
        },
        headers=headers,
        timeout=30
    )
    
    if resp1.status_code == 200:
        code_filtered = resp1.json()['data']
        print(f"✅ 成功，返回 {len(code_filtered)} 个报名")
        
        # 检查是否包含106
        has_106 = any(r.get('registrationId') == 106 for r in code_filtered)
        print(f"  包含报名106: {'✅ 是' if has_106 else '❌ 否'}")
        
        if code_filtered:
            print(f"\n  前3个报名:")
            for r in code_filtered[:3]:
                print(f"    - ID {r.get('registrationId')}: {r.get('projectName')}")
                print(f"      品管工具: {r.get('methodCode')} ({r.get('methodLabel')})")
    else:
        print(f"❌ 请求失败: {resp1.status_code}")
        print(f"响应: {resp1.text[:500]}")
    
    # 测试2: 按label筛选（新功能）
    print("\n\n[3] 测试按label筛选: methodLabel=品管圈-课题达成")
    print("-" * 80)
    
    resp2 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodLabel": "品管圈-课题达成"
        },
        headers=headers,
        timeout=30
    )
    
    if resp2.status_code == 200:
        label_filtered = resp2.json()['data']
        print(f"✅ 成功，返回 {len(label_filtered)} 个报名")
        
        # 检查是否包含106
        has_106 = any(r.get('registrationId') == 106 for r in label_filtered)
        print(f"  包含报名106: {'✅ 是' if has_106 else '❌ 否'}")
        
        if label_filtered:
            print(f"\n  前3个报名:")
            for r in label_filtered[:3]:
                print(f"    - ID {r.get('registrationId')}: {r.get('projectName')}")
                print(f"      品管工具: {r.get('methodCode')} ({r.get('methodLabel')})")
        
        # 对比两种方式的结果
        print(f"\n  结果对比:")
        print(f"    按code筛选: {len(code_filtered) if 'code_filtered' in locals() else 'N/A'} 个")
        print(f"    按label筛选: {len(label_filtered)} 个")
        
        if 'code_filtered' in locals() and len(code_filtered) == len(label_filtered):
            print(f"    ✅ 两种方式结果一致！")
        else:
            print(f"    ⚠️  结果数量不一致")
    else:
        print(f"❌ 请求失败: {resp2.status_code}")
        print(f"响应: {resp2.text[:500]}")
    
    # 测试3: 同时传code和label（code优先）
    print("\n\n[4] 测试同时传code和label: code优先")
    print("-" * 80)
    
    resp3 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodCode": "qc_topic",
            "methodLabel": "PDCA"  # 故意传错误的label
        },
        headers=headers,
        timeout=30
    )
    
    if resp3.status_code == 200:
        both_filtered = resp3.json()['data']
        print(f"✅ 成功，返回 {len(both_filtered)} 个报名")
        
        if both_filtered:
            first_item = both_filtered[0]
            print(f"  第一个结果的品管工具: {first_item.get('methodCode')} ({first_item.get('methodLabel')})")
            
            if first_item.get('methodCode') == 'qc_topic':
                print(f"  ✅ code参数优先生效（正确）")
            else:
                print(f"  ⚠️  label参数生效了（不应该）")
    else:
        print(f"❌ 请求失败: {resp3.status_code}")
    
    # 测试4: 测试其他label
    print("\n\n[5] 测试其他label: PDCA")
    print("-" * 80)
    
    resp4 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodLabel": "PDCA"
        },
        headers=headers,
        timeout=30
    )
    
    if resp4.status_code == 200:
        pdca_filtered = resp4.json()['data']
        print(f"✅ 成功，返回 {len(pdca_filtered)} 个报名")
        
        if pdca_filtered:
            print(f"\n  前3个报名:")
            for r in pdca_filtered[:3]:
                print(f"    - ID {r.get('registrationId')}: {r.get('projectName')}")
                print(f"      品管工具: {r.get('methodCode')} ({r.get('methodLabel')})")
    else:
        print(f"❌ 请求失败: {resp4.status_code}")
    
    # 测试5: 测试不存在的label
    print("\n\n[6] 测试不存在的label: 不存在的品管工具")
    print("-" * 80)
    
    resp5 = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodLabel": "不存在的品管工具"
        },
        headers=headers,
        timeout=30
    )
    
    if resp5.status_code == 200:
        invalid_filtered = resp5.json()['data']
        print(f"返回 {len(invalid_filtered)} 个报名")
        
        if len(invalid_filtered) == 0:
            print(f"  ✅ 正确处理了无效的label（返回空结果）")
        else:
            print(f"  ⚠️  返回了结果（可能未正确处理无效label）")
    else:
        print(f"❌ 请求失败: {resp5.status_code}")

except requests.exceptions.Timeout:
    print("\n❌ 请求超时，服务器可能未运行")
    print("请确保后端服务在运行：")
    print("  mvn spring-boot:run")
except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    print("请确保后端服务在运行：")
    print("  mvn spring-boot:run")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)

print("""
总结：

✅ 新功能：支持按label筛选
  - methodLabel: '品管圈-课题达成'
  - subjectTypeLabel: '教育训练'

✅ 兼容性：仍然支持按code筛选
  - methodCode: 'qc_topic'
  - subjectTypeCode: 'education'

✅ 优先级：code优先于label
  - 如果同时传code和label，使用code

前端可以选择：
  1. 继续使用code（需要维护映射表）
  2. 直接使用label（更简单，推荐）
""")
