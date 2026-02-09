#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 quality_topic 的乱码Label"""

import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

def fix_quality_topic_labels():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("修复 quality_topic 的乱码Label")
        print("=" * 80)
        
        # 1. 查找所有包含问号的记录
        print("\n1. 查找乱码记录...")
        sql = """
        SELECT id, code, label
        FROM dictionary_items
        WHERE type = 'quality_topic' AND label LIKE '%?%'
        """
        
        cursor.execute(sql)
        bad_records = cursor.fetchall()
        
        print(f"   找到 {len(bad_records)} 条乱码记录:")
        for record in bad_records:
            print(f"   - ID: {record[0]}, Code: {record[1]}, Label: {record[2]}")
        
        if not bad_records:
            print("   ✅ 没有乱码记录")
            return
        
        # 2. 删除这些乱码记录
        print("\n2. 删除乱码记录...")
        for record in bad_records:
            record_id = record[0]
            code = record[1]
            cursor.execute("DELETE FROM dictionary_items WHERE id = %s", (record_id,))
            print(f"   ✅ 删除 ID: {record_id}, Code: {code}")
        
        conn.commit()
        print(f"\n   共删除 {len(bad_records)} 条记录")
        
        # 3. 验证删除结果
        print("\n3. 验证删除结果...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dictionary_items
            WHERE type = 'quality_topic' AND label LIKE '%?%'
        """)
        
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            print("   ✅ 所有乱码记录已删除")
        else:
            print(f"   ⚠️  还有 {remaining} 条乱码记录")
        
        # 4. 显示剩余的正常记录
        print("\n4. 剩余的正常记录...")
        cursor.execute("""
            SELECT code, label
            FROM dictionary_items
            WHERE type = 'quality_topic' AND active = TRUE
            ORDER BY id
        """)
        
        normal_records = cursor.fetchall()
        print(f"   共 {len(normal_records)} 条正常记录:\n")
        
        for i, (code, label) in enumerate(normal_records, 1):
            print(f"   {i:2d}. {code:35s} → {label}")
        
        print("\n" + "=" * 80)
        print("✅ 修复完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fix_quality_topic_labels()
