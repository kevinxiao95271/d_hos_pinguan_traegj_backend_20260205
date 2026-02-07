#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全删除机构ID=27 - 使用禁用外键检查的方式
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
    """删除机构ID=27"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        print("=" * 100)
        print("步骤1: 查看机构ID=27的信息")
        print("=" * 100)
        cursor.execute("SELECT id, name, credit_code FROM institutions WHERE id = 27")
        inst = cursor.fetchone()
        if inst:
            print(f"找到机构: ID={inst['id']}, Name={inst['name']}, CreditCode={inst['credit_code']}")
        else:
            print("机构ID=27不存在，无需删除")
            return
        
        print("\n" + "=" * 100)
        print("步骤2: 禁用外键检查")
        print("=" * 100)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        print("✅ 外键检查已禁用")
        
        print("\n" + "=" * 100)
        print("步骤3: 删除机构ID=27的数据")
        print("=" * 100)
        
        # 直接删除机构
        cursor.execute("DELETE FROM institutions WHERE id = 27")
        print(f"✅ 删除institutions: {cursor.rowcount} 条")
        
        # 删除用户
        cursor.execute("DELETE FROM user_accounts WHERE institution_id = 27")
        print(f"✅ 删除user_accounts: {cursor.rowcount} 条")
        
        # 删除报名及相关数据
        cursor.execute("DELETE FROM team_members WHERE registration_id IN (SELECT id FROM registrations WHERE institution_id = 27)")
        print(f"✅ 删除team_members: {cursor.rowcount} 条")
        
        cursor.execute("DELETE FROM project_summaries WHERE registration_id IN (SELECT id FROM registrations WHERE institution_id = 27)")
        print(f"✅ 删除project_summaries: {cursor.rowcount} 条")
        
        cursor.execute("DELETE FROM activity_infos WHERE registration_id IN (SELECT id FROM registrations WHERE institution_id = 27)")
        print(f"✅ 删除activity_infos: {cursor.rowcount} 条")
        
        cursor.execute("DELETE FROM review_feedbacks WHERE registration_id IN (SELECT id FROM registrations WHERE institution_id = 27)")
        print(f"✅ 删除review_feedbacks: {cursor.rowcount} 条")
        
        cursor.execute("DELETE FROM review_tasks WHERE registration_id IN (SELECT id FROM registrations WHERE institution_id = 27)")
        print(f"✅ 删除review_tasks: {cursor.rowcount} 条")
        
        cursor.execute("DELETE FROM registrations WHERE institution_id = 27")
        print(f"✅ 删除registrations: {cursor.rowcount} 条")
        
        print("\n" + "=" * 100)
        print("步骤4: 启用外键检查")
        print("=" * 100)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("✅ 外键检查已启用")
        
        print("\n" + "=" * 100)
        print("步骤5: 提交事务")
        print("=" * 100)
        conn.commit()
        print("✅ 事务已提交")
        
        print("\n" + "=" * 100)
        print("步骤6: 验证结果")
        print("=" * 100)
        cursor.execute("SELECT id, name FROM institutions WHERE name LIKE '%舟山%'")
        remaining = cursor.fetchall()
        print(f"剩余舟山医院记录: {len(remaining)} 个")
        for r in remaining:
            print(f"  ID={r['id']}, Name={r['name']}")
        
        print("\n" + "=" * 100)
        print("✅ 删除完成！")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print("事务已回滚")
        # 确保恢复外键检查
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("外键检查已恢复")
        except:
            pass
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    delete_institution_27()
