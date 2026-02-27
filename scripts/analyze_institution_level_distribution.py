# -*- coding: utf-8 -*-
"""
分析书审分组&面谈分组中机构等级的数据分布
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

print("=" * 120)
print("书审分组&面谈分组 - 机构等级数据分析")
print("=" * 120)

# 1. 数据源头：const_init_institutions 表
print("\n[数据源头] const_init_institutions 表的 level 字段")
print("-" * 120)

cursor.execute("""
    SELECT 
        level,
        COUNT(*) as count
    FROM const_init_institutions
    GROUP BY level
    ORDER BY count DESC
""")

source_levels = cursor.fetchall()

print(f"\n  const_init_institutions 表中 level 字段的分布:")
print(f"  {'等级':<30} {'数量':<10} {'占比'}")
print(f"  {'-' * 80}")

total_institutions = sum(item['count'] for item in source_levels)

for item in source_levels:
    level = item['level'] if item['level'] else '(空值)'
    count = item['count']
    percentage = (count / total_institutions * 100) if total_institutions > 0 else 0
    print(f"  {level:<30} {count:<10} {percentage:.2f}%")

print(f"\n  总计: {total_institutions} 个机构")

# 2. 实际使用情况：registrations 表关联的机构等级
print(f"\n{'=' * 120}")
print("[实际使用] registrations 表中使用的机构等级分布")
print("-" * 120)

cursor.execute("""
    SELECT 
        i.level,
        COUNT(*) as count
    FROM registrations r
    JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.competition_id = 1
    GROUP BY i.level
    ORDER BY count DESC
""")

used_levels = cursor.fetchall()

print(f"\n  registrations 表中实际使用的机构等级:")
print(f"  {'等级':<30} {'数量':<10} {'占比'}")
print(f"  {'-' * 80}")

total_registrations = sum(item['count'] for item in used_levels)

for item in used_levels:
    level = item['level'] if item['level'] else '(空值)'
    count = item['count']
    percentage = (count / total_registrations * 100) if total_registrations > 0 else 0
    print(f"  {level:<30} {count:<10} {percentage:.2f}%")

print(f"\n  总计: {total_registrations} 个报名记录")

# 3. 书审分组列表（已提交状态）
print(f"\n{'=' * 120}")
print("[书审分组列表] 已提交状态的报名记录机构等级分布")
print("-" * 120)

cursor.execute("""
    SELECT 
        i.level,
        COUNT(*) as count
    FROM registrations r
    JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.competition_id = 1
    AND r.status = 'SUBMITTED'
    GROUP BY i.level
    ORDER BY count DESC
""")

submitted_levels = cursor.fetchall()

print(f"\n  书审分组列表中的机构等级:")
print(f"  {'等级':<30} {'数量':<10} {'占比'}")
print(f"  {'-' * 80}")

total_submitted = sum(item['count'] for item in submitted_levels)

for item in submitted_levels:
    level = item['level'] if item['level'] else '(空值)'
    count = item['count']
    percentage = (count / total_submitted * 100) if total_submitted > 0 else 0
    print(f"  {level:<30} {count:<10} {percentage:.2f}%")

print(f"\n  总计: {total_submitted} 个已提交报名")

# 4. 面谈分组列表（进阶组且已提交）
print(f"\n{'=' * 120}")
print("[面谈分组列表] 进阶组已提交状态的报名记录机构等级分布")
print("-" * 120)

cursor.execute("""
    SELECT 
        i.level,
        COUNT(*) as count
    FROM registrations r
    JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.competition_id = 1
    AND r.status = 'SUBMITTED'
    AND r.group_type = 'ADVANCED'
    GROUP BY i.level
    ORDER BY count DESC
""")

interview_levels = cursor.fetchall()

print(f"\n  面谈分组列表中的机构等级:")
print(f"  {'等级':<30} {'数量':<10} {'占比'}")
print(f"  {'-' * 80}")

total_interview = sum(item['count'] for item in interview_levels)

for item in interview_levels:
    level = item['level'] if item['level'] else '(空值)'
    count = item['count']
    percentage = (count / total_interview * 100) if total_interview > 0 else 0
    print(f"  {level:<30} {count:<10} {percentage:.2f}%")

print(f"\n  总计: {total_interview} 个面谈分组报名")

# 5. 特别关注：三级医院的统计
print(f"\n{'=' * 120}")
print("[特别关注] 三级医院（三甲）的详细统计")
print("-" * 120)

# 查找所有包含"三级"的等级
cursor.execute("""
    SELECT level, COUNT(*) as count
    FROM const_init_institutions
    WHERE level LIKE '%三级%' OR level LIKE '%三甲%'
    GROUP BY level
    ORDER BY count DESC
""")

sanjia_types = cursor.fetchall()

print(f"\n  const_init_institutions 表中的三级医院类型:")
for item in sanjia_types:
    print(f"    - {item['level']}: {item['count']} 个")

# 在报名中的三级医院
cursor.execute("""
    SELECT 
        i.level,
        COUNT(*) as count
    FROM registrations r
    JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.competition_id = 1
    AND (i.level LIKE '%三级%' OR i.level LIKE '%三甲%')
    GROUP BY i.level
    ORDER BY count DESC
""")

sanjia_in_registrations = cursor.fetchall()

print(f"\n  registrations 表中的三级医院:")
for item in sanjia_in_registrations:
    print(f"    - {item['level']}: {item['count']} 个报名")

# 6. 空值统计
print(f"\n{'=' * 120}")
print("[空值统计]")
print("-" * 120)

# 源表空值
cursor.execute("""
    SELECT COUNT(*) as count
    FROM const_init_institutions
    WHERE level IS NULL OR level = ''
""")
null_in_source = cursor.fetchone()['count']

# 报名表空值
cursor.execute("""
    SELECT COUNT(*) as count
    FROM registrations r
    JOIN const_init_institutions i ON r.institution_id = i.id
    WHERE r.competition_id = 1
    AND (i.level IS NULL OR i.level = '')
""")
null_in_registrations = cursor.fetchone()['count']

print(f"\n  空值统计:")
print(f"    - const_init_institutions 表: {null_in_source} 个机构 level 为空")
print(f"    - registrations 表（所有报名）: {null_in_registrations} 个报名的机构 level 为空")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[总结]")
print("=" * 120)

print(f"\n  数据源头:")
print(f"    - 表名: const_init_institutions")
print(f"    - 字段: level")
print(f"    - SQL路径: registrations.institution_id -> const_init_institutions.id -> const_init_institutions.level")

print(f"\n  API接口:")
print(f"    - 书审分组: GET /api/admin/registrations/filter")
print(f"    - 面谈分组: GET /api/admin/registrations/interview-groups")
print(f"    - DTO字段: RegistrationFilterItem.institutionLevel / GroupedRegistrationItem.institutionLevel")

print(f"\n  数据质量:")
print(f"    - 源表总数: {total_institutions} 个机构")
print(f"    - 空值数量: {null_in_source} 个")
print(f"    - 报名使用: {total_registrations} 个")
print(f"    - 空值报名: {null_in_registrations} 个")

print(f"\n{'=' * 120}")
