#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查是否有报名填写了项目摘要"""

import requests
import json

BASE_URL = "http://localhost:6031"

def login():
    """登录"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "phone": "13800000041",
        "name": "CommitteeAdmin A",
        "role": "COMMITTEE_ADMIN"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result.get("data", {}).get("token")
    return None

def check_summaries():
    """检查项目摘要"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取所有报名
    url = f"{BASE_URL}/api/admin/registrations/filter?competitionId=23"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 获取报名列表失败: HTTP {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API返回失败: {result.get('message')}")
        return
    
    registrations = result.get("data", [])
    print(f"共有 {len(registrations)} 个报名\n")
    
    # 检查每个报名的详情
    has_summary_count = 0
    no_summary_count = 0
    
    for reg in registrations[:20]:  # 只检查前20个
        reg_id = reg.get("id")
        detail_url = f"{BASE_URL}/api/registrations/{reg_id}"
        detail_response = requests.get(detail_url, headers=headers)
        
        if detail_response.status_code == 200:
            detail_result = detail_response.json()
            if detail_result.get("success"):
                data = detail_result.get("data", {})
                summary = data.get("projectSummary")
                
                if summary:
                    has_summary_count += 1
                    print(f"✅ 报名ID {reg_id}: 有projectSummary")
                    print(f"   字段: theme={bool(summary.get('theme'))}, plan={bool(summary.get('plan'))}, problem={bool(summary.get('problem'))}")
                    print(f"         action={bool(summary.get('action'))}, success={bool(summary.get('success'))}, discussion={bool(summary.get('discussion'))}")
                    print(f"         operation={bool(summary.get('operation'))}, presentation={bool(summary.get('presentation'))}")
                    
                    # 如果找到一个有数据的，显示完整内容
                    if has_summary_count == 1:
                        print("\n" + "=" * 80)
                        print("第一个有projectSummary的报名详细内容:")
                        print("=" * 80)
                        print(json.dumps(summary, ensure_ascii=False, indent=2))
                        print("=" * 80 + "\n")
                else:
                    no_summary_count += 1
    
    print(f"\n统计结果:")
    print(f"  有projectSummary: {has_summary_count}")
    print(f"  无projectSummary: {no_summary_count}")

if __name__ == "__main__":
    check_summaries()
