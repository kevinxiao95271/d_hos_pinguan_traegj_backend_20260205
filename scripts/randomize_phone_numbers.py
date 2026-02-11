#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""混淆数据库中的所有手机号"""

import pymysql
import random
from db_config import DB_CONFIG

def randomize_phones():
    """随机修改所有手机号"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 查找所有包含phone字段的表
        print("=" * 80)
        print("查找包含手机号的表...")
        print("=" * 80)
        
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        phone_tables = []
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = [row[0] for row in cursor.fetchall()]
            if 'phone' in columns:
                phone_tables.append(table)
        
        print(f"\n找到 {len(phone_tables)} 个包含phone字段的表:")
        for table in phone_tables:
            print(f"  - {table}")
        
        # 2. 统计需要修改的记录数
        total_count = 0
        for table in phone_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE phone IS NOT NULL AND phone != ''")
            count = cursor.fetchone()[0]
            total_count += count
            print(f"\n{table}: {count} 条记录")
        
        print(f"\n总计: {total_count} 条记录需要混淆")
        
        # 3. 确认操作
        print("\n" + "=" * 80)
        print("⚠️  警告: 此操作将修改所有手机号，无法恢复！")
        print("=" * 80)
        confirm = input("\n确认执行? (输入 YES 继续): ")
        
        if confirm != "YES":
            print("❌ 操作已取消")
            return
        
        # 4. 执行混淆
        print("\n开始混淆手机号...")
        updated_count = 0
        
        for table in phone_tables:
            print(f"\n处理表: {table}")
            
            # 获取所有手机号
            cursor.execute(f"SELECT id, phone FROM {table} WHERE phone IS NOT NULL AND phone != ''")
            rows = cursor.fetchall()
            
            for row_id, phone in rows:
                if not phone or len(phone) != 11:
                    continue
                
                try:
                    # 转换为数字
                    phone_num = int(phone)
                    
                    # 随机加减1-1000
                    offset = random.randint(-1000, 1000)
                    new_phone_num = phone_num + offset
                    
                    # 确保是11位
                    new_phone = str(new_phone_num).zfill(11)
                    if len(new_phone) > 11:
                        new_phone = new_phone[:11]
                    
                    # 更新数据库
                    cursor.execute(f"UPDATE {table} SET phone = %s WHERE id = %s", (new_phone, row_id))
                    updated_count += 1
                    
                    if updated_count % 10 == 0:
                        print(f"  已处理 {updated_count} 条...")
                
                except ValueError:
                    print(f"  跳过非数字手机号: {phone}")
                    continue
        
        # 5. 提交事务
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ 混淆完成！共修改 {updated_count} 条手机号")
        print("=" * 80)
        
        # 6. 验证结果
        print("\n验证结果（显示前5条）:")
        for table in phone_tables[:3]:
            cursor.execute(f"SELECT id, phone FROM {table} WHERE phone IS NOT NULL LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                print(f"\n{table}:")
                for row_id, phone in rows:
                    print(f"  ID {row_id}: {phone}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    randomize_phones()
