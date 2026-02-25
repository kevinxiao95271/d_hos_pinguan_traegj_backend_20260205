#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为institutions表添加索引以提升搜索性能
"""
import pymysql
import time

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_index_exists(cursor, table_name, index_name):
    """检查索引是否存在"""
    cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}'")
    return cursor.fetchone() is not None

def add_index(cursor, table_name, index_name, column, index_type='INDEX'):
    """添加索引"""
    if check_index_exists(cursor, table_name, index_name):
        print(f"  [SKIP] {index_name} 已存在")
        return False
    
    print(f"  [ADD] 正在创建 {index_name}...")
    start = time.time()
    
    try:
        if isinstance(column, list):
            columns_str = ', '.join(column)
            sql = f"CREATE {index_type} {index_name} ON {table_name}({columns_str})"
        else:
            sql = f"CREATE {index_type} {index_name} ON {table_name}({column})"
        
        cursor.execute(sql)
        elapsed = time.time() - start
        print(f"  [OK] {index_name} 创建成功 ({elapsed:.2f}s)")
        return True
    except Exception as e:
        print(f"  [ERROR] {index_name} 创建失败: {e}")
        return False

def main():
    print("=" * 80)
    print("为 institutions 表添加性能优化索引")
    print("=" * 80)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查看现有索引
        print("\n1. 现有索引:")
        cursor.execute("SHOW INDEX FROM institutions")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"  - {idx[2]}: {idx[4]} ({idx[10]})")
        
        # 添加新索引
        print("\n2. 添加性能优化索引:")
        
        indexes_to_add = [
            ('idx_name', 'name', 'INDEX'),
            ('idx_region', 'region', 'INDEX'),
            ('idx_level', 'level', 'INDEX'),
            ('idx_region_name', ['region', 'name'], 'INDEX'),
        ]
        
        added_count = 0
        for index_name, column, index_type in indexes_to_add:
            if add_index(cursor, 'institutions', index_name, column, index_type):
                added_count += 1
                conn.commit()
        
        print(f"\n3. 索引添加完成:")
        print(f"  - 新增: {added_count} 个")
        print(f"  - 跳过: {len(indexes_to_add) - added_count} 个")
        
        # 分析表
        print("\n4. 分析表（优化查询计划）...")
        cursor.execute("ANALYZE TABLE institutions")
        print("  [OK] 分析完成")
        
        # 查看最终索引
        print("\n5. 最终索引列表:")
        cursor.execute("SHOW INDEX FROM institutions")
        final_indexes = cursor.fetchall()
        for idx in final_indexes:
            print(f"  - {idx[2]}: {idx[4]} (Cardinality: {idx[6]})")
        
        # 测试查询性能
        print("\n6. 测试查询性能:")
        
        # 测试1: 按名称搜索
        start = time.time()
        cursor.execute("SELECT * FROM institutions WHERE name LIKE '%人民医院%' LIMIT 20")
        elapsed1 = (time.time() - start) * 1000
        count1 = len(cursor.fetchall())
        print(f"  - 按名称搜索: {elapsed1:.0f}ms, {count1}条结果")
        
        # 测试2: 按地区搜索
        start = time.time()
        cursor.execute("SELECT * FROM institutions WHERE region = '杭州市' LIMIT 20")
        elapsed2 = (time.time() - start) * 1000
        count2 = len(cursor.fetchall())
        print(f"  - 按地区搜索: {elapsed2:.0f}ms, {count2}条结果")
        
        # 测试3: 组合搜索
        start = time.time()
        cursor.execute("SELECT * FROM institutions WHERE region = '杭州市' AND name LIKE '%人民%' LIMIT 20")
        elapsed3 = (time.time() - start) * 1000
        count3 = len(cursor.fetchall())
        print(f"  - 组合搜索: {elapsed3:.0f}ms, {count3}条结果")
        
        print("\n" + "=" * 80)
        print("索引优化完成！")
        print("=" * 80)
        print("\n建议:")
        print("  1. 重启Spring Boot服务以应用索引优化")
        print("  2. 运行性能测试: python scripts/test_institution_search_performance.py")
        print("  3. 监控生产环境的查询性能")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
