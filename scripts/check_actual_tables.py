# -*- coding: utf-8 -*-
"""
检查实际使用的表和外键
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

def check_actual_tables():
    """检查实际使用的表"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("检查数据库中的实际表")
    print("=" * 80)
    
    # 1. 列出所有表
    cursor.execute("SHOW TABLES")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    # 分类
    active_tables = [t for t in all_tables if not t.endswith('_discard')]
    discard_tables = [t for t in all_tables if t.endswith('_discard')]
    
    print(f"\n总计 {len(all_tables)} 个表:")
    print(f"  - 活跃表: {len(active_tables)} 个")
    print(f"  - 废弃表(_discard): {len(discard_tables)} 个")
    
    print(f"\n【活跃表列表】")
    for table in sorted(active_tables):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = cursor.fetchone()[0]
        print(f"  {table:40s} {cnt:8,} 条记录")
    
    # 2. 检查活跃表的外键
    print("\n" + "=" * 80)
    print("检查活跃表的外键约束")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            CONSTRAINT_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
        AND REFERENCED_TABLE_NAME IS NOT NULL
        AND TABLE_NAME NOT LIKE '%_discard'
        ORDER BY TABLE_NAME, CONSTRAINT_NAME
    """)
    active_fks = cursor.fetchall()
    
    if active_fks:
        print(f"\n活跃表中有 {len(active_fks)} 个外键约束:")
        for fk in active_fks:
            print(f"  - {fk[0]}.{fk[1]} -> {fk[3]}.{fk[4]} (外键: {fk[2]})")
    else:
        print("\n[OK] 活跃表中没有外键约束")
    
    # 3. 检查user_accounts表（报名相关）
    print("\n" + "=" * 80)
    print("检查user_accounts表")
    print("=" * 80)
    
    if 'user_accounts' in active_tables:
        cursor.execute("DESCRIBE user_accounts")
        cols = cursor.fetchall()
        
        print(f"\nuser_accounts表有 {len(cols)} 个字段:")
        for col in cols:
            if 'institution' in col[0].lower():
                print(f"  [*] {col[0]:30s} {col[1]:30s} NULL:{col[2]:5s} KEY:{col[3]}")
            else:
                print(f"      {col[0]:30s} {col[1]:30s} NULL:{col[2]:5s} KEY:{col[3]}")
        
        # 检查索引
        print("\n【user_accounts索引】")
        cursor.execute("SHOW INDEX FROM user_accounts")
        indexes = cursor.fetchall()
        
        idx_dict = {}
        for idx in indexes:
            idx_name = idx[2]
            col_name = idx[4]
            if idx_name not in idx_dict:
                idx_dict[idx_name] = []
            idx_dict[idx_name].append(col_name)
        
        for idx_name, cols in idx_dict.items():
            print(f"  - {idx_name:30s} ({', '.join(cols)})")
    
    # 4. 检查registrations表
    print("\n" + "=" * 80)
    print("检查registrations表")
    print("=" * 80)
    
    if 'registrations' in active_tables:
        cursor.execute("DESCRIBE registrations")
        cols = cursor.fetchall()
        
        print(f"\nregistrations表有 {len(cols)} 个字段:")
        for col in cols:
            if 'institution' in col[0].lower() or 'applicant' in col[0].lower():
                print(f"  [*] {col[0]:30s} {col[1]:30s} NULL:{col[2]:5s} KEY:{col[3]}")
            else:
                print(f"      {col[0]:30s} {col[1]:30s} NULL:{col[2]:5s} KEY:{col[3]}")
        
        # 检查索引
        print("\n【registrations索引】")
        cursor.execute("SHOW INDEX FROM registrations")
        indexes = cursor.fetchall()
        
        idx_dict = {}
        for idx in indexes:
            idx_name = idx[2]
            col_name = idx[4]
            if idx_name not in idx_dict:
                idx_dict[idx_name] = []
            idx_dict[idx_name].append(col_name)
        
        for idx_name, cols in idx_dict.items():
            print(f"  - {idx_name:30s} ({', '.join(cols)})")
    
    # 5. 生成优化SQL
    print("\n" + "=" * 80)
    print("性能优化建议")
    print("=" * 80)
    
    # 检查是否需要添加索引
    suggestions = []
    
    if 'user_accounts' in active_tables:
        cursor.execute("SHOW INDEX FROM user_accounts WHERE Column_name = 'institution_id'")
        if not cursor.fetchall():
            suggestions.append("ALTER TABLE user_accounts ADD INDEX idx_institution_id (institution_id);")
    
    if 'registrations' in active_tables:
        cursor.execute("SHOW INDEX FROM registrations WHERE Column_name = 'institution_id'")
        if not cursor.fetchall():
            suggestions.append("ALTER TABLE registrations ADD INDEX idx_institution_id (institution_id);")
        
        cursor.execute("SHOW INDEX FROM registrations WHERE Column_name = 'applicant_id'")
        if not cursor.fetchall():
            suggestions.append("ALTER TABLE registrations ADD INDEX idx_applicant_id (applicant_id);")
    
    if suggestions:
        print("\n需要添加的索引:")
        for sql in suggestions:
            print(f"  {sql}")
    else:
        print("\n[OK] 主要索引已齐全")
    
    # 6. 删除废弃表的外键
    if discard_tables:
        print("\n-- 可选：删除废弃表的外键约束（提升整体性能）")
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
            AND REFERENCED_TABLE_NAME IS NOT NULL
            AND TABLE_NAME LIKE '%_discard'
            GROUP BY TABLE_NAME, CONSTRAINT_NAME
        """)
        discard_fks = cursor.fetchall()
        
        for table, fk_name in discard_fks:
            print(f"-- ALTER TABLE {table} DROP FOREIGN KEY {fk_name};")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        check_actual_tables()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
