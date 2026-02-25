#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为user_accounts表添加enabled和last_login_at字段
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
    print("数据库迁移：添加用户启用状态和最后登录时间字段")
    print("=" * 80)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 检查enabled字段
        print("\n1. 检查enabled字段...")
        cursor.execute("SHOW COLUMNS FROM user_accounts LIKE 'enabled'")
        result = cursor.fetchone()
        
        if not result:
            print("  [ADD] 正在添加enabled字段...")
            cursor.execute("""
                ALTER TABLE user_accounts 
                ADD COLUMN enabled BOOLEAN NOT NULL DEFAULT TRUE 
                COMMENT '启用状态' 
                AFTER expert_background
            """)
            conn.commit()
            print("  [OK] enabled字段添加成功")
        else:
            print("  [SKIP] enabled字段已存在")
        
        # 2. 检查last_login_at字段
        print("\n2. 检查last_login_at字段...")
        cursor.execute("SHOW COLUMNS FROM user_accounts LIKE 'last_login_at'")
        result = cursor.fetchone()
        
        if not result:
            print("  [ADD] 正在添加last_login_at字段...")
            cursor.execute("""
                ALTER TABLE user_accounts 
                ADD COLUMN last_login_at DATETIME(6) NULL 
                COMMENT '最后登录时间' 
                AFTER created_at
            """)
            conn.commit()
            print("  [OK] last_login_at字段添加成功")
        else:
            print("  [SKIP] last_login_at字段已存在")
        
        # 3. 验证表结构
        print("\n3. 验证表结构...")
        cursor.execute("SHOW COLUMNS FROM user_accounts")
        columns = cursor.fetchall()
        
        print("  user_accounts表结构:")
        for col in columns:
            null_str = 'NULL' if col[2] == 'YES' else 'NOT NULL'
            default = f", Default: {col[4]}" if col[4] else ""
            print(f"    - {col[0]} ({col[1]}) {null_str}{default}")
        
        # 4. 更新现有用户的enabled状态（确保都是启用的）
        print("\n4. 更新现有用户状态...")
        cursor.execute("UPDATE user_accounts SET enabled = TRUE WHERE enabled IS NULL")
        updated = cursor.rowcount
        conn.commit()
        print(f"  [OK] 更新了 {updated} 个用户的启用状态")
        
        # 5. 统计用户数量
        print("\n5. 用户统计...")
        cursor.execute("SELECT COUNT(*) FROM user_accounts")
        total = cursor.fetchone()[0]
        print(f"  总用户数: {total}")
        
        cursor.execute("SELECT role, COUNT(*) FROM user_accounts GROUP BY role")
        role_stats = cursor.fetchall()
        if role_stats:
            print("  按角色统计:")
            for role, count in role_stats:
                print(f"    - {role}: {count}")
        
        print("\n" + "=" * 80)
        print("数据库迁移完成！")
        print("=" * 80)
        
        print("\n功能说明:")
        print("  1. enabled字段：控制用户是否可以登录")
        print("     - TRUE（默认）：用户可以正常登录")
        print("     - FALSE：用户被禁用，无法登录")
        print("  2. last_login_at字段：记录用户最后登录时间")
        print("     - 每次成功登录时自动更新")
        print("     - 用于分析用户活跃度")
        
        print("\n管理员功能:")
        print("  - POST /api/admin/users/query - 查询用户列表")
        print("  - GET /api/admin/users/{id} - 查看用户详情")
        print("  - POST /api/admin/users/reviewers - 创建评委账号")
        print("  - PUT /api/admin/users/{id}/disable - 禁用用户")
        print("  - PUT /api/admin/users/{id}/enable - 启用用户")
        print("  - GET /api/admin/users/statistics - 用户统计")
        
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
