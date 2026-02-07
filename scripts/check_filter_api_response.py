#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查筛选API返回的实际数据结构
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
    print("检查筛选API返回的数据结构")
    print("="*80)
    
    # 查询
    response = requests.get(f"{BASE_URL}/api/admin/registrations/filter",
                           params={"competitionId": 21},
                           headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        if isinstance(data, dict) and "content" in data:
            print("\n✅ 返回分页对象")
            print(f"totalCount: {data.get('totalCount')}")
            print(f"pageNo: {data.get('pageNo')}")
            print(f"pageSize: {data.get('pageSize')}")
            items = data["content"]
        else:
            print("\n✅ 返回数组")
            items = data
        
        print(f"\n总数: {len(items)}")
        
        if items:
            print("\n第1个项目的完整数据:")
            print(json.dumps(items[0], ensure_ascii=False, indent=2))
            
            print("\n第1个项目的所有字段名:")
            print(list(items[0].keys()))
            
            print("\n查找项目138:")
            # 尝试不同的字段名
            for item in items:
                if item.get('id') == 138:
                    print("✅ 通过'id'字段找到138")
                    print(json.dumps(item, ensure_ascii=False, indent=2))
                    break
                elif item.get('registrationId') == 138:
                    print("✅ 通过'registrationId'字段找到138")
                    print(json.dumps(item, ensure_ascii=False, indent=2))
                    break
            else:
                print("❌ 未找到138")
                
                # 打印所有ID（两种可能的字段名）
                ids_by_id = [item.get('id') for item in items if item.get('id') is not None]
                ids_by_registrationId = [item.get('registrationId') for item in items if item.get('registrationId') is not None]
                
                print(f"\n通过'id'字段获取的ID: {ids_by_id[:10]}... (前10个)")
                print(f"通过'registrationId'字段获取的ID: {ids_by_registrationId[:10]}... (前10个)")
    else:
        print(f"\n❌ 请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
