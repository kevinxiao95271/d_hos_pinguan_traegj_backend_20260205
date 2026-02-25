# -*- coding: utf-8 -*-
"""
检查并修复重复的机构数据
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

def check_duplicates():
    """检查重复数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("检查重复数据")
    print("=" * 80)
    
    # 1. 检查重复的uscc
    print("\n[检查重复USCC]")
    cursor.execute("""
        SELECT uscc, COUNT(*) as cnt 
        FROM institutions 
        GROUP BY uscc 
        HAVING cnt > 1
    """)
    dup_uscc = cursor.fetchall()
    
    if dup_uscc:
        print(f"发现 {len(dup_uscc)} 个重复的USCC:")
        for uscc, cnt in dup_uscc[:10]:
            print(f"  {uscc}: {cnt} 条记录")
            
            # 显示重复记录
            cursor.execute("""
                SELECT id, name, region, created_at 
                FROM institutions 
                WHERE uscc = %s 
                ORDER BY id
            """, (uscc,))
            records = cursor.fetchall()
            for rec_id, name, region, created_at in records:
                print(f"    ID:{rec_id:5d} {name[:30]:30s} {region:10s} {created_at}")
    else:
        print("  [OK] 没有重复的USCC")
    
    # 2. 检查重复的code
    print("\n[检查重复CODE]")
    cursor.execute("""
        SELECT code, COUNT(*) as cnt 
        FROM institutions 
        GROUP BY code 
        HAVING cnt > 1
    """)
    dup_code = cursor.fetchall()
    
    if dup_code:
        print(f"发现 {len(dup_code)} 个重复的CODE:")
        for code, cnt in dup_code[:10]:
            print(f"  {code}: {cnt} 条记录")
    else:
        print("  [OK] 没有重复的CODE")
    
    cursor.close()
    conn.close()
    
    return len(dup_uscc) > 0 or len(dup_code) > 0

if __name__ == "__main__":
    has_dup = check_duplicates()
    
    if has_dup:
        print("\n建议: 先清理重复数据，或使用 INSERT IGNORE 跳过重复")
