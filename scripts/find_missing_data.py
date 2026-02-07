#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""找出缺少品管工具和主题类型的项目"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import mysql.connector

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def find_missing():
    """查找缺失数据的项目"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 120)
    print("查找舟山医院缺失品管工具/主题类型的项目")
    print("=" * 120)
    print()
    
    # 查询舟山医院的所有项目
    cursor.execute("""
        SELECT 
            r.id,
            r.project_name,
            r.group_code,
            u.name as applicant_name,
            u.phone,
            ai.method_code,
            ai.subject_type_code,
            ai.theme,
            ai.keywords
        FROM registrations r
        INNER JOIN user_accounts u ON r.applicant_id = u.id
        LEFT JOIN activity_infos ai ON ai.registration_id = r.id
        WHERE r.institution_id = 17
        AND r.competition_id = 21
        ORDER BY r.id
    """)
    
    rows = cursor.fetchall()
    
    print(f"舟山医院共有 {len(rows)} 个项目\n")
    
    missing_method = []
    missing_subject = []
    missing_both = []
    complete = []
    
    for row in rows:
        reg_id, project_name, group_code, applicant, phone, method, subject, theme, keywords = row
        
        has_method = method is not None and method.strip() != ''
        has_subject = subject is not None and subject.strip() != ''
        
        if not has_method and not has_subject:
            missing_both.append({
                'id': reg_id,
                'name': project_name,
                'applicant': applicant,
                'phone': phone,
                'group': group_code
            })
        elif not has_method:
            missing_method.append({
                'id': reg_id,
                'name': project_name,
                'applicant': applicant,
                'phone': phone,
                'group': group_code,
                'subject': subject
            })
        elif not has_subject:
            missing_subject.append({
                'id': reg_id,
                'name': project_name,
                'applicant': applicant,
                'phone': phone,
                'group': group_code,
                'method': method
            })
        else:
            complete.append({
                'id': reg_id,
                'name': project_name,
                'method': method,
                'subject': subject
            })
    
    print(f"📊 统计结果：")
    print(f"   ✅ 数据完整: {len(complete)} 个")
    print(f"   ❌ 缺少品管工具和主题类型: {len(missing_both)} 个")
    print(f"   ⚠️  仅缺少品管工具: {len(missing_method)} 个")
    print(f"   ⚠️  仅缺少主题类型: {len(missing_subject)} 个")
    print()
    
    if missing_both:
        print("=" * 120)
        print(f"❌ 以下 {len(missing_both)} 个项目缺少品管工具和主题类型（需要补充）：")
        print("=" * 120)
        for p in missing_both:
            print(f"  项目ID: {p['id']} | 分组: {p['group']} | 申请人: {p['applicant']} ({p['phone']})")
            print(f"  项目名称: {p['name']}")
            print()
    
    if missing_method:
        print("=" * 120)
        print(f"⚠️  以下 {len(missing_method)} 个项目仅缺少品管工具：")
        print("=" * 120)
        for p in missing_method:
            print(f"  项目ID: {p['id']} | 分组: {p['group']} | 主题类型: {p['subject']}")
            print(f"  项目名称: {p['name'][:60]}...")
            print()
    
    if missing_subject:
        print("=" * 120)
        print(f"⚠️  以下 {len(missing_subject)} 个项目仅缺少主题类型：")
        print("=" * 120)
        for p in missing_subject:
            print(f"  项目ID: {p['id']} | 分组: {p['group']} | 品管工具: {p['method']}")
            print(f"  项目名称: {p['name'][:60]}...")
            print()
    
    # 导出缺失数据的项目ID列表
    all_missing_ids = [p['id'] for p in missing_both] + [p['id'] for p in missing_method] + [p['id'] for p in missing_subject]
    
    if all_missing_ids:
        print("=" * 120)
        print(f"需要补充数据的项目ID列表（共 {len(all_missing_ids)} 个）：")
        print(', '.join(map(str, sorted(all_missing_ids))))
        print("=" * 120)
    
    cursor.close()
    conn.close()
    
    return all_missing_ids

if __name__ == "__main__":
    find_missing()
