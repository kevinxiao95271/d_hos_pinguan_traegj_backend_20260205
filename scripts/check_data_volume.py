#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库数据量"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_volume():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("数据库数据量统计")
        print("=" * 80)
        
        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n共 {len(tables)} 个表\n")
        
        total_rows = 0
        table_stats = []
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_rows += count
            
            cursor.execute(f"""
                SELECT 
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                FROM information_schema.TABLES 
                WHERE table_schema = %s AND table_name = %s
            """, (DB_CONFIG['database'], table))
            
            size_result = cursor.fetchone()
            size_mb = size_result[0] if size_result and size_result[0] else 0
            
            table_stats.append((table, count, size_mb))
        
        # 按记录数排序
        table_stats.sort(key=lambda x: x[1], reverse=True)
        
        print(f"{'表名':<40} {'记录数':>10} {'大小(MB)':>12}")
        print("-" * 80)
        
        for table, count, size in table_stats:
            print(f"{table:<40} {count:>10,} {size:>12.2f}")
        
        print("-" * 80)
        print(f"{'总计':<40} {total_rows:>10,}")
        
        # 数据库总大小
        cursor.execute(f"""
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
            FROM information_schema.TABLES 
            WHERE table_schema = %s
        """, (DB_CONFIG['database'],))
        
        total_size = cursor.fetchone()[0]
        print(f"\n数据库总大小: {total_size:.2f} MB")
        
        # 迁移时间估算
        print("\n" + "=" * 80)
        print("迁移时间估算")
        print("=" * 80)
        
        # 假设每秒处理1000条记录
        estimated_seconds = total_rows / 1000
        estimated_minutes = estimated_seconds / 60
        
        print(f"\n使用 pgLoader 工具:")
        print(f"  预计时间: {estimated_minutes:.1f} 分钟")
        print(f"  处理速度: 约1000条/秒")
        
        print(f"\n手动导出导入:")
        print(f"  预计时间: {estimated_minutes * 2:.1f} 分钟")
        print(f"  处理速度: 约500条/秒")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_volume()
