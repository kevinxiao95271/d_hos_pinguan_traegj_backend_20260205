# -*- coding: utf-8 -*-
"""
检查机构分布情况
"""
import pymysql

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
print("机构分布情况检查")
print("=" * 100)

# 1. 统计每个机构的项目数
print("\n[1] 机构项目数分布 (Top 20):")
cursor.execute("""
    SELECT 
        i.name,
        i.level,
        COUNT(r.id) as project_count
    FROM registrations r
    JOIN institutions i ON r.institution_id = i.id
    GROUP BY i.id, i.name, i.level
    ORDER BY project_count DESC
    LIMIT 20
""")

results = cursor.fetchall()
for idx, (name, level, count) in enumerate(results, 1):
    level_str = level if level else "未定级"
    print(f"  {idx:>2}. {name:<50} [{level_str:<10}] {count:>3} 个项目")

# 2. 统计机构等级分布
print(f"\n[2] 机构等级分布:")
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
for level, inst_count, proj_count in level_stats:
    percentage = proj_count / total_projects * 100 if total_projects > 0 else 0
    print(f"  {level:<15} {inst_count:>3} 家机构 / {proj_count:>3} 个项目 ({percentage:>5.1f}%)")

# 3. 统计项目数分布
print(f"\n[3] 项目数分布统计:")
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
for proj_count, inst_count in dist_stats:
    print(f"  {proj_count:>3} 个项目: {inst_count:>3} 家机构")

# 4. 总体统计
cursor.execute("SELECT COUNT(DISTINCT institution_id) FROM registrations")
total_institutions = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM registrations")
total_registrations = cursor.fetchone()[0]

print(f"\n[4] 总体情况:")
print(f"  参与机构总数: {total_institutions}")
print(f"  报名项目总数: {total_registrations}")
print(f"  平均每家机构: {total_registrations / total_institutions:.2f} 个项目")

cursor.close()
conn.close()

print("\n" + "=" * 100)
