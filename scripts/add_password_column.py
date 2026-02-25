#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为user_accounts表添加password字段
"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def main():
    print("=" * 80)
    print("数据库迁移：添加password字段到user_accounts表")
    print("=" * 80)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 检查字段是否已存在
        print("\n1. 检查password字段是否存在...")
        cursor.execute("SHOW COLUMNS FROM user_accounts LIKE 'password'")
        result = cursor.fetchone()
        
        if result:
            print("  [SKIP] password字段已存在")
            return
        
        # 2. 添加password字段
        print("\n2. 添加password字段...")
        cursor.execute("""
            ALTER TABLE user_accounts 
            ADD COLUMN password VARCHAR(128) NULL COMMENT '密码(BCrypt加密)' 
            AFTER phone
        """)
        conn.commit()
        print("  [OK] password字段添加成功")
        
        # 3. 验证字段
        print("\n3. 验证字段...")
        cursor.execute("SHOW COLUMNS FROM user_accounts")
        columns = cursor.fetchall()
        
        print("  user_accounts表结构:")
        for col in columns:
            print(f"    - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        # 4. 查询现有用户
        print("\n4. 检查现有用户...")
        cursor.execute("SELECT COUNT(*) FROM user_accounts")
        user_count = cursor.fetchone()[0]
        print(f"  现有用户数: {user_count}")
        
        if user_count > 0:
            print("\n  ⚠️ 重要提示:")
            print("  - 现有用户的password字段为NULL")
            print("  - 这些用户需要重新设置密码才能登录")
            print("  - 或使用旧的 /api/auth/login 接口（不推荐）")
            print("  - 建议通知用户重新注册或重置密码")
        
        print("\n" + "=" * 80)
        print("数据库迁移完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
