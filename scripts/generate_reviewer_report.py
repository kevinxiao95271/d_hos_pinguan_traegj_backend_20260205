#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成评委数据报告
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql
from collections import defaultdict

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def main():
    print("="*80)
    print("评委数据报告")
    print("="*80)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 获取所有评委
    cursor.execute("""
        SELECT 
            ua.id,
            ua.phone,
            ua.name,
            ua.title,
            i.name as institution_name,
            ua.reviewer_group_code,
            ua.interview_group_code,
            ua.expert_background
        FROM user_accounts ua
        LEFT JOIN institutions i ON ua.institution_id = i.id
        WHERE ua.role = 'REVIEWER'
        ORDER BY ua.id
    """)
    
    reviewers = cursor.fetchall()
    
    print(f"\n总评委数量: {len(reviewers)}")
    print("\n" + "="*80)
    
    # 按专家背景分组
    by_background = defaultdict(list)
    for r in reviewers:
        bg = r['expert_background'] or '未设置'
        by_background[bg].append(r)
    
    print("\n按专家背景分类:")
    print("-"*80)
    for bg, items in sorted(by_background.items()):
        print(f"  {bg}: {len(items)}人")
    
    # 按初审分组
    by_reviewer_group = defaultdict(list)
    for r in reviewers:
        group = r['reviewer_group_code'] or '未分组'
        by_reviewer_group[group].append(r)
    
    print("\n按初审分组分类:")
    print("-"*80)
    for group, items in sorted(by_reviewer_group.items()):
        print(f"  {group}: {len(items)}人")
    
    # 按终审分组
    by_interview_group = defaultdict(list)
    for r in reviewers:
        group = r['interview_group_code'] or '未分组'
        by_interview_group[group].append(r)
    
    print("\n按终审分组分类:")
    print("-"*80)
    for group, items in sorted(by_interview_group.items()):
        print(f"  {group}: {len(items)}人")
    
    # 详细列表
    print("\n\n评委详细列表:")
    print("="*80)
    print(f"{'ID':<5} {'姓名':<15} {'手机号':<15} {'机构':<30} {'背景':<10}")
    print("-"*80)
    
    for r in reviewers:
        print(f"{r['id']:<5} {r['name']:<15} {r['phone']:<15} {(r['institution_name'] or 'N/A'):<30} {(r['expert_background'] or 'N/A'):<10}")
    
    # 生成Markdown报告
    with open('评委数据报告.md', 'w', encoding='utf-8') as f:
        f.write("# 评委数据报告\n\n")
        f.write(f"**生成时间:** 2026-02-06\n\n")
        f.write(f"**总评委数量:** {len(reviewers)}\n\n")
        
        f.write("## 按专家背景分类\n\n")
        f.write("| 专家背景 | 人数 |\n")
        f.write("|---------|-----|\n")
        for bg, items in sorted(by_background.items()):
            f.write(f"| {bg} | {len(items)} |\n")
        
        f.write("\n## 按初审分组分类\n\n")
        f.write("| 初审分组 | 人数 |\n")
        f.write("|---------|-----|\n")
        for group, items in sorted(by_reviewer_group.items()):
            f.write(f"| {group} | {len(items)} |\n")
        
        f.write("\n## 按终审分组分类\n\n")
        f.write("| 终审分组 | 人数 |\n")
        f.write("|---------|-----|\n")
        for group, items in sorted(by_interview_group.items()):
            f.write(f"| {group} | {len(items)} |\n")
        
        f.write("\n## 评委详细列表\n\n")
        f.write("| ID | 姓名 | 手机号 | 机构 | 职称 | 专家背景 | 初审组 | 终审组 |\n")
        f.write("|----|------|--------|------|------|---------|-------|-------|\n")
        
        for r in reviewers:
            f.write(f"| {r['id']} | {r['name']} | {r['phone']} | {r['institution_name'] or 'N/A'} | {r['title'] or 'N/A'} | {r['expert_background'] or 'N/A'} | {r['reviewer_group_code'] or 'N/A'} | {r['interview_group_code'] or 'N/A'} |\n")
        
        f.write("\n## API访问信息\n\n")
        f.write("### 评委列表接口\n\n")
        f.write("**路径:** `GET /api/admin/reviewers`\n\n")
        f.write("**权限:** COMMITTEE, COMMITTEE_ADMIN, OPS\n\n")
        f.write("**查询参数:**\n")
        f.write("- `institutionId` (可选): 按机构ID筛选\n")
        f.write("- `reviewerGroupCode` (可选): 按初审分组筛选\n")
        f.write("- `interviewGroupCode` (可选): 按终审分组筛选\n")
        f.write("- `expertBackground` (可选): 按专家背景筛选\n\n")
        f.write("**示例:**\n")
        f.write("```bash\n")
        f.write("# 获取所有评委\n")
        f.write("curl -H 'Authorization: Bearer <token>' http://localhost:6031/api/admin/reviewers\n\n")
        f.write("# 按管理背景筛选\n")
        f.write("curl -H 'Authorization: Bearer <token>' 'http://localhost:6031/api/admin/reviewers?expertBackground=管理'\n")
        f.write("```\n")
    
    print("\n\n报告已保存到: 评委数据报告.md")
    print("="*80)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
