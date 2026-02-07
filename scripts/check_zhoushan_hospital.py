#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询舟山医院是否存在
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
    print("查询舟山医院")
    print("="*80)
    
    # 查询所有机构
    response = requests.get(f"{BASE_URL}/api/admin/institutions",
                           headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        # 处理分页和非分页两种情况
        if isinstance(data, dict) and "content" in data:
            institutions = data["content"]
        else:
            institutions = data
        
        print(f"\n总共 {len(institutions)} 个机构\n")
        
        # 查找舟山医院
        zhoushan_hospitals = []
        for inst in institutions:
            if "舟山" in inst.get("name", ""):
                zhoushan_hospitals.append(inst)
        
        if zhoushan_hospitals:
            print(f"✅ 找到 {len(zhoushan_hospitals)} 个包含'舟山'的医院:\n")
            for inst in zhoushan_hospitals:
                print(f"ID: {inst.get('id')}")
                print(f"名称: {inst.get('name')}")
                print(f"代码: {inst.get('code')}")
                print(f"统一社会信用代码: {inst.get('uscc')}")
                print(f"地区: {inst.get('region')}")
                print(f"等级: {inst.get('level')}")
                print(f"创建时间: {inst.get('createdAt')}")
                print("-" * 80)
                
                # 查询该机构的报名项目
                reg_response = requests.get(f"{BASE_URL}/api/registrations/by-institution",
                                           params={"institutionId": inst.get('id')},
                                           headers={"Authorization": f"Bearer {token}"})
                if reg_response.status_code == 200:
                    registrations = reg_response.json()["data"]
                    print(f"📋 该机构有 {len(registrations)} 个报名项目:")
                    for reg in registrations:
                        print(f"  - ID: {reg.get('id')}, 项目: {reg.get('projectName')}, 状态: {reg.get('status')}")
                print("=" * 80 + "\n")
        else:
            print("❌ 未找到舟山医院")
            print("\n所有机构名称列表:")
            for inst in institutions[:20]:
                print(f"  - {inst.get('name')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
