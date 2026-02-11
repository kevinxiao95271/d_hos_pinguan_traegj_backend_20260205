#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PostgreSQL迁移 - 步骤2: 导出并迁移数据"""

import pymysql
import psycopg2
from psycopg2.extras import execute_batch
from db_config import DB_CONFIG
import time

# PostgreSQL配置
PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'zjylzl',
    'user': 'postgres',
    'password': 'zjylzl',
    'options': '-c search_path=zjylzl'
}

# 数据类型映射
TYPE_MAPPING = {
    'int': 'INTEGER',
    'bigint': 'BIGINT',
    'tinyint': 'SMALLINT',
    'varchar': 'VARCHAR',
    'text': 'TEXT',
    'datetime': 'TIMESTAMP',
    'decimal': 'NUMERIC',
    'bit': 'BOOLEAN'
}

def convert_mysql_type_to_pg(mysql_type):
    """转换MySQL类型到PostgreSQL"""
    mysql_type_lower = mysql_type.lower()
    
    # 特殊处理bit(1) -> BOOLEAN
    if mysql_type_lower.startswith('bit(1)'):
        return 'BOOLEAN'
    
    # 特殊处理tinyint(1) -> BOOLEAN
    if mysql_type_lower.startswith('tinyint(1)'):
        return 'BOOLEAN'
    
    for mysql_key, pg_type in TYPE_MAPPING.items():
        if mysql_type_lower.startswith(mysql_key):
            # 保留长度和精度，但BOOLEAN不需要
            if pg_type == 'BOOLEAN':
                return pg_type
            if '(' in mysql_type:
                params = mysql_type[mysql_type.index('('):]
                return pg_type + params
            return pg_type
    
    return mysql_type

def get_table_structure(mysql_cursor, table_name):
    """获取表结构"""
    mysql_cursor.execute(f"SHOW CREATE TABLE {table_name}")
    create_sql = mysql_cursor.fetchone()[1]
    
    mysql_cursor.execute(f"DESCRIBE {table_name}")
    columns = mysql_cursor.fetchall()
    
    return columns, create_sql

def create_pg_table(pg_cursor, table_name, columns):
    """在PostgreSQL中创建表"""
    
    # 构建CREATE TABLE语句
    col_defs = []
    primary_key = None
    
    for col in columns:
        col_name, col_type, null, key, default, extra = col
        
        # 转换类型
        pg_type = convert_mysql_type_to_pg(col_type)
        
        # 处理AUTO_INCREMENT
        if 'auto_increment' in extra.lower():
            if 'int' in col_type.lower():
                if 'bigint' in col_type.lower():
                    pg_type = 'BIGSERIAL'
                else:
                    pg_type = 'SERIAL'
        
        # 构建列定义
        col_def = f'"{col_name}" {pg_type}'
        
        # NULL约束
        if null == 'NO':
            col_def += ' NOT NULL'
        
        # 主键
        if key == 'PRI':
            primary_key = col_name
        
        col_defs.append(col_def)
    
    # 添加主键约束
    if primary_key:
        col_defs.append(f'PRIMARY KEY ("{primary_key}")')
    
    # 生成CREATE TABLE语句
    create_sql = f'CREATE TABLE IF NOT EXISTS zjylzl."{table_name}" (\n  '
    create_sql += ',\n  '.join(col_defs)
    create_sql += '\n)'
    
    return create_sql

def migrate_table_data(mysql_cursor, pg_cursor, pg_conn, table_name):
    """迁移表数据"""
    
    # 获取数据
    mysql_cursor.execute(f"SELECT * FROM {table_name}")
    rows = mysql_cursor.fetchall()
    
    if not rows:
        return 0
    
    # 获取列信息（包括类型）
    mysql_cursor.execute(f"DESCRIBE {table_name}")
    columns_info = mysql_cursor.fetchall()
    columns = [col[0] for col in columns_info]
    column_types = {col[0]: col[1] for col in columns_info}
    
    # 转换数据
    converted_rows = []
    for row in rows:
        converted_row = []
        for i, value in enumerate(row):
            col_name = columns[i]
            col_type = column_types[col_name].lower()
            
            # 转换BOOLEAN类型
            if value is not None and ('bit(1)' in col_type or 'tinyint(1)' in col_type):
                # MySQL的bit(1)或tinyint(1)转为PostgreSQL的BOOLEAN
                if isinstance(value, bytes):
                    value = value != b'\x00'
                elif isinstance(value, int):
                    value = value != 0
                else:
                    value = bool(value)
            
            converted_row.append(value)
        converted_rows.append(tuple(converted_row))
    
    # 构建INSERT语句
    col_names = ', '.join([f'"{col}"' for col in columns])
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f'INSERT INTO zjylzl."{table_name}" ({col_names}) VALUES ({placeholders})'
    
    # 批量插入
    execute_batch(pg_cursor, insert_sql, converted_rows, page_size=100)
    pg_conn.commit()
    
    return len(converted_rows)

