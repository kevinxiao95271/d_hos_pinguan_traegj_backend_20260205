#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复组别名称，去掉括号"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def fix_group_names():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 查看修改前的数据
        print("=== 修改前的组别分布 ===\n")
        cursor.execute("SELECT DISTINCT competition_group, COUNT(*) as count FROM pinguan_his_data GROUP BY competition_group ORDER BY count DESC")
        groups = cursor.fetchall()
        for group, count in groups:
            print(f"  '{group}': {count} 条")
        
        # 2. 执行修改
        print("\n=== 开始修改 ===\n")
        old_value = "基层组(基层组积分方式同综合组)"
        new_value = "基层组"
        
        cursor.execute(
            "UPDATE pinguan_his_data SET competition_group = %s WHERE competition_group = %s",
            (new_value, old_value)
        )
        affected_rows = cursor.rowcount
        print(f"已修改 {affected_rows} 条记录")
        
        # 3. 提交事务
        conn.commit()
        print("✓ 修改已提交")
        
        # 4. 查看修改后的数据
        print("\n=== 修改后的组别分布 ===\n")
        cursor.execute("SELECT DISTINCT competition_group, COUNT(*) as count FROM pinguan_his_data GROUP BY competition_group ORDER BY count DESC")
        groups = cursor.fetchall()
        for group, count in groups:
            print(f"  '{group}': {count} 条")
        
        print("\n=== 验证修改 ===\n")
        cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE competition_group = %s", (new_value,))
        count = cursor.fetchone()[0]
        print(f"'基层组' 记录数: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM pinguan_his_data WHERE competition_group = %s", (old_value,))
        count = cursor.fetchone()[0]
        print(f"'基层组(基层组积分方式同综合组)' 记录数: {count}")
        
        if count == 0:
            print("\n✓ 修改成功！所有带括号的基层组已改为'基层组'")
        else:
            print(f"\n✗ 还有 {count} 条记录未修改")
            
    except Exception as e:
        print(f"\n✗ 修改失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("准备修改数据库中的组别名称...")
    print("将 '基层组(基层组积分方式同综合组)' 改为 '基层组'\n")
    
    confirm = input("确认执行修改？(yes/no): ")
    if confirm.lower() == 'yes':
        fix_group_names()
    else:
        print("已取消修改")
