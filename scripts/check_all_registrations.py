#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量查询所有报名数据，检查methodLabel和subjectTypeLabel的实际情况
"""

import requests
import json

# API配置
BASE_URL = "http://localhost:6031"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
FILTER_URL = f"{BASE_URL}/api/admin/registrations/filter"

# 登录信息 - 使用OPS账号
LOGIN_DATA = {
    "phone": "13900000000",
    "name": "Admin User",
    "title": "Manager",
    "role": "OPS",
    "institutionId": 1
}

def login():
    """登录并获取token"""
    print("=" * 80)
    print("步骤1: 管理员登录")
    print("=" * 80)
    response = requests.post(LOGIN_URL, json=LOGIN_DATA)
    print(f"登录响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result.get('data', {}).get('token')
        print(f"[OK] Login successful, token retrieved")
        return token
    else:
        print(f"[ERROR] Login failed (status {response.status_code})")
        print(f"Response: {response.text}")
        return None

def check_all_registrations(token):
    """全量查询所有报名数据"""
    print("\n" + "=" * 80)
    print("步骤2: 全量查询所有报名数据（不带任何filter）")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"competitionId": 1}  # 只传competitionId，不传任何filter
    
    response = requests.get(FILTER_URL, headers=headers, params=params)
    print(f"查询响应状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ 查询失败: {response.text}")
        return
    
    result = response.json()
    data = result.get('data', [])
    
    print(f"\n总共查询到 {len(data)} 条报名记录")
    
    # 统计分析
    total = len(data)
    has_method_label = 0
    has_subject_label = 0
    has_method_code = 0
    has_subject_code = 0
    has_both_labels = 0
    empty_both_labels = 0
    
    # 详细记录
    records_with_labels = []
    records_without_labels = []
    
    for item in data:
        reg_id = item.get('registrationId')
        project_name = item.get('projectName', 'N/A')
        institution = item.get('institutionName', 'N/A')
        method_code = item.get('methodCode', '')
        method_label = item.get('methodLabel', '')
        subject_code = item.get('subjectTypeCode', '')
        subject_label = item.get('subjectTypeLabel', '')
        
        # 统计
        if method_label and method_label.strip():
            has_method_label += 1
        if subject_label and subject_label.strip():
            has_subject_label += 1
        if method_code and method_code.strip():
            has_method_code += 1
        if subject_code and subject_code.strip():
            has_subject_code += 1
        
        if (method_label and method_label.strip()) and (subject_label and subject_label.strip()):
            has_both_labels += 1
            records_with_labels.append({
                'id': reg_id,
                'project': project_name,
                'institution': institution,
                'methodCode': method_code,
                'methodLabel': method_label,
                'subjectCode': subject_code,
                'subjectLabel': subject_label
            })
        elif not (method_label and method_label.strip()) and not (subject_label and subject_label.strip()):
            empty_both_labels += 1
            records_without_labels.append({
                'id': reg_id,
                'project': project_name,
                'institution': institution,
                'methodCode': method_code,
                'methodLabel': method_label,
                'subjectCode': subject_code,
                'subjectLabel': subject_label
            })
    
    # 打印统计结果
    print("\n" + "=" * 80)
    print("统计结果")
    print("=" * 80)
    print(f"总记录数: {total}")
    print(f"有 methodLabel 的记录: {has_method_label} ({has_method_label*100//total if total > 0 else 0}%)")
    print(f"有 subjectTypeLabel 的记录: {has_subject_label} ({has_subject_label*100//total if total > 0 else 0}%)")
    print(f"有 methodCode 的记录: {has_method_code} ({has_method_code*100//total if total > 0 else 0}%)")
    print(f"有 subjectTypeCode 的记录: {has_subject_code} ({has_subject_code*100//total if total > 0 else 0}%)")
    print(f"两个label都有的记录: {has_both_labels} ({has_both_labels*100//total if total > 0 else 0}%)")
    print(f"两个label都为空的记录: {empty_both_labels} ({empty_both_labels*100//total if total > 0 else 0}%)")
    
    # 打印有label的示例（前5条）
    print("\n" + "=" * 80)
    print("有完整label的记录示例（前5条）")
    print("=" * 80)
    for record in records_with_labels[:5]:
        print(f"\nID: {record['id']}")
        print(f"  项目: {record['project']}")
        print(f"  机构: {record['institution']}")
        print(f"  methodCode: {record['methodCode']} -> methodLabel: {record['methodLabel']}")
        print(f"  subjectCode: {record['subjectCode']} -> subjectLabel: {record['subjectLabel']}")
    
    # 打印没有label的示例（前10条）
    print("\n" + "=" * 80)
    print("label为空的记录示例（前10条）")
    print("=" * 80)
    for record in records_without_labels[:10]:
        print(f"\nID: {record['id']}")
        print(f"  项目: {record['project']}")
        print(f"  机构: {record['institution']}")
        print(f"  methodCode: '{record['methodCode']}' -> methodLabel: '{record['methodLabel']}'")
        print(f"  subjectCode: '{record['subjectCode']}' -> subjectLabel: '{record['subjectLabel']}'")
    
    # 重点分析：检查舟山医院的数据
    print("\n" + "=" * 80)
    print("重点分析：舟山医院的数据")
    print("=" * 80)
    zhoushan_records = [item for item in data if '舟山' in item.get('institutionName', '')]
    print(f"舟山医院记录数: {len(zhoushan_records)}")
    
    for item in zhoushan_records:
        print(f"\nID: {item.get('registrationId')}")
        print(f"  项目: {item.get('projectName', 'N/A')}")
        print(f"  methodCode: '{item.get('methodCode', '')}' -> methodLabel: '{item.get('methodLabel', '')}'")
        print(f"  subjectCode: '{item.get('subjectTypeCode', '')}' -> subjectLabel: '{item.get('subjectTypeLabel', '')}'")

def main():
    # 登录
    token = login()
    if not token:
        return
    
    # 全量查询
    check_all_registrations(token)
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
