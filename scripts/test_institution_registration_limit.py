#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试机构报名数量限制功能"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_registration_limit():
    """测试机构报名数量限制"""
    print("=" * 80)
    print("测试机构报名数量限制功能")
    print("=" * 80)
    
    # 1. 登录管理员
    print("\n【步骤1】登录组委会管理员")
    login_data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 查询当前限制值
    print(f"\n【步骤2】查询当前限制值")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/settings?key=maxRegistrationsPerInstitution",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            current_limit = result["data"]["settingValue"]
            print(f"✅ 当前限制值: {current_limit}")
        else:
            print(f"⚠️  配置不存在，将使用默认值 8")
            current_limit = "8"
    else:
        print(f"⚠️  查询失败，将使用默认值 8")
        current_limit = "8"
    
    # 3. 修改限制值为3（用于测试）
    print(f"\n【步骤3】修改限制值为 3（用于测试）")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/settings",
        headers=headers,
        json={
            "key": "maxRegistrationsPerInstitution",
            "value": "3"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ 修改成功: {result['data']['settingValue']}")
        else:
            print(f"❌ 修改失败: {result.get('message')}")
            return
    else:
        print(f"❌ 修改失败: {response.status_code}")
        return
    
    # 4. 查询某个机构的报名数量
    print(f"\n【步骤4】查询机构报名数量")
    
    competition_id = 21
    institution_id = 1  # 浙江大学医学院附属第二医院
    
    response = requests.get(
        f"{BASE_URL}/api/admin/registrations/filter?competitionId={competition_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            all_registrations = result["data"]
            # 筛选该机构的报名
            institution_registrations = [
                r for r in all_registrations 
                if r.get('institutionName') == '浙江大学医学院附属第二医院（浙二医院）'
            ]
            count = len(institution_registrations)
            print(f"✅ 机构 ID {institution_id} 已报名: {count} 个项目")
            print(f"   限制值: 3")
            print(f"   状态: {'已达上限' if count >= 3 else f'还可报名 {3 - count} 个'}")
        else:
            print(f"❌ 查询失败: {result.get('message')}")
    else:
        print(f"❌ 查询失败: {response.status_code}")
    
    # 5. 恢复原限制值
    print(f"\n【步骤5】恢复原限制值为 {current_limit}")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/settings",
        headers=headers,
        json={
            "key": "maxRegistrationsPerInstitution",
            "value": current_limit
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ 恢复成功: {result['data']['settingValue']}")
        else:
            print(f"❌ 恢复失败: {result.get('message')}")
    else:
        print(f"❌ 恢复失败: {response.status_code}")
    
    # 6. 显示功能说明
    print("\n" + "=" * 80)
    print("功能说明")
    print("=" * 80)
    print("""
1. 限制规则：
   - 同一机构在同一赛事中的报名项目数不得超过N个
   - 默认值：N = 8
   - 可通过系统设置修改

2. 运维操作：
   - 查询限制值：GET /api/admin/settings?key=maxRegistrationsPerInstitution
   - 修改限制值：POST /api/admin/settings
     Body: {"key": "maxRegistrationsPerInstitution", "value": "10"}

3. 错误提示：
   - 当机构报名数达到上限时，创建报名会失败
   - 错误信息：该机构报名数量已达上限（N个项目），无法继续报名

4. 注意事项：
   - 统计所有状态的报名（草稿、已提交、已退回等）
   - 修改限制值不影响已有报名
   - 只有管理员可以修改系统设置
    """)
    
    print("=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_registration_limit()
