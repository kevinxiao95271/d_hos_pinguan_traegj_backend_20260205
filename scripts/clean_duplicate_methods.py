#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复的品管工具字典数据
保留新code格式，删除旧的method_X格式
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

def clean_duplicates():
    """清理重复数据"""
    
    print("=" * 80)
    print("清理重复的品管工具字典数据")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 查询要删除的旧数据
        print("\n[1] 查询要删除的旧数据 (method_X格式)")
        cur.execute("""
            SELECT id, code, label
            FROM dictionary_items
            WHERE type = 'method' AND code LIKE 'method_%'
            ORDER BY id
        """)
        
        old_methods = cur.fetchall()
        print(f"    找到 {len(old_methods)} 条旧数据:")
        for id, code, label in old_methods:
            print(f"      ID:{id:3d} | {code:20s} | {label}")
        
        # 2. 查询要保留的新数据
        print("\n[2] 查询要保留的新数据 (新code格式)")
        cur.execute("""
            SELECT id, code, label
            FROM dictionary_items
            WHERE type = 'method' AND code NOT LIKE 'method_%'
            ORDER BY id
        """)
        
        new_methods = cur.fetchall()
        print(f"    找到 {len(new_methods)} 条新数据:")
        for id, code, label in new_methods:
            print(f"      ID:{id:3d} | {code:20s} | {label}")
        
        # 3. 检查是否有项目使用了旧的method code
        print("\n[3] 检查是否有项目使用旧code")
        old_codes = [code for _, code, _ in old_methods]
        
        if old_codes:
            placeholders = ', '.join(['%s'] * len(old_codes))
            cur.execute(f"""
                SELECT method_code, COUNT(*) as count
                FROM activity_infos
                WHERE method_code IN ({placeholders})
                GROUP BY method_code
                ORDER BY method_code
            """, old_codes)
            
            usage = cur.fetchall()
            
            if usage:
                print(f"    ⚠ 发现 {len(usage)} 个旧code被使用:")
                for code, count in usage:
                    print(f"      {code}: {count} 个项目")
                print(f"    需要先更新这些项目的method_code")
                
                # 创建新旧code映射
                code_mapping = {
                    'method_1': 'qc_problem',
                    'method_2': 'qc_topic',
                    'method_3': 'project_improve',
                    'method_4': 'balanced_scorecard',
                    'method_5': 'root_cause',
                    'method_6': 'fmea',
                    'method_7': 'benchmark',
                    'method_8': '5s',
                    'method_9': 'qfd',
                    'method_10': 'quality_report',
                    'method_11': 'six_sigma',
                    'method_12': 'ebm',
                    'method_13': 'pdca',
                    'method_14': 'trm',
                    'method_15': 'process_improve',
                    'method_16': 'other',
                    'method_17': 'uncategorized'
                }
                
                print(f"\n    更新项目的method_code...")
                for old_code, new_code in code_mapping.items():
                    cur.execute("""
                        UPDATE activity_infos
                        SET method_code = %s
                        WHERE method_code = %s
                    """, (new_code, old_code))
                    
                    if cur.rowcount > 0:
                        print(f"      {old_code} -> {new_code}: 更新了 {cur.rowcount} 个项目")
                
                conn.commit()
            else:
                print(f"    ✓ 没有项目使用旧code")
        
        # 4. 删除旧数据
        print(f"\n[4] 删除旧数据")
        
        if old_methods:
            old_ids = [id for id, _, _ in old_methods]
            placeholders = ', '.join(['%s'] * len(old_ids))
            
            cur.execute(f"""
                DELETE FROM dictionary_items
                WHERE id IN ({placeholders})
            """, old_ids)
            
            deleted_count = cur.rowcount
            conn.commit()
            
            print(f"    ✓ 删除了 {deleted_count} 条旧数据")
        else:
            print(f"    没有需要删除的数据")
        
        # 5. 验证结果
        print(f"\n[5] 验证清理结果")
        cur.execute("""
            SELECT label, COUNT(*) as count
            FROM dictionary_items
            WHERE type = 'method'
            GROUP BY label
            HAVING COUNT(*) > 1
        """)
        
        remaining_dups = cur.fetchall()
        
        if remaining_dups:
            print(f"    ✗ 仍有 {len(remaining_dups)} 个重复的label:")
            for label, count in remaining_dups:
                print(f"      {label}: {count} 次")
        else:
            print(f"    ✓ 没有重复的label了")
        
        # 6. 显示最终结果
        print(f"\n[6] 最终的品管工具列表")
        cur.execute("""
            SELECT id, code, label
            FROM dictionary_items
            WHERE type = 'method'
            ORDER BY id
        """)
        
        final_methods = cur.fetchall()
        print(f"    共 {len(final_methods)} 个品管工具:")
        for id, code, label in final_methods:
            print(f"      ID:{id:3d} | {code:20s} | {label}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("清理完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 清理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_duplicates()
