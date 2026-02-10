#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行分值字段更新SQL"""

import pymysql
from db_config import DB_CONFIG

def execute_update():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("开始修改数据库字段...")
        
        # 执行ALTER TABLE
        cursor.execute("""
            ALTER TABLE review_scores 
              MODIFY COLUMN plan DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN problem DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN action DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN success DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN review DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN operation DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN presentation DECIMAL(4,1) NOT NULL,
              MODIFY COLUMN total DECIMAL(5,1) NOT NULL
        """)
        conn.commit()
        print("✅ 字段修改成功")
        
        # 验证修改结果
        cursor.execute("DESCRIBE review_scores")
        print("\n字段类型验证:")
        for row in cursor.fetchall():
            if row[0] in ['plan', 'problem', 'action', 'success', 'review', 'operation', 'presentation', 'total']:
                print(f"  {row[0]}: {row[1]}")
        
        # 查看数据
        cursor.execute("SELECT COUNT(*) FROM review_scores")
        count = cursor.fetchone()[0]
        print(f"\n现有评分记录数: {count}")
        
        if count > 0:
            cursor.execute("SELECT plan, problem, action, total FROM review_scores LIMIT 3")
            print("\n数据示例:")
            for row in cursor.fetchall():
                print(f"  plan={row[0]}, problem={row[1]}, action={row[2]}, total={row[3]}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    execute_update()
