#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查项目138的详细情况
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:6031"

def login():
    """登录"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Manager",
        "role": "OPS",
        "institutionId": 1
    })
    return response.json()["data"]["token"]

def main():
    token = login()
    
    print("="*80)
    print("检查项目138")
    print("="*80)
    
    # 1. 查询详情
    print("\n1️⃣  GET /api/registrations/138")
    response = requests.get(f"{BASE_URL}/api/registrations/138", 
                           headers={"Authorization": f"Bearer {token}"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"返回数据:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print(f"错误: {response.text}")
    
    # 2. 查询所有项目看是否包含138
    print("\n2️⃣  GET /api/admin/registrations/filter?competitionId=21")
    response = requests.get(f"{BASE_URL}/api/admin/registrations/filter",
                           params={"competitionId": 21},
                           headers={"Authorization": f"Bearer {token}"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        if isinstance(data, dict) and "content" in data:
            registrations = data["content"]
            total = data["totalCount"]
        else:
            registrations = data
            total = len(registrations)
        
        print(f"总数: {total}")
        
        # 查找138
        found = None
        for reg in registrations:
            if reg.get("id") == 138:
                found = reg
                break
        
        if found:
            print(f"\n✅ 找到项目138:")
            print(json.dumps(found, ensure_ascii=False, indent=2))
        else:
            print(f"\n❌ 未找到项目138")
            print(f"\n前5个项目的ID: {[r.get('id') for r in registrations[:5]]}")
            
            # 检查是否有138附近的ID
            nearby_ids = [r.get('id') for r in registrations if 135 <= r.get('id', 0) <= 140]
            if nearby_ids:
                print(f"138附近的ID: {nearby_ids}")
    
    # 3. 直接查询所有项目（不分页，不筛选）
    print("\n3️⃣  GET /api/admin/registrations/filter (无筛选)")
    response = requests.get(f"{BASE_URL}/api/admin/registrations/filter",
                           params={},
                           headers={"Authorization": f"Bearer {token}"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        if isinstance(data, list):
            all_ids = [r.get('id') for r in data]
            print(f"总共 {len(all_ids)} 个项目")
            if 138 in all_ids:
                print(f"✅ 138存在于所有项目中")
                # 找到并打印
                for r in data:
                    if r.get('id') == 138:
                        print(json.dumps(r, ensure_ascii=False, indent=2))
            else:
                print(f"❌ 138不存在于所有项目中")
                print(f"ID范围: {min(all_ids)} - {max(all_ids)}")

if __name__ == "__main__":
    main()
