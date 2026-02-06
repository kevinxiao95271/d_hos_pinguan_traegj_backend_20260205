#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试组委会角色权限
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import time

BASE_URL = "http://localhost:6031"

def wait_for_server():
    """等待服务器启动"""
    print("等待服务器启动...")
    for i in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/actuator/health", timeout=3)
            if resp.status_code == 200:
                print(f"[成功] 服务器已启动")
                return True
        except:
            pass
        print(f"  等待中... ({i+1}/30)")
        time.sleep(3)
    
    print("[失败] 服务器启动超时")
    return False

def test_committee_access():
    """测试组委会角色访问权限"""
    print("\n" + "="*80)
    print("测试组委会（COMMITTEE）角色权限")
    print("="*80)
    
    # 1. 组委会登录
    print("\n[步骤1] 组委会登录")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800000009",
        "name": "Committee",
        "title": "组委会",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"[失败] 登录失败: {login_resp.status_code}")
        return
    
    login_data = login_resp.json()
    if not login_data.get("success"):
        print(f"[失败] 登录失败: {login_data.get('message')}")
        return
    
    token = login_data["data"]["token"]
    print(f"[成功] 登录成功，用户ID: {login_data['data']['id']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试获取报名列表（待分配的任务池）
    print("\n[步骤2] 获取待分配的任务池（报名列表）")
    
    endpoints = [
        ("/api/registrations?competitionId=21", "基础报名列表"),
        ("/api/registrations/status?competitionId=21&status=APPROVED", "已审批报名"),
        ("/api/admin/registrations/filter?competitionId=21", "管理端报名筛选"),
    ]
    
    for endpoint, desc in endpoints:
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    count = len(data.get("data", []))
                    print(f"  [成功] {desc}: 返回 {count} 条数据")
                else:
                    print(f"  [失败] {desc}: {data.get('message')}")
            elif resp.status_code == 401:
                print(f"  [401权限不足] {desc}")
            elif resp.status_code == 403:
                print(f"  [403禁止访问] {desc}")
            else:
                print(f"  [失败] {desc}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [异常] {desc}: {e}")
    
    # 3. 测试获取评审专家池
    print("\n[步骤3] 获取评审专家池")
    
    reviewer_endpoints = [
        ("/api/admin/reviewers", "评审专家列表（管理端）"),
        ("/api/admin/reviewers?expertBackground=MEDICAL", "按背景筛选评审专家"),
    ]
    
    for endpoint, desc in reviewer_endpoints:
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    count = len(data.get("data", []))
                    print(f"  [成功] {desc}: 返回 {count} 条数据")
                else:
                    print(f"  [失败] {desc}: {data.get('message')}")
            elif resp.status_code == 401:
                print(f"  [401权限不足] {desc} - 需要修复")
            elif resp.status_code == 403:
                print(f"  [403禁止访问] {desc} - 需要修复")
            else:
                print(f"  [失败] {desc}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [异常] {desc}: {e}")
    
    # 4. 测试分配评审任务
    print("\n[步骤4] 测试分配评审任务权限")
    
    task_endpoint = "/api/admin/reviews/tasks"
    try:
        # 不实际分配，只测试权限
        resp = requests.post(f"{BASE_URL}{task_endpoint}", headers=headers, 
                            json={"registrationId": 106, "reviewerId": 6, "stage": "BOOK"},
                            timeout=10)
        
        if resp.status_code == 200:
            print(f"  [成功] 可以分配评审任务")
        elif resp.status_code == 400:
            data = resp.json()
            # 400可能是参数问题，不是权限问题
            print(f"  [部分成功] 权限OK，但参数可能有误: {data}")
        elif resp.status_code == 401:
            print(f"  [401权限不足] 无法分配评审任务 - 需要修复")
        elif resp.status_code == 403:
            print(f"  [403禁止访问] 无法分配评审任务 - 需要修复")
        else:
            print(f"  [失败] HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [异常] {e}")
    
    # 5. 测试查看评审汇总
    print("\n[步骤5] 测试查看评审汇总权限")
    
    summary_endpoints = [
        ("/api/admin/reviews/summary?competitionId=21&stage=BOOK", "评审汇总"),
        ("/api/admin/reviews/rankings?competitionId=21&stage=BOOK", "评审排名"),
        ("/api/admin/stats/summary", "统计数据"),
    ]
    
    for endpoint, desc in summary_endpoints:
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            if resp.status_code == 200:
                print(f"  [成功] {desc}")
            elif resp.status_code == 401:
                print(f"  [401权限不足] {desc} - 需要修复")
            elif resp.status_code == 403:
                print(f"  [403禁止访问] {desc} - 需要修复")
            else:
                print(f"  [失败] {desc}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [异常] {desc}: {e}")
    
    print("\n" + "="*80)
    print("权限测试完成")
    print("="*80)

if __name__ == "__main__":
    if wait_for_server():
        test_committee_access()
    else:
        print("无法连接到服务器")
