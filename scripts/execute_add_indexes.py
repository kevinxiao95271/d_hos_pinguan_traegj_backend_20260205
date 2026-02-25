# -*- coding: utf-8 -*-
"""
执行添加索引
"""
import pymysql
import time

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def add_index_safe(cursor, table, index_name, column):
    """安全地添加索引（如果不存在）"""
    try:
        # 检查索引是否已存在
        cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index_name}'")
        if cursor.fetchone():
            print(f"  [SKIP] {table}.{index_name} 已存在")
            return False
        
        # 创建索引
        sql = f"CREATE INDEX {index_name} ON {table}({column})"
        print(f"  [CREATE] {sql}")
        cursor.execute(sql)
        return True
    except Exception as e:
        print(f"  [ERROR] {table}.{index_name}: {e}")
        return False

def execute_add_indexes():
    """执行添加索引"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("添加缺失的索引")
    print("=" * 80)
    
    created_count = 0
    
    # 1. user_accounts表
    print("\n【user_accounts表】")
    if add_index_safe(cursor, 'user_accounts', 'idx_institution_id', 'institution_id'):
        created_count += 1
    if add_index_safe(cursor, 'user_accounts', 'idx_role', 'role'):
        created_count += 1
    if add_index_safe(cursor, 'user_accounts', 'idx_enabled', 'enabled'):
        created_count += 1
    
    # 2. registrations表
    print("\n【registrations表】")
    if add_index_safe(cursor, 'registrations', 'idx_institution_id', 'institution_id'):
        created_count += 1
    if add_index_safe(cursor, 'registrations', 'idx_applicant_id', 'applicant_id'):
        created_count += 1
    if add_index_safe(cursor, 'registrations', 'idx_competition_id', 'competition_id'):
        created_count += 1
    if add_index_safe(cursor, 'registrations', 'idx_status', 'status'):
        created_count += 1
    if add_index_safe(cursor, 'registrations', 'idx_group_code', 'group_code'):
        created_count += 1
    
    # 3. 其他表的常用查询字段
    print("\n【其他表】")
    if add_index_safe(cursor, 'registration_members', 'idx_registration_id', 'registration_id'):
        created_count += 1
    if add_index_safe(cursor, 'material_files', 'idx_registration_id', 'registration_id'):
        created_count += 1
    if add_index_safe(cursor, 'project_summaries', 'idx_registration_id', 'registration_id'):
        created_count += 1
    if add_index_safe(cursor, 'activity_infos', 'idx_registration_id', 'registration_id'):
        created_count += 1
    
    # 提交事务
    conn.commit()
    
    # 4. 显示结果
    print("\n" + "=" * 80)
    print("索引创建完成")
    print("=" * 80)
    print(f"新增索引数: {created_count}")
    
    # 5. 显示最终索引列表
    print("\n【user_accounts表索引】")
    cursor.execute("SHOW INDEX FROM user_accounts")
    indexes = cursor.fetchall()
    idx_dict = {}
    for idx in indexes:
        idx_name = idx[2]
        col_name = idx[4]
        if idx_name not in idx_dict:
            idx_dict[idx_name] = []
        idx_dict[idx_name].append(col_name)
    
    for idx_name, cols in sorted(idx_dict.items()):
        print(f"  - {idx_name:30s} ({', '.join(cols)})")
    
    print("\n【registrations表索引】")
    cursor.execute("SHOW INDEX FROM registrations")
    indexes = cursor.fetchall()
    idx_dict = {}
    for idx in indexes:
        idx_name = idx[2]
        col_name = idx[4]
        if idx_name not in idx_dict:
            idx_dict[idx_name] = []
        idx_dict[idx_name].append(col_name)
    
    for idx_name, cols in sorted(idx_dict.items()):
        print(f"  - {idx_name:30s} ({', '.join(cols)})")
    
    print("\n[OK] 所有索引已就绪，性能应大幅提升！")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        execute_add_indexes()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
