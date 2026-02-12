#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看user_accounts表结构和评委数据
"""

import sys
import io
import psycopg2

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'user': 'postgres',
    'password': 'zjylzl',
    'database': 'd_hos_pinguan_20260211'
}

def check_structure():
    """查看表结构和数据"""
    
    print("=" * 80)
    print("user_accounts表结构和评委数据")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 查看表结构
        print("\n[1] user_accounts表结构:")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'user_accounts'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col_name, data_type, max_len, nullable in columns:
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            len_str = f"({max_len})" if max_len else ""
            print(f"  {col_name:25s} {data_type}{len_str:15s} {nullable_str}")
        
        # 2. 查询评委角色的用户
        print("\n[2] 评委(REVIEWER)角色的用户数据:")
        cur.execute("""
            SELECT 
                id, phone, name, title, role, 
                institution_id, reviewer_group_code, 
                interview_group_code, expert_background
            FROM user_accounts
            WHERE role = 'REVIEWER'
            ORDER BY id
            LIMIT 5
        """)
        
        reviewers = cur.fetchall()
        print(f"  找到 {len(reviewers)} 个评委 (显示前5个):")
        
        if reviewers:
            for id, phone, name, title, role, inst_id, rev_group, int_group, expert_bg in reviewers:
                print(f"\n    ID: {id}")
                print(f"      手机号: {phone}")
                print(f"      姓名: {name}")
                print(f"      职称: {title}")
                print(f"      角色: {role}")
                print(f"      机构ID: {inst_id}")
                print(f"      书审分组: {rev_group}")
                print(f"      面谈分组: {int_group}")
                print(f"      专家背景: {expert_bg}")
        else:
            print("  没有评委数据")
        
        # 3. 统计各角色用户数
        print("\n[3] 用户角色统计:")
        cur.execute("""
            SELECT role, COUNT(*) as count
            FROM user_accounts
            GROUP BY role
            ORDER BY role
        """)
        
        role_stats = cur.fetchall()
        for role, count in role_stats:
            print(f"  {role}: {count} 个")
        
        # 4. 检查字段是否存在
        print("\n[4] 字段存在性检查:")
        expected_fields = [
            'phone', 'name', 'title', 'institution_id',
            'reviewer_group_code', 'interview_group_code', 'expert_background'
        ]
        
        actual_fields = [col[0] for col in columns]
        
        for field in expected_fields:
            if field in actual_fields:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} (不存在)")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_structure()
