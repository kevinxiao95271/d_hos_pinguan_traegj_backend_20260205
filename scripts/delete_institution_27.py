#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除机构ID=27（重复的舟山医院）及其所有关联数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

DB_CONFIG = {
    'host': '1.94.176.95',
    'user': 'wjx',
    'password': 'kevinxiao',
    'database': 'pinguan_db',
    'charset': 'utf8mb4',
    'port': 3306
}

def delete_institution_27():
    """删除机构ID=27及其所有关联数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        print("=" * 100)
        print("开始删除机构ID=27（舟山医院）及其所有关联数据")
        print("=" * 100)
        
        # 1. 查看要删除的机构信息
        print("\n1. 查看机构信息：")
        cursor.execute("SELECT id, name, credit_code FROM institutions WHERE id = 27")
        inst = cursor.fetchone()
        if inst:
            print(f"   ID={inst['id']}, Name={inst['name']}, CreditCode={inst['credit_code']}")
        else:
            print("   机构ID=27不存在")
            return
        
        # 2. 获取该机构的报名ID列表
        print("\n2. 查找关联的报名记录：")
        cursor.execute("SELECT id, project_name FROM registrations WHERE institution_id = 27")
        registrations = cursor.fetchall()
        print(f"   找到 {len(registrations)} 个报名项目")
        
        if registrations:
            reg_ids = [r['id'] for r in registrations]
            reg_ids_str = ','.join(map(str, reg_ids))
            
            # 3. 删除报名相关的子表数据（按顺序）
            print("\n3. 删除报名相关数据：")
            
            # 删除团队成员
            cursor.execute(f"DELETE FROM team_members WHERE registration_id IN ({reg_ids_str})")
            print(f"   ✅ 删除team_members: {cursor.rowcount} 条")
            
            # 删除项目总结
            cursor.execute(f"DELETE FROM project_summaries WHERE registration_id IN ({reg_ids_str})")
            print(f"   ✅ 删除project_summaries: {cursor.rowcount} 条")
            
            # 删除活动信息
            cursor.execute(f"DELETE FROM activity_infos WHERE registration_id IN ({reg_ids_str})")
            print(f"   ✅ 删除activity_infos: {cursor.rowcount} 条")
            
            # 删除评审反馈
            cursor.execute(f"DELETE FROM review_feedbacks WHERE registration_id IN ({reg_ids_str})")
            print(f"   ✅ 删除review_feedbacks: {cursor.rowcount} 条")
            
            # 删除评审任务
            cursor.execute(f"DELETE FROM review_tasks WHERE registration_id IN ({reg_ids_str})")
            print(f"   ✅ 删除review_tasks: {cursor.rowcount} 条")
            
            # 删除报名记录
            cursor.execute("DELETE FROM registrations WHERE institution_id = 27")
            print(f"   ✅ 删除registrations: {cursor.rowcount} 条")
        
        # 4. 删除该机构的用户
        print("\n4. 删除用户账号：")
        cursor.execute("DELETE FROM user_accounts WHERE institution_id = 27")
        print(f"   ✅ 删除user_accounts: {cursor.rowcount} 条")
        
        # 5. 删除机构本身
        print("\n5. 删除机构记录：")
        cursor.execute("DELETE FROM institutions WHERE id = 27")
        print(f"   ✅ 删除institutions: {cursor.rowcount} 条")
        
        # 提交事务
        conn.commit()
        print("\n" + "=" * 100)
        print("✅ 所有数据删除完成，事务已提交")
        print("=" * 100)
        
        # 6. 验证结果
        print("\n6. 验证剩余的舟山医院记录：")
        cursor.execute("SELECT id, name, credit_code FROM institutions WHERE name LIKE '%舟山%'")
        remaining = cursor.fetchall()
        print(f"   剩余 {len(remaining)} 个舟山医院记录：")
        for r in remaining:
            print(f"     ID={r['id']}, Name={r['name']}, CreditCode={r['credit_code']}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print("事务已回滚")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    delete_institution_27()
