#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动修复使用乱码quality_topic code的记录 - 随机分配正确的code"""

import pymysql
import random

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def auto_fix():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("自动修复使用乱码quality_topic code的记录")
        print("=" * 80)
        
        bad_codes = [
            'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
            'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
            'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
            'quality_topic_10', 'quality_topic_11'
        ]
        
        # 获取所有正确的code
        print("\n1. 获取正确的quality_topic code列表...")
        cursor.execute("""
            SELECT code, label
            FROM dictionary_items
            WHERE type = 'quality_topic' AND active = TRUE AND code NOT LIKE 'quality_topic_%'
            ORDER BY id
        """)
        
        valid_codes = cursor.fetchall()
        print(f"   找到 {len(valid_codes)} 个正确的code:")
        for code, label in valid_codes[:5]:
            print(f"     - {code}: {label}")
        print(f"     ... (还有 {len(valid_codes) - 5} 个)")
        
        # 2. 检查受影响的记录
        print("\n2. 检查受影响的记录...")
        placeholders = ','.join(['%s'] * len(bad_codes))
        sql = f"""
        SELECT ai.id, ai.quality_topic_code, r.project_name
        FROM activity_infos ai
        JOIN registrations r ON ai.registration_id = r.id
        WHERE ai.quality_topic_code IN ({placeholders})
        ORDER BY ai.id
        """
        
        cursor.execute(sql, bad_codes)
        bad_records = cursor.fetchall()
        
        if not bad_records:
            print("   ✅ 没有需要修复的记录")
            return
        
        print(f"   找到 {len(bad_records)} 条需要修复的记录")
        
        # 3. 显示修复计划
        print("\n3. 修复计划:")
        print("   将随机分配正确的code给这些记录，用于测试不同的Label显示")
        print("")
        
        # 4. 执行更新
        print("4. 执行更新...")
        updated_count = 0
        
        for record_id, old_code, project_name in bad_records:
            # 随机选择一个正确的code
            new_code, new_label = random.choice(valid_codes)
            
            sql = """
            UPDATE activity_infos
            SET quality_topic_code = %s
            WHERE id = %s
            """
            
            cursor.execute(sql, (new_code, record_id))
            updated_count += 1
            
            print(f"   ✅ ID {record_id}: {old_code} → {new_code} ({new_label})")
        
        conn.commit()
        print(f"\n   共更新 {updated_count} 条记录")
        
        # 5. 验证更新结果
        print("\n5. 验证更新结果...")
        sql = f"""
        SELECT COUNT(*) as count
        FROM activity_infos
        WHERE quality_topic_code IN ({placeholders})
        """
        
        cursor.execute(sql, bad_codes)
        remaining = cursor.fetchone()[0]
        
        if remaining == 0:
            print("   ✅ 所有乱码code已更新")
        else:
            print(f"   ⚠️  还有 {remaining} 条记录未更新")
        
        # 6. 显示更新后的分布
        print("\n6. 更新后的code分布...")
        cursor.execute("""
            SELECT quality_topic_code, COUNT(*) as count
            FROM activity_infos
            WHERE quality_topic_code IS NOT NULL
            GROUP BY quality_topic_code
            ORDER BY count DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        print("   Top 10 使用最多的code:")
        for code, count in results:
            # 获取label
            cursor.execute("""
                SELECT label FROM dictionary_items
                WHERE type = 'quality_topic' AND code = %s
            """, (code,))
            label_result = cursor.fetchone()
            label = label_result[0] if label_result else '未知'
            print(f"     - {code}: {count} 条 ({label})")
        
        print("\n" + "=" * 80)
        print("✅ 修复完成！")
        print("=" * 80)
        print("\n现在所有记录都使用正确的code，API会返回正确的中文Label")
        print("前端可以看到各种不同的医疗质量相关主题")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    auto_fix()
