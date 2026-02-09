#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正机构地区信息"""

import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

# 需要修正的机构列表
CORRECTIONS = [
    # 省级医院（应该在杭州）
    (7, '浙江医院', '杭州'),
    (8, '浙江大学医学院附属第一医院（浙一医院）', '杭州'),
    (9, '浙江省人民医院', '杭州'),
    (11, '浙江大学医学院附属儿童医院（浙江省儿童医院）', '杭州'),
    (13, '浙江省肿瘤医院', '杭州'),
    (14, '浙江大学医学院附属口腔医院（浙江省口腔医院）', '杭州'),
    
    # 杭州市医院
    (12, '浙江省中西医结合医院（杭州市红十字会医院）', '杭州'),
    (15, '杭州市肝病研究所（西溪医院）', '杭州'),
    
    # 宁波市医院
    (16, '宁波市第一医院', '宁波'),
    (18, '宁波市医疗中心李惠利医院', '宁波'),
    
    # 温州市医院
    (19, '温州医科大学附属第二医院（温医二院）', '温州'),
    
    # 绍兴市医院
    (20, '绍兴市人民医院', '绍兴'),
    
    # 嘉兴市医院
    (21, '嘉兴市第一医院', '嘉兴'),
    
    # 湖州市医院
    (22, '湖州市中心医院', '湖州'),
    
    # 金华市医院
    (23, '金华市中心医院', '金华'),
    
    # 衢州市医院
    (24, '衢州市人民医院', '衢州'),
]

def backup_data(cursor):
    """备份数据"""
    print("=" * 80)
    print("1. 备份数据")
    print("=" * 80)
    
    try:
        # 检查备份表是否存在
        cursor.execute("SHOW TABLES LIKE 'institutions_backup_20260208'")
        if cursor.fetchone():
            print("⚠️  备份表已存在，跳过备份")
        else:
            cursor.execute("""
                CREATE TABLE institutions_backup_20260208 AS 
                SELECT * FROM institutions
            """)
            print("✅ 已创建备份表: institutions_backup_20260208")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        raise

def show_before_state(cursor):
    """显示修正前的状态"""
    print("\n" + "=" * 80)
    print("2. 修正前的状态")
    print("=" * 80)
    
    ids = [item[0] for item in CORRECTIONS]
    placeholders = ','.join(['%s'] * len(ids))
    
    cursor.execute(f"""
        SELECT id, name, region
        FROM institutions
        WHERE id IN ({placeholders})
        ORDER BY id
    """, ids)
    
    results = cursor.fetchall()
    print(f"\n{'ID':<5} {'机构名称':<50} {'当前地区':<10}")
    print("-" * 80)
    for row in results:
        print(f"{row[0]:<5} {row[1]:<50} {row[2]:<10}")

def apply_corrections(cursor, conn):
    """应用修正"""
    print("\n" + "=" * 80)
    print("3. 应用修正")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for inst_id, inst_name, correct_region in CORRECTIONS:
        try:
            cursor.execute("""
                UPDATE institutions 
                SET region = %s 
                WHERE id = %s
            """, (correct_region, inst_id))
            
            print(f"✅ ID {inst_id}: {inst_name[:40]}... → {correct_region}")
            success_count += 1
        except Exception as e:
            print(f"❌ ID {inst_id}: 修正失败 - {e}")
            fail_count += 1
    
    # 提交事务
    conn.commit()
    
    print(f"\n修正完成: 成功 {success_count} 条, 失败 {fail_count} 条")

def show_after_state(cursor):
    """显示修正后的状态"""
    print("\n" + "=" * 80)
    print("4. 修正后的状态")
    print("=" * 80)
    
    ids = [item[0] for item in CORRECTIONS]
    placeholders = ','.join(['%s'] * len(ids))
    
    cursor.execute(f"""
        SELECT id, name, region
        FROM institutions
        WHERE id IN ({placeholders})
        ORDER BY id
    """, ids)
    
    results = cursor.fetchall()
    print(f"\n{'ID':<5} {'机构名称':<50} {'修正后地区':<10}")
    print("-" * 80)
    for row in results:
        print(f"{row[0]:<5} {row[1]:<50} {row[2]:<10}")

def verify_corrections(cursor):
    """验证修正结果"""
    print("\n" + "=" * 80)
    print("5. 验证修正结果")
    print("=" * 80)
    
    all_correct = True
    
    for inst_id, inst_name, expected_region in CORRECTIONS:
        cursor.execute("""
            SELECT region FROM institutions WHERE id = %s
        """, (inst_id,))
        
        result = cursor.fetchone()
        if result:
            actual_region = result[0]
            if actual_region == expected_region:
                print(f"✅ ID {inst_id}: {expected_region}")
            else:
                print(f"❌ ID {inst_id}: 期望 {expected_region}, 实际 {actual_region}")
                all_correct = False
        else:
            print(f"❌ ID {inst_id}: 未找到记录")
            all_correct = False
    
    if all_correct:
        print(f"\n✅ 所有修正都已正确应用！")
    else:
        print(f"\n⚠️  部分修正未成功，请检查")
    
    return all_correct

def show_region_distribution(cursor):
    """显示地区分布统计"""
    print("\n" + "=" * 80)
    print("6. 地区分布统计（赛事21）")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            i.region,
            COUNT(*) as count
        FROM registrations r
        LEFT JOIN institutions i ON r.institution_id = i.id
        WHERE r.competition_id = 21
        GROUP BY i.region
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    print(f"\n{'地区':<15} {'报名数':<10}")
    print("-" * 30)
    total = 0
    for row in results:
        print(f"{row[0]:<15} {row[1]:<10}")
        total += row[1]
    print("-" * 30)
    print(f"{'总计':<15} {total:<10}")

def main():
    print("=" * 80)
    print("机构地区信息修正脚本")
    print("=" * 80)
    print(f"将修正 {len(CORRECTIONS)} 个机构的地区信息")
    print()
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. 备份数据
        backup_data(cursor)
        
        # 2. 显示修正前状态
        show_before_state(cursor)
        
        # 3. 应用修正
        apply_corrections(cursor, conn)
        
        # 4. 显示修正后状态
        show_after_state(cursor)
        
        # 5. 验证修正结果
        verify_corrections(cursor)
        
        # 6. 显示地区分布
        show_region_distribution(cursor)
        
        print("\n" + "=" * 80)
        print("修正完成！")
        print("=" * 80)
        print("备份表: institutions_backup_20260208")
        print("如需回滚，执行: DROP TABLE institutions; RENAME TABLE institutions_backup_20260208 TO institutions;")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        conn.rollback()
        print("已回滚所有更改")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
