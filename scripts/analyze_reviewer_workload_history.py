#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析历史数据中评委的评审任务数量
按年份统计平均每个评委的评审任务数
"""

import psycopg2
from collections import defaultdict

# 数据库连接配置
DB_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'd_hos_pinguan_20260211',
    'user': 'postgres',
    'password': 'zjylzl'
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("历史数据表结构分析")
    print("=" * 80)
    
    # 1. 查看表结构
    print("\n[1] pinguan_his_data 表结构:")
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name='pinguan_his_data' 
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    for col in columns:
        print(f"  - {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
    
    # 2. 查看数据总量
    print("\n[2] 数据总量:")
    cur.execute("SELECT COUNT(*) FROM pinguan_his_data")
    total = cur.fetchone()[0]
    print(f"  总记录数: {total}")
    
    # 3. 查看年份分布
    print("\n[3] 年份分布:")
    cur.execute("""
        SELECT year, COUNT(*) as count
        FROM pinguan_his_data
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """)
    years = cur.fetchall()
    for year, count in years:
        print(f"  {year}年: {count}条记录")
    
    # 4. 检查评委相关字段
    print("\n[4] 评委相关字段检查:")
    
    # 检查是否有评委姓名字段
    reviewer_fields = []
    for col in columns:
        col_name = col[0].lower()
        if any(keyword in col_name for keyword in ['reviewer', 'expert', '评委', '专家', 'judge']):
            reviewer_fields.append(col[0])
    
    if reviewer_fields:
        print(f"  找到评委相关字段: {', '.join(reviewer_fields)}")
        
        # 查看这些字段的样本数据
        for field in reviewer_fields:
            cur.execute(f"""
                SELECT {field}, COUNT(*) as count
                FROM pinguan_his_data
                WHERE {field} IS NOT NULL AND {field} != ''
                GROUP BY {field}
                ORDER BY count DESC
                LIMIT 5
            """)
            samples = cur.fetchall()
            if samples:
                print(f"\n  {field} 样本数据（前5）:")
                for val, count in samples:
                    print(f"    - {val}: {count}条")
    else:
        print("  未找到明确的评委字段")
    
    # 5. 查看所有字段的样本数据（前3条）
    print("\n[5] 样本数据（前3条）:")
    cur.execute("SELECT * FROM pinguan_his_data LIMIT 3")
    sample_rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    
    for i, row in enumerate(sample_rows, 1):
        print(f"\n  记录 {i}:")
        for col_name, value in zip(col_names, row):
            if value is not None and str(value).strip():
                print(f"    {col_name}: {value}")
    
    # 6. 尝试分析评审任务数量
    print("\n" + "=" * 80)
    print("评审任务数量分析")
    print("=" * 80)
    
    # 检查是否有评委相关字段可以用来统计
    if reviewer_fields:
        for field in reviewer_fields:
            print(f"\n[按 {field} 统计]")
            
            # 按年份和评委统计
            cur.execute(f"""
                SELECT 
                    year,
                    COUNT(DISTINCT {field}) as reviewer_count,
                    COUNT(*) as total_tasks,
                    ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT {field}), 0), 2) as avg_tasks_per_reviewer
                FROM pinguan_his_data
                WHERE year IS NOT NULL 
                    AND {field} IS NOT NULL 
                    AND {field} != ''
                GROUP BY year
                ORDER BY year
            """)
            
            results = cur.fetchall()
            if results:
                print(f"\n  年份 | 评委数 | 总任务数 | 平均任务/评委")
                print("  " + "-" * 50)
                for year, reviewer_count, total_tasks, avg_tasks in results:
                    print(f"  {year} | {reviewer_count:6d} | {total_tasks:8d} | {avg_tasks:15.2f}")
                
                # 计算总体平均
                total_reviewers = sum(r[1] for r in results)
                total_all_tasks = sum(r[2] for r in results)
                overall_avg = total_all_tasks / total_reviewers if total_reviewers > 0 else 0
                print("  " + "-" * 50)
                print(f"  总计 | {total_reviewers:6d} | {total_all_tasks:8d} | {overall_avg:15.2f}")
            else:
                print(f"  {field} 字段无有效数据")
    else:
        print("\n⚠️  历史数据表中没有找到评委相关字段")
        print("   可能的原因:")
        print("   1. 历史数据只记录了项目信息，没有记录评委信息")
        print("   2. 评委信息在其他表中")
        print("   3. 字段名称不明显，需要进一步确认")
    
    # 7. 检查是否有其他可能包含评委信息的字段
    print("\n[6] 检查所有文本字段（可能包含评委信息）:")
    text_fields = [col[0] for col in columns if col[1] in ('character varying', 'text')]
    
    for field in text_fields[:10]:  # 只检查前10个文本字段
        cur.execute(f"""
            SELECT {field}
            FROM pinguan_his_data
            WHERE {field} IS NOT NULL AND {field} != ''
            LIMIT 1
        """)
        sample = cur.fetchone()
        if sample:
            print(f"  {field}: {sample[0][:100]}...")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
