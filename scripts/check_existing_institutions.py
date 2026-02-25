#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中现有的机构数据
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

def check_existing_institutions():
    """检查现有机构数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 100)
    print("检查数据库中现有的机构数据")
    print("=" * 100)
    
    # 查看表结构
    print("\n1. institutions 表结构:")
    cursor.execute("DESCRIBE institutions")
    columns = cursor.fetchall()
    for col in columns:
        field, type_, null, key, default, extra = col
        print(f"  - {field}: {type_} ({null}) {key} {extra}")
    
    # 统计总数
    cursor.execute("SELECT COUNT(*) FROM institutions")
    total = cursor.fetchone()[0]
    print(f"\n2. 总记录数: {total}")
    
    if total > 0:
        # 查看示例数据
        print(f"\n3. 前10条记录:")
        cursor.execute("SELECT id, name, code, uscc, region, level FROM institutions LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            id_, name, code, uscc, region, level = row
            print(f"  ID={id_}, 名称={name}, 代码={code}, USCC={uscc}, 地区={region}, 等级={level}")
        
        # 统计地区分布
        cursor.execute("""
            SELECT region, COUNT(*) as cnt 
            FROM institutions 
            WHERE region IS NOT NULL 
            GROUP BY region 
            ORDER BY cnt DESC 
            LIMIT 20
        """)
        regions = cursor.fetchall()
        print(f"\n4. 地区分布（前20）:")
        for region, cnt in regions:
            print(f"  {region}: {cnt}")
        
        # 统计等级分布
        cursor.execute("""
            SELECT level, COUNT(*) as cnt 
            FROM institutions 
            WHERE level IS NOT NULL 
            GROUP BY level 
            ORDER BY cnt DESC
        """)
        levels = cursor.fetchall()
        print(f"\n5. 等级分布:")
        for level, cnt in levels:
            print(f"  {level}: {cnt}")
        
        # 检查重复的USCC
        cursor.execute("""
            SELECT uscc, COUNT(*) as cnt 
            FROM institutions 
            GROUP BY uscc 
            HAVING cnt > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\n6. 重复的USCC:")
            for uscc, cnt in duplicates:
                print(f"  {uscc}: {cnt}条")
        else:
            print(f"\n6. 没有重复的USCC")
        
        # 检查空值
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) as null_name,
                SUM(CASE WHEN code IS NULL THEN 1 ELSE 0 END) as null_code,
                SUM(CASE WHEN uscc IS NULL THEN 1 ELSE 0 END) as null_uscc,
                SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END) as null_region,
                SUM(CASE WHEN level IS NULL THEN 1 ELSE 0 END) as null_level
            FROM institutions
        """)
        null_counts = cursor.fetchone()
        print(f"\n7. 空值统计:")
        print(f"  name: {null_counts[0]}")
        print(f"  code: {null_counts[1]}")
        print(f"  uscc: {null_counts[2]}")
        print(f"  region: {null_counts[3]}")
        print(f"  level: {null_counts[4]}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_existing_institutions()
