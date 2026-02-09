#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复评委英文名称，改为真实的中文姓名和职称"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from db_config import DB_CONFIG

# 数据库连接
conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor()

print("="*80)
print("修复评委英文名称")
print("="*80)

# 定义要更新的评委信息
reviewer_updates = [
    {
        'phone': '13800000021',
        'old_name': 'Reviewer A',
        'name': '李明华',
        'title': '主任医师',
        'expert_background': 'MEDICAL',
        'institution_id': 2,  # 浙江大学医学院附属第二医院
        'reviewer_group_code': 'A1',
        'interview_group_code': 'A1'
    },
    {
        'phone': '13800000022',
        'old_name': 'Reviewer B',
        'name': '张秀英',
        'title': '护理部主任',
        'expert_background': 'NURSING',
        'institution_id': 1,  # 浙江大学医学院附属第一医院
        'reviewer_group_code': 'A1',
        'interview_group_code': 'A1'
    },
    {
        'phone': '13800000023',
        'old_name': 'Reviewer C',
        'name': '陈明',
        'title': '质控科主任',
        'expert_background': 'MANAGEMENT',
        'institution_id': 3,  # 浙江省人民医院
        'reviewer_group_code': 'A1',
        'interview_group_code': 'A1'
    },
    {
        'phone': '13800000024',
        'old_name': 'Reviewer D',
        'name': '刘建平',
        'title': '副主任医师',
        'expert_background': 'MEDICAL',
        'institution_id': 4,  # 浙江省中医院
        'reviewer_group_code': 'B2',
        'interview_group_code': 'B2'
    },
    {
        'phone': '13800000025',
        'old_name': 'Reviewer E',
        'name': '王芳',
        'title': '主任护师',
        'expert_background': 'NURSING',
        'institution_id': 5,  # 杭州市第一人民医院
        'reviewer_group_code': 'B2',
        'interview_group_code': 'B2'
    },
    {
        'phone': '13800000026',
        'old_name': 'Reviewer F',
        'name': '赵强',
        'title': '医务处主任',
        'expert_background': 'MANAGEMENT',
        'institution_id': 6,  # 杭州市中医院
        'reviewer_group_code': 'B2',
        'interview_group_code': 'B2'
    }
]

updated_count = 0

for reviewer in reviewer_updates:
    print(f"\n更新: {reviewer['old_name']} -> {reviewer['name']}")
    
    try:
        cursor.execute("""
            UPDATE user_accounts
            SET name = %s,
                title = %s,
                expert_background = %s,
                institution_id = %s,
                reviewer_group_code = %s,
                interview_group_code = %s
            WHERE phone = %s AND role = 'REVIEWER'
        """, (
            reviewer['name'],
            reviewer['title'],
            reviewer['expert_background'],
            reviewer['institution_id'],
            reviewer['reviewer_group_code'],
            reviewer['interview_group_code'],
            reviewer['phone']
        ))
        
        if cursor.rowcount > 0:
            print(f"  ✅ 已更新")
            print(f"     姓名: {reviewer['name']}")
            print(f"     职称: {reviewer['title']}")
            print(f"     专家背景: {reviewer['expert_background']}")
            print(f"     机构ID: {reviewer['institution_id']}")
            print(f"     分组: {reviewer['reviewer_group_code']}")
            updated_count += 1
        else:
            print(f"  ⚠️  未找到该评委")
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")

conn.commit()

print("\n" + "="*80)
print(f"更新完成！共更新 {updated_count} 个评委")
print("="*80)

# 验证更新结果
print("\n验证更新结果:\n")

cursor.execute("""
    SELECT u.id, u.phone, u.name, u.title, u.expert_background,
           i.name as institution_name
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.phone IN (
        '13800000021', '13800000022', '13800000023',
        '13800000024', '13800000025', '13800000026'
    )
    AND u.role = 'REVIEWER'
    ORDER BY u.phone
""")

reviewers = cursor.fetchall()

for r in reviewers:
    print(f"{r[2]} ({r[1]})")
    print(f"  职称: {r[3]}")
    print(f"  专家背景: {r[4]}")
    print(f"  机构: {r[5]}")
    print()

cursor.close()
conn.close()

print("✅ 所有评委信息已更新为真实的中文姓名和完整信息！")
