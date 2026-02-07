#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""步骤1: 测试书审排名API"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("步骤1: 测试书审排名API")
print("="*80)

try:
    # 1. 登录
    print("\n[1] 登录组委会账号")
    print("-" * 80)
    
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"   {login_resp.text}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取书审排名
    print("\n[2] 获取书审排名")
    print("-" * 80)
    
    book_resp = requests.get(f"{BASE}/api/admin/reviews/rankings", params={
        "competitionId": 21,
        "stage": "BOOK"
    }, headers=headers, timeout=10)
    
    print(f"API路径: GET /api/admin/reviews/rankings")
    print(f"参数:")
    print(f"  - competitionId: 21")
    print(f"  - stage: BOOK")
    print(f"状态码: {book_resp.status_code}")
    
    if book_resp.status_code == 200:
        book_data = book_resp.json()['data']
        print(f"✅ 获取成功")
        print(f"\n返回数据统计:")
        print(f"  - 书审项目数: {len(book_data)}")
        
        if len(book_data) > 0:
            print(f"\n前5名书审排名:")
            print(f"  {'排名':<6} {'项目名称':<35} {'机构':<30} {'组别':<10} {'得分':<8}")
            print(f"  {'-'*95}")
            
            for item in book_data[:5]:
                project_name = item['projectName'][:30] if len(item['projectName']) > 30 else item['projectName']
                institution = item['institutionName'][:25] if len(item['institutionName']) > 25 else item['institutionName']
                group_map = {'BASIC': '基层组', 'ADVANCED': '进阶组', 'COMPREHENSIVE': '综合组'}
                group = group_map.get(item['groupType'], item['groupType'])
                
                print(f"  {item['rank']:<6} {project_name:<35} {institution:<30} {group:<10} {item['avgTotal']:<8.1f}")
            
            print(f"\n书审得分统计:")
            scores = [item['avgTotal'] for item in book_data]
            print(f"  - 平均分: {sum(scores) / len(scores):.2f}")
            print(f"  - 最高分: {max(scores):.2f}")
            print(f"  - 最低分: {min(scores):.2f}")
            
            print(f"\n返回数据结构示例（第1条）:")
            print(json.dumps(book_data[0], ensure_ascii=False, indent=2))
            
            # 保存数据供下一步使用
            with open('scripts/test_data_book.json', 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 数据已保存到: scripts/test_data_book.json")
            
    else:
        print(f"❌ 获取失败")
        print(f"   {book_resp.text}")
        exit(1)

except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    print("请启动服务器：mvn spring-boot:run")
    exit(1)
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("✅ 步骤1测试完成")
print("="*80)
