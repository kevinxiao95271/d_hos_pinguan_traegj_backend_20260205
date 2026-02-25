# -*- coding: utf-8 -*-
"""
自动迁移（无交互）
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

def migrate_auto():
    """自动迁移"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("自动迁移机构数据")
    print("=" * 80)
    
    try:
        # 1. 创建表
        print("\n[1/4] 创建 const_init_institutions 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS const_init_institutions (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                code VARCHAR(64) NOT NULL,
                uscc VARCHAR(32) NOT NULL,
                name VARCHAR(200) NOT NULL,
                region VARCHAR(64),
                city VARCHAR(50),
                level VARCHAR(32),
                created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                
                UNIQUE KEY uk_code (code),
                UNIQUE KEY uk_uscc (uscc),
                KEY idx_name (name),
                KEY idx_region (region),
                KEY idx_city (city),
                KEY idx_level (level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("  OK")
        
        # 2. 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
        const_count = cursor.fetchone()[0]
        
        if const_count == 0:
            # 3. 迁移数据
            print("\n[2/4] 迁移数据...")
            cursor.execute("""
                INSERT IGNORE INTO const_init_institutions (code, uscc, name, region, city, level, created_at)
                SELECT code, uscc, name, region, city, level, created_at
                FROM institutions
            """)
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
            const_count = cursor.fetchone()[0]
            print(f"  OK 迁移了 {const_count:,} 条记录")
        else:
            print(f"\n[2/4] const_init_institutions 已有数据: {const_count:,} 条")
        
        # 4. 查找需要保留的机构
        print("\n[3/4] 查找活跃机构...")
        cursor.execute("""
            SELECT DISTINCT institution_id 
            FROM user_accounts 
            WHERE institution_id IS NOT NULL
        """)
        keep_ids = [row[0] for row in cursor.fetchall()]
        print(f"  需要保留: {len(keep_ids)} 个机构")
        
        # 5. 清理 institutions（保留活跃机构）
        print("\n[4/4] 清理 institutions 表...")
        cursor.execute("SELECT COUNT(*) FROM institutions")
        before_count = cursor.fetchone()[0]
        
        if keep_ids:
            cursor.execute("""
                DELETE FROM institutions 
                WHERE id NOT IN ({})
            """.format(','.join(map(str, keep_ids))))
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM institutions")
            after_count = cursor.fetchone()[0]
            
            print(f"  删除前: {before_count:,} 条")
            print(f"  删除后: {after_count:,} 条")
            print(f"  已删除: {before_count - after_count:,} 条")
        else:
            print("  WARN 没有需要保留的机构")
        
        # 6. 汇总
        print("\n" + "=" * 80)
        print("迁移完成")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
        const_final = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM institutions")
        inst_final = cursor.fetchone()[0]
        
        print(f"\nconst_init_institutions: {const_final:,} 条 (全量，用于搜索)")
        print(f"institutions:             {inst_final:,} 条 (活跃，用于业务)")
        
        print("\n✓ 迁移成功！")
        print("  - 注册时从 const_init_institutions 搜索")
        print("  - 选择后自动同步到 institutions")
        print("  - 业务流程使用 institutions（轻量级）")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_auto()
