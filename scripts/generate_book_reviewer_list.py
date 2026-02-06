#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成书审评委清单（与前端一致）"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql

# 数据库连接
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("="*80)
print("书审评委清单")
print("="*80)
print("\n来源: user_accounts 表 (role='REVIEWER')")
print("用途: 书审评委池、面试评委池、决赛评委池")
print("说明: 同一张表，通过 reviewer_group_code/interview_group_code 区分不同池子\n")

# 查询所有REVIEWER角色的用户
cursor.execute("""
    SELECT 
        u.id,
        u.phone,
        u.name,
        u.title,
        u.expert_background,
        u.reviewer_group_code,
        u.interview_group_code,
        i.id as institution_id,
        i.name as institution_name,
        (SELECT COUNT(*) FROM review_tasks rt WHERE rt.reviewer_id = u.id) as task_count
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.name
""")

reviewers = cursor.fetchall()

print("="*80)
print(f"书审评委列表（共 {len(reviewers)} 人）")
print("="*80)
print()
print(f"{'姓名':<12} {'职称':<20} {'机构':<40} {'状态':<10} {'背景':<10} {'负荷':<8}")
print("-" * 120)

# 背景翻译
bg_map = {
    'MEDICAL': '医疗',
    'NURSING': '护理',
    'MANAGEMENT': '管理',
    None: '未设置'
}

for r in reviewers:
    name = r['name'] or 'N/A'
    title = r['title'] or '未设置'
    institution = r['institution_name'] or ''
    status = '可分配'
    background = bg_map.get(r['expert_background'], '未设置')
    load = r['task_count']
    
    # 对齐输出
    name_display = name + ' ' * (12 - len(name))
    title_display = title + ' ' * (20 - len(title))
    institution_display = (institution[:38] + '..') if len(institution) > 40 else institution + ' ' * (40 - len(institution))
    
    print(f"{name_display} {title_display} {institution_display} {status:<10} {background:<10} {load:<8}")

print()
print("="*80)
print("字段说明")
print("="*80)
print()
print("表: user_accounts")
print("  - role = 'REVIEWER' (评委角色)")
print("  - reviewer_group_code: 书审分组 (A1/B1/B2等)")
print("  - interview_group_code: 面试分组 (A1/B1/B2等)")
print("  - expert_background: 专家背景 (MEDICAL/NURSING/MANAGEMENT)")
print()
print("评委池设计:")
print("  - 书审评委池: 根据 reviewer_group_code 筛选")
print("  - 面试评委池: 根据 interview_group_code 筛选")
print("  - 决赛评委池: 可以是面试评委的子集或单独配置")
print()
print("分配逻辑:")
print("  - 自动分配时，根据 stage 类型选择对应的分组码")
print("  - BOOK/FINAL 阶段: 使用 reviewer_group_code")
print("  - INTERVIEW 阶段: 使用 interview_group_code")
print()

# 统计信息
print("="*80)
print("统计信息")
print("="*80)
print()

cursor.execute("""
    SELECT expert_background, COUNT(*) as count
    FROM user_accounts
    WHERE role = 'REVIEWER'
    GROUP BY expert_background
""")

bg_stats = cursor.fetchall()

print("按专家背景统计:")
for stat in bg_stats:
    bg = bg_map.get(stat['expert_background'], '未设置')
    count = stat['count']
    print(f"  {bg}: {count} 人")

cursor.execute("""
    SELECT reviewer_group_code, COUNT(*) as count
    FROM user_accounts
    WHERE role = 'REVIEWER'
    GROUP BY reviewer_group_code
    ORDER BY reviewer_group_code
""")

group_stats = cursor.fetchall()

print("\n按书审分组统计:")
for stat in group_stats:
    group = stat['reviewer_group_code'] or '未设置'
    count = stat['count']
    print(f"  {group}: {count} 人")

cursor.execute("""
    SELECT u.id, u.name, COUNT(rt.id) as task_count
    FROM user_accounts u
    INNER JOIN review_tasks rt ON u.id = rt.reviewer_id
    WHERE u.role = 'REVIEWER'
    GROUP BY u.id, u.name
    ORDER BY task_count DESC
""")

load_stats = cursor.fetchall()

if load_stats:
    print("\n当前负荷统计（有任务的评委）:")
    for stat in load_stats:
        print(f"  {stat['name']}: {stat['task_count']} 个任务")
else:
    print("\n当前负荷: 所有评委负荷为 0")

cursor.close()
conn.close()

print("\n" + "="*80)
print("✅ 数据来源: d_hos_pinguan_traegj_20260205.user_accounts")
print("✅ 前端API: GET /api/admin/reviewers")
print("="*80)
