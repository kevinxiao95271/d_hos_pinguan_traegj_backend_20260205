#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查品管工具字典数据重复
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

def check_duplicates():
    """检查品管工具重复"""
    
    print("=" * 80)
    print("检查品管工具字典数据重复")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. 查询所有method类型的字典项
        print("\n[1] 查询所有品管工具 (type='method')")
        cur.execute("""
            SELECT id, code, label, type, active
            FROM dictionary_items
            WHERE type = 'method'
            ORDER BY id
        """)
        
        methods = cur.fetchall()
        print(f"    找到 {len(methods)} 条记录:")
        
        for id, code, label, type, active in methods:
            active_str = "✓" if active else "✗"
            print(f"      ID:{id:3d} | code:{code:20s} | label:{label:30s} | active:{active_str}")
        
        # 2. 检查label重复
        print("\n[2] 检查label重复情况")
        cur.execute("""
            SELECT label, COUNT(*) as count, array_agg(code) as codes, array_agg(id) as ids
            FROM dictionary_items
            WHERE type = 'method'
            GROUP BY label
            HAVING COUNT(*) > 1
            ORDER BY label
        """)
        
        duplicates = cur.fetchall()
        
        if duplicates:
            print(f"    发现 {len(duplicates)} 个重复的label:")
            for label, count, codes, ids in duplicates:
                print(f"      '{label}' 出现 {count} 次")
                print(f"        codes: {codes}")
                print(f"        ids: {ids}")
        else:
            print(f"    ✓ 没有重复的label")
        
        # 3. 检查code重复
        print("\n[3] 检查code重复情况")
        cur.execute("""
            SELECT code, COUNT(*) as count, array_agg(label) as labels, array_agg(id) as ids
            FROM dictionary_items
            WHERE type = 'method'
            GROUP BY code
            HAVING COUNT(*) > 1
            ORDER BY code
        """)
        
        code_duplicates = cur.fetchall()
        
        if code_duplicates:
            print(f"    发现 {len(code_duplicates)} 个重复的code:")
            for code, count, labels, ids in code_duplicates:
                print(f"      '{code}' 出现 {count} 次")
                print(f"        labels: {labels}")
                print(f"        ids: {ids}")
        else:
            print(f"    ✓ 没有重复的code")
        
        # 4. 分析重复原因
        print("\n[4] 分析重复数据")
        
        if duplicates:
            print("    重复原因分析:")
            print("    - 可能是数据迁移时重复导入")
            print("    - 或者是历史数据中就存在重复")
            
            # 检查是否有新旧code的对应关系
            old_new_pairs = [
                ('method_1', 'qc_problem'),
                ('method_2', 'qc_topic')
            ]
            
            print("\n    检查新旧code对应关系:")
            for old_code, new_code in old_new_pairs:
                cur.execute("""
                    SELECT id, code, label
                    FROM dictionary_items
                    WHERE type = 'method' AND code IN (%s, %s)
                    ORDER BY code
                """, (old_code, new_code))
                
                pairs = cur.fetchall()
                if len(pairs) == 2:
                    print(f"      {old_code} <-> {new_code}:")
                    for id, code, label in pairs:
                        print(f"        ID:{id} | {code} | {label}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_duplicates()
