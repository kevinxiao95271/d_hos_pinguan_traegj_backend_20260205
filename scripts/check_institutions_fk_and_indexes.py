# -*- coding: utf-8 -*-
"""
检查institutions表的外键和索引
"""
import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def check_fk_and_indexes():
    """检查外键和索引"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("检查institutions表的外键和索引")
    print("=" * 80)
    
    # 1. 检查外键
    print("\n【外键约束】")
    cursor.execute("""
        SELECT 
            CONSTRAINT_NAME,
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'institutions'
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    fks = cursor.fetchall()
    
    if fks:
        print(f"发现 {len(fks)} 个外键约束:")
        for fk in fks:
            print(f"  - {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
    else:
        print("  无外键约束")
    
    # 2. 检查索引
    print("\n【索引】")
    cursor.execute("SHOW INDEX FROM institutions")
    indexes = cursor.fetchall()
    
    index_dict = {}
    for idx in indexes:
        idx_name = idx[2]
        col_name = idx[4]
        if idx_name not in index_dict:
            index_dict[idx_name] = []
        index_dict[idx_name].append(col_name)
    
    print(f"发现 {len(index_dict)} 个索引:")
    for idx_name, cols in index_dict.items():
        cols_str = ', '.join(cols)
        print(f"  - {idx_name:30s} ({cols_str})")
    
    # 3. 检查哪些表引用了institutions
    print("\n【被引用情况】")
    cursor.execute("""
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            CONSTRAINT_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
        AND REFERENCED_TABLE_NAME = 'institutions'
    """)
    refs = cursor.fetchall()
    
    if refs:
        print(f"发现 {len(refs)} 个表引用了institutions:")
        for ref in refs:
            print(f"  - {ref[0]}.{ref[1]} -> institutions.{ref[3]} (外键: {ref[2]})")
    else:
        print("  无其他表引用")
    
    # 4. 检查表结构
    print("\n【表结构】")
    cursor.execute("DESCRIBE institutions")
    columns = cursor.fetchall()
    
    print(f"institutions表有 {len(columns)} 个字段:")
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        col_null = col[2]
        col_key = col[3]
        print(f"  {col_name:30s} {col_type:30s} NULL:{col_null:5s} KEY:{col_key}")
    
    # 5. 统计数据量
    print("\n【数据统计】")
    cursor.execute("SELECT COUNT(*) FROM institutions")
    total = cursor.fetchone()[0]
    print(f"institutions表共有 {total:,} 条记录")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        check_fk_and_indexes()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
