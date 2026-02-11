#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""混淆数据库中的所有手机号（自动执行）"""

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
        
        # 3. 备份原始数据
        print("\n备份原始手机号...")
        backup_data = {}
        for table in phone_tables:
            cursor.execute(f"SELECT id, phone FROM {table} WHERE phone IS NOT NULL AND phone != ''")
            backup_data[table] = cursor.fetchall()
        print(f"✅ 已备份 {sum(len(v) for v in backup_data.values())} 条记录")
        
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
                    if offset == 0:  # 确保一定有变化
                        offset = random.choice([-500, 500])
                    
                    new_phone_num = phone_num + offset
                    
                    # 确保是11位且以1开头
                    new_phone = str(abs(new_phone_num)).zfill(11)
                    if len(new_phone) > 11:
                        new_phone = new_phone[:11]
                    if not new_phone.startswith('1'):
                        new_phone = '1' + new_phone[1:]
                    
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
        
        # 6. 验证结果（对比前后）
        print("\n验证结果（显示前10条对比）:")
        for table in phone_tables:
            print(f"\n{table}:")
            cursor.execute(f"SELECT id, phone FROM {table} WHERE phone IS NOT NULL LIMIT 10")
            new_rows = cursor.fetchall()
            
            # 找到对应的原始数据
            old_dict = {row[0]: row[1] for row in backup_data.get(table, [])}
            
            print(f"  {'ID':<5} {'原手机号':<15} {'新手机号':<15} {'变化':<10}")
            print(f"  {'-'*5} {'-'*15} {'-'*15} {'-'*10}")
            
            for row_id, new_phone in new_rows[:10]:
                old_phone = old_dict.get(row_id, 'N/A')
                if old_phone != 'N/A':
                    try:
                        diff = int(new_phone) - int(old_phone)
                        print(f"  {row_id:<5} {old_phone:<15} {new_phone:<15} {diff:+d}")
                    except:
                        print(f"  {row_id:<5} {old_phone:<15} {new_phone:<15} N/A")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    randomize_phones()
