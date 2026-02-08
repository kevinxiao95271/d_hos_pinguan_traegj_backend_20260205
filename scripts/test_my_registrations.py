#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试我的报名接口"""

import requests
import json

BASE_URL = "http://localhost:6031"

def login_contestant():
    """登录参赛者账号"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": "13900000001",
        "name": "张三",
        "role": "CONTESTANT"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result.get("data", {}).get("token")
    return None

def test_my_registrations():
    """测试我的报名接口"""
    token = login_contestant()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=" * 100)
    print("测试我的报名接口")
    print("=" * 100)
    
    url = f"{BASE_URL}/api/registrations/my"
    print(f"\n请求URL: {url}\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"响应状态码: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", [])
            
            print(f"✅ 请求成功！")
            print(f"报名数量: {len(data)}\n")
            
            if len(data) > 0:
                print("=" * 100)
                print("报名列表详情")
                print("=" * 100)
                
                for i, reg in enumerate(data, 1):
                    print(f"\n报名 {i}:")
                    print(f"  报名ID: {reg.get('id')}")
                    print(f"  项目名称: {reg.get('projectName')}")
                    print(f"  组别: {reg.get('groupType')}")
                    print(f"  分组: {reg.get('groupCode')}")
                    print(f"  状态: {reg.get('status')}")
                    print(f"  提交时间: {reg.get('submittedAt')}")
                    print(f"  创建时间: {reg.get('createdAt')}")
                    print(f"\n  机构信息:")
                    print(f"    机构ID: {reg.get('institutionId')}")
                    print(f"    机构名称: {reg.get('institutionName')}")
                    print(f"    机构等级: {reg.get('institutionLevel')}")
                    print(f"\n  赛事信息:")
                    print(f"    赛事ID: {reg.get('competitionId')}")
                    print(f"    赛事名称: {reg.get('competitionName')}")
                
                # 检查字段完整性
                print("\n" + "=" * 100)
                print("字段完整性检查")
                print("=" * 100)
                
                required_fields = [
                    'id', 'projectName', 'groupType', 'groupCode', 'status',
                    'institutionId', 'institutionName', 'institutionLevel',
                    'competitionId', 'competitionName'
                ]
                
                missing_counts = {field: 0 for field in required_fields}
                
                for reg in data:
                    for field in required_fields:
                        if not reg.get(field):
                            missing_counts[field] += 1
                
                print(f"\n总报名数: {len(data)}")
                print(f"\n字段缺失统计:")
                
                all_complete = True
                for field, count in missing_counts.items():
                    status = "✅" if count == 0 else "⚠️"
                    if count > 0:
                        all_complete = False
                    print(f"  {status} {field}: {count} 条记录缺失 ({count/len(data)*100:.1f}%)")
                
                if all_complete:
                    print("\n✅ 所有字段完整！")
                else:
                    print("\n⚠️ 部分字段缺失")
                
                # 显示完整的JSON（第一条）
                print("\n" + "=" * 100)
                print("第一条报名的完整JSON")
                print("=" * 100)
                print(json.dumps(data[0], ensure_ascii=False, indent=2))
                
            else:
                print("⚠️  没有报名记录")
        else:
            print(f"❌ API返回失败: {result.get('message')}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"响应内容: {response.text}")

if __name__ == "__main__":
    test_my_registrations()
