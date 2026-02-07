#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""通过API检查舟山医院项目数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import time

BASE_URL = "http://localhost:6031"

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", 
        json={
            "phone": "13900000000",
            "name": "Admin User",
            "title": "Manager",
            "role": "OPS",
            "institutionId": 1
        })
    
    if response.status_code == 200:
        return response.json()['data']['token']
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return None

def check_projects(token):
    """检查项目数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 获取书审阶段的项目列表（舟山医院）
    print("=" * 120)
    print("检查书审阶段-舟山医院项目")
    print("=" * 120)
    print()
    
    # 获取报名筛选列表，按机构筛选
    response = requests.get(
        f"{BASE_URL}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "institutionId": 17  # 舟山医院
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取失败: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()['data']
    projects = data.get('content', data) if isinstance(data, dict) else data
    
    print(f"找到 {len(projects)} 个项目\n")
    
    # 检查每个项目的详细信息
    missing_count = 0
    for i, project in enumerate(projects, 1):
        reg_id = project.get('registrationId') or project.get('id')
        
        # 获取项目详情
        detail_response = requests.get(
            f"{BASE_URL}/api/registrations/{reg_id}",
            headers=headers
        )
        
        if detail_response.status_code != 200:
            print(f"❌ [{i}] 获取项目{reg_id}详情失败")
            continue
        
        detail = detail_response.json()['data']
        activity = detail.get('activityInfo', {})
        
        # 检查必要字段
        method_code = activity.get('methodCode')
        subject_type = activity.get('subjectTypeCode')
        quality_topic = activity.get('qualityTopicCode')
        theme = activity.get('theme')
        
        has_method = method_code is not None and method_code != ''
        has_subject = subject_type is not None and subject_type != ''
        has_quality = quality_topic is not None and quality_topic != ''
        has_theme = theme is not None and theme != ''
        
        is_complete = has_method and has_subject and has_quality and has_theme
        
        status = "✅" if is_complete else "❌"
        
        print(f"{status} [{i}] 项目ID: {reg_id}")
        print(f"    项目: {detail.get('projectName', '')[:50]}...")
        print(f"    申请人: {detail.get('applicantName', '')} | 分组: {detail.get('groupCode', '')}")
        print(f"    品管工具 (methodCode): {method_code or '❌ 缺失'}")
        print(f"    主题类型 (subjectTypeCode): {subject_type or '❌ 缺失'}")
        print(f"    质量主题 (qualityTopicCode): {quality_topic or '❌ 缺失'}")
        print(f"    主题 (theme): {theme or '❌ 缺失'}")
        
        if not is_complete:
            missing_count += 1
        
        print()
    
    print("=" * 120)
    print(f"统计: 总共{len(projects)}个项目, {missing_count}个缺失字段")
    print("=" * 120)

def main():
    """主函数"""
    print("正在登录...")
    token = login()
    
    if not token:
        return
    
    print("✅ 登录成功\n")
    
    check_projects(token)

if __name__ == "__main__":
    main()
