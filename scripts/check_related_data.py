# -*- coding: utf-8 -*-
"""
检查500错误记录的所有关联数据完整性
"""
import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

print("=" * 100)
print("检查500错误记录的关联数据完整性")
print("=" * 100)

error_ids = [34, 49, 55, 56, 64, 116, 122, 125]

for reg_id in error_ids:
    print(f"\n{'-' * 100}")
    print(f"[记录 {reg_id}]")
    print(f"{'-' * 100}")
    
    # 获取 registration 记录
    cursor.execute("""
        SELECT *
        FROM registrations
        WHERE id = %s
    """, (reg_id,))
    
    reg = cursor.fetchone()
    
    if not reg:
        print(f"  [ERROR] registrations 表中未找到记录")
        continue
    
    # 检查关联表
    checks = [
        ('competition', 'competitions', reg['competition_id']),
        ('institution', 'const_init_institutions', reg['institution_id']),
        ('applicant', 'user_accounts', reg['applicant_id'])
    ]
    
    all_ok = True
    
    for name, table, fk_id in checks:
        if fk_id:
            cursor.execute(f"""
                SELECT id FROM {table} WHERE id = %s
            """, (fk_id,))
            
            result = cursor.fetchone()
            
            if result:
                print(f"  {name:<15} id={fk_id:<10} [OK]")
            else:
                print(f"  {name:<15} id={fk_id:<10} [ERROR] 记录不存在")
                all_ok = False
        else:
            print(f"  {name:<15} id=NULL        [WARNING] 外键为空")
    
    # 检查 activity_info
    cursor.execute("""
        SELECT * FROM activity_infos WHERE registration_id = %s
    """, (reg_id,))
    
    activity = cursor.fetchone()
    
    if activity:
        print(f"  activity_info   [OK]")
    else:
        print(f"  activity_info   [ERROR] 未找到关联的 activity_info")
        all_ok = False
    
    if all_ok:
        print(f"\n  [结论] 所有关联数据完整")
    else:
        print(f"\n  [结论] 存在缺失的关联数据")

cursor.close()
conn.close()

print(f"\n{'=' * 100}")
