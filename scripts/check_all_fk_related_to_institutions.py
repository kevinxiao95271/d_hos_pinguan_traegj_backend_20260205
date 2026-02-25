# -*- coding: utf-8 -*-
"""
检查所有与institutions相关的外键
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

def check_all_fks():
    """检查所有外键"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("检查整个数据库的外键约束")
    print("=" * 80)
    
    # 1. 所有外键
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
        ORDER BY TABLE_NAME, CONSTRAINT_NAME
    """)
    all_fks = cursor.fetchall()
    
    print(f"\n整个数据库共有 {len(all_fks)} 个外键约束")
    
    # 2. 按表分组
    fk_by_table = {}
    institutions_related = []
    
    for fk in all_fks:
        table = fk[0]
        if table not in fk_by_table:
            fk_by_table[table] = []
        fk_by_table[table].append(fk)
        
        # 检查是否与institutions相关
        if fk[3] == 'institutions' or table == 'institutions':
            institutions_related.append(fk)
    
    print(f"\n【所有外键按表分组】")
    for table, fks in sorted(fk_by_table.items()):
        print(f"\n{table} ({len(fks)}个外键):")
        for fk in fks:
            print(f"  - {fk[2]}: {fk[1]} -> {fk[3]}.{fk[4]}")
    
    # 3. institutions相关的外键
    print("\n" + "=" * 80)
    print("与institutions相关的外键")
    print("=" * 80)
    
    if institutions_related:
        print(f"\n发现 {len(institutions_related)} 个与institutions相关的外键:")
        for fk in institutions_related:
            print(f"  - {fk[0]}.{fk[1]} -> {fk[3]}.{fk[4]} (外键名: {fk[2]})")
    else:
        print("\n[OK] 没有与institutions相关的外键")
    
    # 4. 检查users表
    print("\n" + "=" * 80)
    print("检查users表")
    print("=" * 80)
    
    cursor.execute("DESCRIBE users")
    user_cols = cursor.fetchall()
    print(f"\nusers表有 {len(user_cols)} 个字段:")
    for col in user_cols:
        col_name = col[0]
        col_type = col[1]
        col_key = col[3]
        if 'institution' in col_name.lower():
            print(f"  [*] {col_name:30s} {col_type:30s} KEY:{col_key}")
        else:
            print(f"      {col_name:30s} {col_type:30s} KEY:{col_key}")
    
    # 5. 检查users表的索引
    print("\n【users表索引】")
    cursor.execute("SHOW INDEX FROM users")
    user_indexes = cursor.fetchall()
    
    user_idx_dict = {}
    for idx in user_indexes:
        idx_name = idx[2]
        col_name = idx[4]
        if idx_name not in user_idx_dict:
            user_idx_dict[idx_name] = []
        user_idx_dict[idx_name].append(col_name)
    
    for idx_name, cols in user_idx_dict.items():
        cols_str = ', '.join(cols)
        print(f"  - {idx_name:30s} ({cols_str})")
    
    # 6. 检查是否有institution_id字段但没有索引
    has_institution_id = False
    has_institution_id_index = False
    
    for col in user_cols:
        if col[0] == 'institution_id':
            has_institution_id = True
            if col[3] != '':  # KEY字段不为空说明有索引
                has_institution_id_index = True
    
    print("\n【关键检查】")
    if has_institution_id:
        print(f"  users.institution_id 字段: 存在")
        if has_institution_id_index:
            print(f"  users.institution_id 索引: 已有")
        else:
            print(f"  users.institution_id 索引: [WARNING] 缺失！")
    
    # 7. 生成SQL修复语句
    print("\n" + "=" * 80)
    print("修复SQL语句")
    print("=" * 80)
    
    if institutions_related:
        print("\n-- 删除与institutions相关的外键")
        for fk in institutions_related:
            print(f"ALTER TABLE {fk[0]} DROP FOREIGN KEY {fk[2]};")
    
    if has_institution_id and not has_institution_id_index:
        print("\n-- 为users.institution_id添加索引")
        print("CREATE INDEX idx_institution_id ON users(institution_id);")
    
    print("\n-- 为其他可能的关联字段添加索引")
    print("-- (根据实际查询情况调整)")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        check_all_fks()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
