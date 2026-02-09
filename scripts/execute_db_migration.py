#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行数据库迁移"""

import pymysql
from db_config import DB_CONFIG

# 腾讯云MySQL连接信息
# DB_CONFIG imported from db_config.py

def execute_migration():
    """执行数据库迁移"""
    print("=" * 80)
    print("步骤1: 执行数据库迁移")
    print("=" * 80)
    
    try:
        # 连接数据库
        print("\n1. 连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查字段是否已存在
        print("\n2. 检查字段是否已存在...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'd_hos_pinguan_traegj_20260205' 
            AND TABLE_NAME = 'activity_infos' 
            AND COLUMN_NAME = 'related_to_digital_ai'
        """)
        
        if cursor.fetchone():
            print("⚠️  related_to_digital_ai 字段已存在，跳过添加")
        else:
            print("📝 related_to_digital_ai 字段不存在，开始添加...")
            
            # 添加字段
            sql = """
                ALTER TABLE activity_infos 
                ADD COLUMN related_to_digital_ai BOOLEAN NOT NULL DEFAULT FALSE 
                COMMENT '是否与数字化/人工智能应用相关主题' 
                AFTER cross_department
            """
            cursor.execute(sql)
            conn.commit()
            print("✅ related_to_digital_ai 字段添加成功")
        
        # 检查 project_summaries 表的字段
        print("\n3. 检查 project_summaries 表字段...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'd_hos_pinguan_traegj_20260205' 
            AND TABLE_NAME = 'project_summaries' 
            AND COLUMN_NAME IN ('operation', 'presentation')
        """)
        
        existing_fields = [row[0] for row in cursor.fetchall()]
        
        if 'operation' not in existing_fields:
            print("📝 添加 operation 字段...")
            cursor.execute("""
                ALTER TABLE project_summaries 
                ADD COLUMN operation VARCHAR(1000) NULL COMMENT '运作' 
                AFTER discussion
            """)
            conn.commit()
            print("✅ operation 字段添加成功")
        else:
            print("⚠️  operation 字段已存在")
        
        if 'presentation' not in existing_fields:
            print("📝 添加 presentation 字段...")
            cursor.execute("""
                ALTER TABLE project_summaries 
                ADD COLUMN presentation VARCHAR(1000) NULL COMMENT '展示' 
                AFTER operation
            """)
            conn.commit()
            print("✅ presentation 字段添加成功")
        else:
            print("⚠️  presentation 字段已存在")
        
        # 验证字段
        print("\n4. 验证字段...")
        cursor.execute("DESCRIBE activity_infos")
        activity_fields = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("DESCRIBE project_summaries")
        summary_fields = [row[0] for row in cursor.fetchall()]
        
        print("\nactivity_infos 表字段:")
        for field in activity_fields:
            print(f"  - {field}")
        
        print("\nproject_summaries 表字段:")
        for field in summary_fields:
            print(f"  - {field}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 数据库迁移完成！")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {e}")
        return False

if __name__ == "__main__":
    success = execute_migration()
    if success:
        print("\n下一步: 重启应用")
    else:
        print("\n请检查错误信息")
