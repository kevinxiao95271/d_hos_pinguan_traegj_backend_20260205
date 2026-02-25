# -*- coding: utf-8 -*-
"""
迁移机构数据：institutions → const_init_institutions
保留已有用户关联的机构在 institutions 表中
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

def migrate():
    """执行迁移"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("机构数据迁移")
    print("=" * 80)
    
    try:
        # 1. 检查当前状态
        print("\n[1/6] 检查当前状态...")
        cursor.execute("SELECT COUNT(*) FROM institutions")
        inst_count = cursor.fetchone()[0]
        print(f"  institutions 表: {inst_count:,} 条记录")
        
        cursor.execute("SELECT COUNT(*) FROM user_accounts WHERE institution_id IS NOT NULL")
        user_with_inst = cursor.fetchone()[0]
        print(f"  关联机构的用户: {user_with_inst} 个")
        
        # 2. 创建 const_init_institutions 表
        print("\n[2/6] 创建 const_init_institutions 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS const_init_institutions (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                code VARCHAR(64) NOT NULL COMMENT '机构代码',
                uscc VARCHAR(32) NOT NULL COMMENT '统一社会信用代码',
                name VARCHAR(200) NOT NULL COMMENT '机构名称',
                region VARCHAR(64) COMMENT '地区',
                city VARCHAR(50) COMMENT '城市',
                level VARCHAR(32) COMMENT '等级',
                created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                
                UNIQUE KEY uk_code (code),
                UNIQUE KEY uk_uscc (uscc),
                KEY idx_name (name),
                KEY idx_region (region),
                KEY idx_city (city),
                KEY idx_level (level),
                KEY idx_region_name (region, name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='常量机构库（36K+，仅用于注册时搜索）'
        """)
        conn.commit()
        print("  OK 表创建成功")
        
        # 3. 检查是否已经迁移过
        cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
        const_count = cursor.fetchone()[0]
        
        if const_count > 0:
            print(f"  WARN const_init_institutions 已有 {const_count:,} 条数据")
            print("  跳过迁移，使用现有数据")
            # 直接使用现有数据，不重新迁移
        
        # 4. 迁移数据到 const_init_institutions
        print("\n[3/6] 迁移数据到 const_init_institutions...")
        start = time.time()
        cursor.execute("""
            INSERT IGNORE INTO const_init_institutions (code, uscc, name, region, city, level, created_at)
            SELECT code, uscc, name, region, city, level, created_at
            FROM institutions
        """)
        conn.commit()
        elapsed = time.time() - start
        
        if cursor.rowcount < inst_count:
            print(f"  WARN 跳过了 {inst_count - cursor.rowcount} 条重复记录")
        
        cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
        migrated = cursor.fetchone()[0]
        print(f"  OK 迁移完成: {migrated:,} 条记录 ({elapsed:.2f}秒)")
        
        # 5. 查找需要保留的机构（有用户关联的）
        print("\n[4/6] 查找需要保留的机构...")
        cursor.execute("""
            SELECT DISTINCT institution_id 
            FROM user_accounts 
            WHERE institution_id IS NOT NULL
        """)
        keep_ids = [row[0] for row in cursor.fetchall()]
        print(f"  需要保留: {len(keep_ids)} 个机构")
        
        if keep_ids:
            cursor.execute("""
                SELECT id, name, region 
                FROM institutions 
                WHERE id IN ({})
            """.format(','.join(map(str, keep_ids))))
            keep_insts = cursor.fetchall()
            print(f"  保留的机构列表:")
            for inst_id, name, region in keep_insts:
                print(f"    - ID:{inst_id:5d} {name[:40]:40s} ({region})")
        
        # 6. 清理 institutions 表（保留有用户的机构）
        print("\n[5/6] 清理 institutions 表...")
        print("  WARN 即将删除无用户关联的机构")
        
        if not keep_ids:
            print("  [WARNING] 没有需要保留的机构，将清空整个表")
            response = input("  确认清空 institutions 表？(y/n): ")
            if response.lower() == 'y':
                cursor.execute("TRUNCATE TABLE institutions")
                conn.commit()
                print("  OK institutions 表已清空")
        else:
            response = input(f"  确认删除除 {len(keep_ids)} 个机构外的所有数据？(y/n): ")
            if response.lower() == 'y':
                cursor.execute("""
                    DELETE FROM institutions 
                    WHERE id NOT IN ({})
                """.format(','.join(map(str, keep_ids))))
                deleted = cursor.rowcount
                conn.commit()
                print(f"  OK 删除了 {deleted:,} 条记录")
                
                cursor.execute("SELECT COUNT(*) FROM institutions")
                remaining = cursor.fetchone()[0]
                print(f"  OK institutions 表剩余: {remaining} 条记录")
        
        # 7. 汇总结果
        print("\n[6/6] 迁移完成！")
        print("=" * 80)
        print("最终状态")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
        const_final = cursor.fetchone()[0]
        print(f"const_init_institutions: {const_final:,} 条 (全量机构库)")
        
        cursor.execute("SELECT COUNT(*) FROM institutions")
        inst_final = cursor.fetchone()[0]
        print(f"institutions:             {inst_final:,} 条 (活跃机构)")
        
        print("\n说明:")
        print("1. const_init_institutions: 存储全部36K+机构，仅用于注册搜索")
        print("2. institutions: 只存储有用户注册的机构，用于业务流程")
        print("3. 后续注册流程会自动同步选中的机构到 institutions")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
