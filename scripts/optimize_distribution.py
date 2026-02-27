# -*- coding: utf-8 -*-
"""
优化机构分布：
1. 将未定级机构的项目转移到三甲医院（确保未定级<5%）
2. 将超过3个项目的机构的项目分散（确保每家最多3个）
"""
import pymysql
import random

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

print("=" * 100)
print("优化机构分布")
print("=" * 100)

# 1. 检查当前状态
cursor.execute("SELECT COUNT(*) FROM registrations")
total_registrations = cursor.fetchone()[0]

# 计算未定级的目标上限（5%）
ungraded_max = int(total_registrations * 0.05)
print(f"\n[1] 当前状态:")
print(f"  总项目数: {total_registrations}")
print(f"  未定级项目上限(5%): {ungraded_max}")

# 2. 处理未定级机构的项目
print(f"\n[2] 处理未定级机构...")

# 获取未定级机构的项目
cursor.execute("""
    SELECT r.id, r.institution_id, i.name
    FROM registrations r
    JOIN institutions i ON r.institution_id = i.id
    WHERE i.level IS NULL OR i.level = '' OR i.level NOT IN ('三甲', '二甲')
    ORDER BY RAND()
""")
ungraded_registrations = cursor.fetchall()
current_ungraded = len(ungraded_registrations)

print(f"  当前未定级项目: {current_ungraded} 个 ({current_ungraded/total_registrations*100:.1f}%)")
print(f"  需要转移: {max(0, current_ungraded - ungraded_max)} 个")

# 获取只有1个项目的三甲医院
cursor.execute("""
    SELECT i.id, i.name, COUNT(r.id) as project_count
    FROM institutions i
    LEFT JOIN registrations r ON i.id = r.institution_id
    WHERE i.level = '三甲'
    GROUP BY i.id, i.name
    HAVING project_count <= 1
    ORDER BY project_count, RAND()
    LIMIT 50
""")
target_sanjia = list(cursor.fetchall())

print(f"  可用的三甲医院(≤1个项目): {len(target_sanjia)} 家")

# 转移多余的未定级项目到三甲医院
moved_count = 0
for i in range(min(current_ungraded - ungraded_max, len(target_sanjia))):
    if i < len(ungraded_registrations) and i < len(target_sanjia):
        reg_id = ungraded_registrations[i][0]
        target_inst_id = target_sanjia[i][0]
        
        try:
            cursor.execute("""
                UPDATE registrations 
                SET institution_id = %s 
                WHERE id = %s
            """, (target_inst_id, reg_id))
            moved_count += 1
        except Exception as e:
            print(f"  转移失败: {str(e)[:60]}")
            conn.rollback()

conn.commit()
print(f"  已转移: {moved_count} 个项目到三甲医院")

# 3. 处理超过3个项目的机构
print(f"\n[3] 处理项目过多的机构...")

cursor.execute("""
    SELECT i.id, i.name, i.level, COUNT(r.id) as project_count
    FROM institutions i
    JOIN registrations r ON i.id = r.institution_id
    GROUP BY i.id, i.name, i.level
    HAVING project_count > 3
    ORDER BY project_count DESC
""")
over_limit_institutions = cursor.fetchall()

print(f"  超过3个项目的机构: {len(over_limit_institutions)} 家")

for inst_id, inst_name, inst_level, proj_count in over_limit_institutions:
    excess = proj_count - 3
    print(f"  {inst_name[:40]:<40} {proj_count} 个项目，需转移 {excess} 个")
    
    # 获取该机构的项目
    cursor.execute("""
        SELECT id FROM registrations 
        WHERE institution_id = %s 
        ORDER BY RAND()
        LIMIT %s
    """, (inst_id, excess))
    
    registrations_to_move = [row[0] for row in cursor.fetchall()]
    
    # 获取只有1个项目的三甲医院
    cursor.execute("""
        SELECT i.id
        FROM institutions i
        LEFT JOIN registrations r ON i.id = r.institution_id
        WHERE i.level = '三甲'
        GROUP BY i.id
        HAVING COUNT(r.id) <= 1
        ORDER BY RAND()
        LIMIT %s
    """, (excess,))
    
    target_institutions = [row[0] for row in cursor.fetchall()]
    
    # 逐个转移
    for reg_id, target_inst_id in zip(registrations_to_move, target_institutions):
        try:
            cursor.execute("""
                UPDATE registrations 
                SET institution_id = %s 
                WHERE id = %s
            """, (target_inst_id, reg_id))
        except Exception as e:
            print(f"    转移失败: {str(e)[:60]}")
            conn.rollback()

conn.commit()

# 4. 验证最终结果
print(f"\n[4] 最终验证...")

cursor.execute("""
    SELECT 
        COALESCE(i.level, '未定级') as level,
        COUNT(DISTINCT i.id) as institution_count,
        COUNT(r.id) as project_count
    FROM registrations r
    JOIN institutions i ON r.institution_id = i.id
    GROUP BY COALESCE(i.level, '未定级')
    ORDER BY project_count DESC
""")

level_stats = cursor.fetchall()
print(f"\n  机构等级分布:")
for level, inst_count, proj_count in level_stats:
    percentage = proj_count / total_registrations * 100
    status = "[OK]" if (level != '未定级' or percentage <= 5.0) else "[超标]"
    print(f"    {status} {level:<15} {inst_count:>3} 家机构 / {proj_count:>3} 个项目 ({percentage:>5.1f}%)")

cursor.execute("""
    SELECT 
        project_count,
        COUNT(*) as institution_count
    FROM (
        SELECT 
            institution_id,
            COUNT(*) as project_count
        FROM registrations
        GROUP BY institution_id
    ) as t
    GROUP BY project_count
    ORDER BY project_count
""")

dist_stats = cursor.fetchall()
print(f"\n  项目数分布:")
for proj_count, inst_count in dist_stats:
    status = "[OK]" if proj_count <= 3 else "[超标]"
    print(f"    {status} {proj_count} 个项目: {inst_count} 家机构")

cursor.execute("SELECT COUNT(DISTINCT institution_id) FROM registrations")
final_institution_count = cursor.fetchone()[0]
print(f"\n  最终参与机构数: {final_institution_count}")
print(f"  平均每家机构: {total_registrations / final_institution_count:.2f} 个项目")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("优化完成！")
print("=" * 100)
