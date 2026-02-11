#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PostgreSQL迁移 - 步骤1: 准备工作"""

import pymysql
import psycopg2
from db_config import DB_CONFIG

# PostgreSQL配置
PG_CONFIG = {
    'host': '119.167.165.27',
    'port': 5432,
    'database': 'zjylzl',
    'user': 'postgres',
    'password': 'zjylzl',
    'options': '-c search_path=zjylzl'
}

def test_connections():
    """测试数据库连接"""
    print("=" * 80)
    print("步骤1: 测试数据库连接")
    print("=" * 80)
    
    # 测试MySQL连接
    print("\n【1.1】测试MySQL连接...")
    try:
        mysql_conn = pymysql.connect(**DB_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT VERSION()")
        version = mysql_cursor.fetchone()[0]
        print(f"✅ MySQL连接成功")
        print(f"   版本: {version}")
        mysql_cursor.close()
        mysql_conn.close()
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        return False
    
    # 测试PostgreSQL连接
    print("\n【1.2】测试PostgreSQL连接...")
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT version()")
        version = pg_cursor.fetchone()[0]
        print(f"✅ PostgreSQL连接成功")
        print(f"   版本: {version[:50]}...")
        pg_cursor.close()
        pg_conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return False
    
    return True

def check_pg_schema():
    """检查PostgreSQL Schema"""
    print("\n【1.3】检查PostgreSQL Schema...")
    
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        
        # 检查schema是否存在
        pg_cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'zjylzl'
        """)
        
        if pg_cursor.fetchone():
            print("✅ Schema 'zjylzl' 已存在")
        else:
            print("⚠️  Schema 'zjylzl' 不存在，正在创建...")
            pg_cursor.execute("CREATE SCHEMA IF NOT EXISTS zjylzl")
            pg_conn.commit()
            print("✅ Schema 'zjylzl' 创建成功")
        
        # 检查权限
        pg_cursor.execute("""
            SELECT has_schema_privilege('postgres', 'zjylzl', 'CREATE')
        """)
        has_privilege = pg_cursor.fetchone()[0]
        
        if has_privilege:
            print("✅ 用户有CREATE权限")
        else:
            print("❌ 用户没有CREATE权限")
            return False
        
        pg_cursor.close()
        pg_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查Schema失败: {e}")
        return False

def analyze_mysql_data():
    """分析MySQL数据"""
    print("\n【1.4】分析MySQL数据...")
    
    try:
        mysql_conn = pymysql.connect(**DB_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # 获取所有表
        mysql_cursor.execute("SHOW TABLES")
        tables = [row[0] for row in mysql_cursor.fetchall()]
        
        print(f"\n找到 {len(tables)} 个表:")
        
        total_rows = 0
        table_stats = []
        
        for table in tables:
            mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = mysql_cursor.fetchone()[0]
            total_rows += count
            table_stats.append((table, count))
        
        # 按记录数排序
        table_stats.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n{'表名':<40} {'记录数':>10}")
        print("-" * 52)
        for table, count in table_stats:
            print(f"{table:<40} {count:>10,}")
        
        print("-" * 52)
        print(f"{'总计':<40} {total_rows:>10,}")
        
        mysql_cursor.close()
        mysql_conn.close()
        
        return {
            'table_count': len(tables),
            'total_rows': total_rows,
            'tables': table_stats
        }
        
    except Exception as e:
        print(f"❌ 分析MySQL数据失败: {e}")
        return None

def check_table_structures():
    """检查表结构"""
    print("\n【1.5】检查表结构...")
    
    try:
        mysql_conn = pymysql.connect(**DB_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # 获取所有表
        mysql_cursor.execute("SHOW TABLES")
        tables = [row[0] for row in mysql_cursor.fetchall()]
        
        print(f"\n检查 {len(tables)} 个表的结构...")
        
        enum_tables = []
        auto_increment_tables = []
        
        for table in tables:
            # 检查字段类型
            mysql_cursor.execute(f"DESCRIBE {table}")
            columns = mysql_cursor.fetchall()
            
            for col in columns:
                col_name, col_type, null, key, default, extra = col
                
                # 检查ENUM类型
                if 'enum' in col_type.lower():
                    enum_tables.append((table, col_name, col_type))
                
                # 检查AUTO_INCREMENT
                if 'auto_increment' in extra.lower():
                    auto_increment_tables.append((table, col_name))
        
        if enum_tables:
            print(f"\n⚠️  发现 {len(enum_tables)} 个ENUM字段（需要转换）:")
            for table, col, col_type in enum_tables[:5]:
                print(f"   {table}.{col}: {col_type}")
            if len(enum_tables) > 5:
                print(f"   ... 还有 {len(enum_tables) - 5} 个")
        else:
            print("\n✅ 没有ENUM字段")
        
        if auto_increment_tables:
            print(f"\n✅ 发现 {len(auto_increment_tables)} 个AUTO_INCREMENT字段")
        
        mysql_cursor.close()
        mysql_conn.close()
        
        return {
            'enum_count': len(enum_tables),
            'auto_increment_count': len(auto_increment_tables),
            'enum_fields': enum_tables,
            'auto_increment_fields': auto_increment_tables
        }
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        return None

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("PostgreSQL迁移 - 阶段1: 准备工作")
    print("=" * 80)
    
    # 1. 测试连接
    if not test_connections():
        print("\n❌ 连接测试失败，请检查配置")
        return False
    
    # 2. 检查Schema
    if not check_pg_schema():
        print("\n❌ Schema检查失败")
        return False
    
    # 3. 分析数据
    data_stats = analyze_mysql_data()
    if not data_stats:
        print("\n❌ 数据分析失败")
        return False
    
    # 4. 检查表结构
    structure_stats = check_table_structures()
    if not structure_stats:
        print("\n❌ 表结构检查失败")
        return False
    
    # 总结
    print("\n" + "=" * 80)
    print("准备工作完成总结")
    print("=" * 80)
    print(f"✅ MySQL连接正常")
    print(f"✅ PostgreSQL连接正常")
    print(f"✅ Schema准备就绪")
    print(f"✅ 数据统计: {data_stats['table_count']} 个表, {data_stats['total_rows']:,} 条记录")
    print(f"⚠️  需要处理: {structure_stats['enum_count']} 个ENUM字段")
    print(f"✅ 自增字段: {structure_stats['auto_increment_count']} 个")
    
    print("\n准备工作完成，可以继续下一步：数据导出")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            print("\n❌ 准备工作失败，请解决问题后重试")
            exit(1)
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
