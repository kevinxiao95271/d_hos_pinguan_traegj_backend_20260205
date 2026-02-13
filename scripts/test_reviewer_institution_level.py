#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评审专家列表接口的institutionLevel字段
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def main():
    print("=" * 80)
    print("测试评审专家列表 - institutionLevel字段")
    print("=" * 80)
    
    # 1. 管理员登录
    print("\n[1] 管理员登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    })
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(login_resp.text)
        return
    
    token = login_resp.json()['data']['token']
    print("✅ 登录成功")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 2. 获取评审专家列表
    print("\n[2] 获取评审专家列表...")
    reviewers_resp = requests.get(
        f"{BASE_URL}/api/admin/reviewers",
        headers=headers
    )
    
    if reviewers_resp.status_code != 200:
        print(f"❌ 获取失败: {reviewers_resp.status_code}")
        print(reviewers_resp.text)
        return
    
    reviewers = reviewers_resp.json()['data']
    print(f"✅ 获取成功，共 {len(reviewers)} 名评审专家")
    
    # 3. 检查字段
    print("\n[3] 检查字段完整性...")
    required_fields = [
        'id', 'phone', 'name', 'title', 
        'institutionId', 'institutionName', 'institutionLevel',
        'expertBackground', 'currentLoad'
    ]
    
    if not reviewers:
        print("⚠️  没有评审专家数据")
        return
    
    first_reviewer = reviewers[0]
    missing_fields = [field for field in required_fields if field not in first_reviewer]
    
    if missing_fields:
        print(f"❌ 缺少字段: {', '.join(missing_fields)}")
        print(f"实际字段: {list(first_reviewer.keys())}")
        return
    
    print("✅ 所有必需字段都存在")
    
    # 4. 显示示例数据
    print("\n[4] 示例数据（前5名）:")
    print("-" * 80)
    print(f"{'ID':<4} | {'姓名':<10} | {'职称':<12} | {'机构':<25} | {'机构等级':<10} | {'负荷':<4}")
    print("-" * 80)
    
    for reviewer in reviewers[:5]:
        print(f"{reviewer['id']:<4} | "
              f"{reviewer['name']:<10} | "
              f"{reviewer.get('title', ''):<12} | "
              f"{reviewer.get('institutionName', '')[:25]:<25} | "
              f"{reviewer.get('institutionLevel', ''):<10} | "
              f"{reviewer['currentLoad']:<4}")
    
    # 5. 统计机构等级分布
    print("\n[5] 机构等级分布:")
    level_count = {}
    for reviewer in reviewers:
        level = reviewer.get('institutionLevel') or '未设置'
        level_count[level] = level_count.get(level, 0) + 1
    
    print("-" * 40)
    for level, count in sorted(level_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {level:<15}: {count:3d}人 ({count/len(reviewers)*100:.1f}%)")
    
    # 6. 完整JSON示例
    print("\n[6] 完整JSON示例（第1名评审专家）:")
    print("-" * 80)
    print(json.dumps(first_reviewer, ensure_ascii=False, indent=2))
    
    # 7. 验证数据结构
    print("\n[7] 数据结构验证:")
    print("-" * 80)
    
    checks = {
        'id是数字': isinstance(first_reviewer['id'], int),
        'institutionLevel是字符串或null': isinstance(first_reviewer.get('institutionLevel'), (str, type(None))),
        'currentLoad是数字': isinstance(first_reviewer['currentLoad'], int),
        'institutionName存在': 'institutionName' in first_reviewer,
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    # 8. 测试筛选功能
    print("\n[8] 测试筛选功能...")
    
    # 按机构筛选
    if reviewers and reviewers[0].get('institutionId'):
        inst_id = reviewers[0]['institutionId']
        filtered_resp = requests.get(
            f"{BASE_URL}/api/admin/reviewers?institutionId={inst_id}",
            headers=headers
        )
        if filtered_resp.status_code == 200:
            filtered = filtered_resp.json()['data']
            print(f"  ✅ 按机构筛选: 找到 {len(filtered)} 名评审专家")
            if filtered:
                print(f"     示例: {filtered[0]['name']} - {filtered[0].get('institutionName')} ({filtered[0].get('institutionLevel')})")
        else:
            print(f"  ❌ 按机构筛选失败: {filtered_resp.status_code}")
    
    # 按专业背景筛选
    if reviewers and reviewers[0].get('expertBackground'):
        bg = reviewers[0]['expertBackground']
        filtered_resp = requests.get(
            f"{BASE_URL}/api/admin/reviewers?expertBackground={bg}",
            headers=headers
        )
        if filtered_resp.status_code == 200:
            filtered = filtered_resp.json()['data']
            print(f"  ✅ 按专业背景筛选({bg}): 找到 {len(filtered)} 名评审专家")
        else:
            print(f"  ❌ 按专业背景筛选失败: {filtered_resp.status_code}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    
    # 总结
    print("\n✅ institutionLevel字段已成功添加到评审专家列表接口")
    print("\n响应格式:")
    print("""
{
  "id": 14,
  "phone": "13800000001",
  "name": "评委姓名",
  "title": "主任护师",
  "institutionId": 1,
  "institutionName": "浙江大学医学院附属第二医院",
  "institutionLevel": "三级甲等",  ← 新增字段
  "expertBackground": "MEDICAL",
  "currentLoad": 0
}
    """)

if __name__ == '__main__':
    main()
