# -*- coding: utf-8 -*-
"""
重新分配报名机构，确保：
1. 使用三甲医院为主
2. 大部分机构只有1个项目
3. 少数机构有2-3个项目
4. 未定级机构占比<5%
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
print("重新分配报名机构")
print("=" * 100)

# 1. 获取所有三甲医院和二甲医院
print("\n[1] 获取三甲和二甲医院...")
cursor.execute("""
    SELECT id, name, level, region 
    FROM institutions 
    WHERE level IN ('三甲', '二甲')
    ORDER BY FIELD(level, '三甲', '二甲'), name
""")
high_level_hospitals = cursor.fetchall()
print(f"  三甲/二甲医院: {len(high_level_hospitals)} 家")

# 分类统计
cursor.execute("SELECT COUNT(*) FROM institutions WHERE level = '三甲'")
sanjia_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM institutions WHERE level = '二甲'")
erjia_count = cursor.fetchone()[0]
print(f"    三甲医院: {sanjia_count} 家")
print(f"    二甲医院: {erjia_count} 家")

# 2. 获取少量未定级机构（不超过5%）
cursor.execute("""
    SELECT id, name, level, region 
    FROM institutions 
    WHERE level IS NULL OR level = '' OR level NOT IN ('三甲', '二甲', '一甲')
    ORDER BY RAND()
    LIMIT 10
""")
ungraded_hospitals = cursor.fetchall()
print(f"  未定级机构: {len(ungraded_hospitals)} 家")

# 3. 获取所有报名记录
cursor.execute("SELECT id FROM registrations ORDER BY id")
registration_ids = [row[0] for row in cursor.fetchall()]
total_registrations = len(registration_ids)
print(f"\n[2] 总报名数: {total_registrations}")

# 4. 计算机构分配策略
# 目标：100家机构左右，大部分1个项目，少数2-3个
target_institutions = min(100, len(high_level_hospitals))
print(f"  目标机构数: {target_institutions}")

# 分配策略：
# - 70%的机构只有1个项目 (70家 = 70个项目)
# - 20%的机构有2个项目 (20家 = 40个项目)
# - 10%的机构有3个项目 (10家 = 30个项目)
# 总计：100家机构，140个项目（127个实际项目需要调整比例）

one_project_count = int(total_registrations * 0.70)  # 70%机构只有1个项目
two_project_count = int((total_registrations - one_project_count) * 0.67)  # 约20家*2
three_project_count = total_registrations - one_project_count - two_project_count  # 剩余

one_project_institutions = one_project_count  # 70家
two_project_institutions = two_project_count // 2  # 约20家
three_project_institutions = three_project_count // 3  # 约10家

print(f"\n[3] 分配策略:")
print(f"  1个项目: {one_project_institutions} 家机构 (共{one_project_count}个项目)")
print(f"  2个项目: {two_project_institutions} 家机构 (共{two_project_count}个项目)")
print(f"  3个项目: {three_project_institutions} 家机构 (共{three_project_count}个项目)")
print(f"  总计: {one_project_institutions + two_project_institutions + three_project_institutions} 家机构")

# 5. 随机选择机构
high_level_hospitals = list(high_level_hospitals)  # 转换为list
random.shuffle(high_level_hospitals)
selected_institutions = []

# 优先使用三甲医院（占95%）
target_sanjia = int((one_project_institutions + two_project_institutions + three_project_institutions) * 0.95)
sanjia_hospitals = [h for h in high_level_hospitals if h[2] == '三甲']
erjia_hospitals = [h for h in high_level_hospitals if h[2] == '二甲']

# 分配三甲医院
for i in range(min(target_sanjia, len(sanjia_hospitals))):
    selected_institutions.append(sanjia_hospitals[i])

# 补充二甲医院
remaining = (one_project_institutions + two_project_institutions + three_project_institutions) - len(selected_institutions)
for i in range(min(remaining - len(ungraded_hospitals), len(erjia_hospitals))):
    selected_institutions.append(erjia_hospitals[i])

# 补充少量未定级（不超过5%）
ungraded_quota = int(len(selected_institutions) * 0.05)
for i in range(min(ungraded_quota, len(ungraded_hospitals))):
    selected_institutions.append(ungraded_hospitals[i])

print(f"\n[4] 实际选择机构:")
print(f"  三甲医院: {len([h for h in selected_institutions if h[2] == '三甲'])} 家")
print(f"  二甲医院: {len([h for h in selected_institutions if h[2] == '二甲'])} 家")
print(f"  未定级: {len([h for h in selected_institutions if not h[2] or h[2] not in ['三甲', '二甲']])} 家")
print(f"  总计: {len(selected_institutions)} 家")

# 6. 创建分配方案
institution_allocation = []

# 1个项目的机构
for i in range(one_project_institutions):
    if i < len(selected_institutions):
        institution_allocation.append((selected_institutions[i][0], 1))

# 2个项目的机构
for i in range(two_project_institutions):
    idx = one_project_institutions + i
    if idx < len(selected_institutions):
        institution_allocation.append((selected_institutions[idx][0], 2))

# 3个项目的机构
for i in range(three_project_institutions):
    idx = one_project_institutions + two_project_institutions + i
    if idx < len(selected_institutions):
        institution_allocation.append((selected_institutions[idx][0], 3))

# 7. 执行分配
print(f"\n[5] 开始分配报名到机构...")
random.shuffle(registration_ids)  # 打乱报名顺序
registration_index = 0
updated_count = 0

for institution_id, project_count in institution_allocation:
    for _ in range(project_count):
        if registration_index < len(registration_ids):
            reg_id = registration_ids[registration_index]
            try:
                cursor.execute("""
                    UPDATE registrations 
                    SET institution_id = %s 
                    WHERE id = %s
                """, (institution_id, reg_id))
                updated_count += 1
                registration_index += 1
            except Exception as e:
                print(f"  更新失败 [报名ID: {reg_id}]: {str(e)[:60]}")
                conn.rollback()

conn.commit()

print(f"  更新完成: {updated_count}/{total_registrations}")

# 8. 验证结果
print(f"\n[6] 验证分配结果...")

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
total_projects = sum([row[2] for row in level_stats])
print(f"\n  机构等级分布:")
for level, inst_count, proj_count in level_stats:
    percentage = proj_count / total_projects * 100 if total_projects > 0 else 0
    print(f"    {level:<15} {inst_count:>3} 家机构 / {proj_count:>3} 个项目 ({percentage:>5.1f}%)")

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
    print(f"    {proj_count} 个项目: {inst_count} 家机构")

cursor.execute("SELECT COUNT(DISTINCT institution_id) FROM registrations")
final_institution_count = cursor.fetchone()[0]
print(f"\n  最终参与机构数: {final_institution_count}")
print(f"  平均每家机构: {total_registrations / final_institution_count:.2f} 个项目")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("机构重新分配完成！")
print("=" * 100)