def migrate_all_tables():
    """迁移所有表"""
    print("=" * 80)
    print("步骤2: 导出并迁移数据")
    print("=" * 80)
    
    # 连接数据库
    mysql_conn = pymysql.connect(**DB_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    try:
        # 获取所有表
        mysql_cursor.execute("SHOW TABLES")
        tables = [row[0] for row in mysql_cursor.fetchall()]
        
        print(f"\n找到 {len(tables)} 个表需要迁移\n")
        
        total_rows = 0
        success_tables = []
        failed_tables = []
        
        for i, table in enumerate(tables, 1):
            print(f"[{i}/{len(tables)}] 迁移表: {table}")
            
            try:
                # 1. 获取表结构
                columns, _ = get_table_structure(mysql_cursor, table)
                print(f"  ├─ 获取结构: {len(columns)} 个字段")
                
                # 2. 创建PostgreSQL表
                create_sql = create_pg_table(pg_cursor, table, columns)
                
                # 先删除已存在的表
                pg_cursor.execute(f'DROP TABLE IF EXISTS zjylzl."{table}" CASCADE')
                pg_conn.commit()
                
                pg_cursor.execute(create_sql)
                pg_conn.commit()
                print(f"  ├─ 创建表: 成功")
                
                # 3. 迁移数据
                row_count = migrate_table_data(mysql_cursor, pg_cursor, pg_conn, table)
                total_rows += row_count
                print(f"  └─ 迁移数据: {row_count:,} 条记录")
                
                success_tables.append((table, row_count))
                
            except Exception as e:
                print(f"  └─ ❌ 失败: {e}")
                failed_tables.append((table, str(e)))
                pg_conn.rollback()
                continue
        
        # 总结
        print("\n" + "=" * 80)
        print("迁移完成总结")
        print("=" * 80)
        print(f"✅ 成功: {len(success_tables)} 个表")
        print(f"❌ 失败: {len(failed_tables)} 个表")
        print(f"📊 总记录数: {total_rows:,} 条")
        
        if failed_tables:
            print("\n失败的表:")
            for table, error in failed_tables:
                print(f"  - {table}: {error[:50]}...")
        
        # 验证数据
        print("\n" + "=" * 80)
        print("验证数据")
        print("=" * 80)
        
        for table, expected_count in success_tables[:10]:
            pg_cursor.execute(f'SELECT COUNT(*) FROM zjylzl."{table}"')
            actual_count = pg_cursor.fetchone()[0]
            
            status = "✅" if actual_count == expected_count else "❌"
            print(f"{status} {table}: {actual_count:,} / {expected_count:,}")
        
        if len(success_tables) > 10:
            print(f"... 还有 {len(success_tables) - 10} 个表")
        
        return len(failed_tables) == 0
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        mysql_cursor.close()
        mysql_conn.close()
        pg_cursor.close()
        pg_conn.close()

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("PostgreSQL迁移 - 阶段2: 数据迁移")
    print("=" * 80)
    
    start_time = time.time()
    
    success = migrate_all_tables()
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    if success:
        print(f"✅ 数据迁移完成！耗时: {elapsed_time:.1f} 秒")
        print("=" * 80)
        print("\n下一步: 修改应用配置（application.yml 和 pom.xml）")
    else:
        print(f"❌ 数据迁移失败！耗时: {elapsed_time:.1f} 秒")
        print("=" * 80)
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
