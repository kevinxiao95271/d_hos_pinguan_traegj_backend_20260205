#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动修复使用了不存在code的experience_improve记录"""

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

# 有效的code列表（排除测试数据）
VALID_CODES = [
    'appointment',
    'outpatient_process',
    'inpatient_experience',
    'post_discharge',
    'pre_in_out',
    'environment',
    'internet_med',
    'other',
    'appointment_service',
    'post_hospital_service',
    'pre_inpatient_connection',
    'comfortable_environment',
    'internet_diagnosis'
]

def fix_bad_codes():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查找使用了不存在code的记录
        bad_codes = ['experience_1', 'experience_2', 'experience_3']
        
        print("=" * 80)
        print("修复 experience_improve 不存在的code")
        print("=" * 80)
        
        for bad_code in bad_codes:
            cursor.execute("""
                SELECT id, experience_improve_code
                FROM activity_infos
                WHERE experience_improve_code = %s
            """, (bad_code,))
            
            records = cursor.fetchall()
            
            if records:
                print(f"\n找到 {len(records)} 条使用 {bad_code} 的记录")
                
                for record_id, old_code in records:
                    # 随机选择一个有效的code
                    new_code = random.choice(VALID_CODES)
                    
                    # 更新记录
                    cursor.execute("""
                        UPDATE activity_infos
                        SET experience_improve_code = %s
                        WHERE id = %s
                    """, (new_code, record_id))
                    
                    print(f"  ✅ ID {record_id}: {old_code} → {new_code}")
                
                conn.commit()
            else:
                print(f"\n没有找到使用 {bad_code} 的记录")
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fix_bad_codes()
