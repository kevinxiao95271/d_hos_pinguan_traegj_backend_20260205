# -*- coding: utf-8 -*-
"""
检查评审专家的机构分配情况
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
print("评审专家机构分配检查")
print("=" * 100)

# 1. 统计评审专家数量
print("\n[1] 评审专家统计:")
cursor.execute("""
    SELECT COUNT(*) 
    FROM user_accounts 
    WHERE role = 'REVIEWER'
""")
total_reviewers = cursor.fetchone()[0]
print(f"  评审专家总数: {total_reviewers}")

# 2. 检查评审专家的机构分配
print("\n[2] 评审专家机构分配情况:")
cursor.execute("""
    SELECT 
        u.id,
        u.name,
        u.phone,
        u.institution_id,
        i.name as institution_name,
        i.level as institution_level
    FROM user_accounts u
    LEFT JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.id
""")

reviewers = cursor.fetchall()

has_institution = 0
no_institution = 0
sanjia_count = 0
non_sanjia_count = 0

print(f"\n  评审专家详情:")
for id, name, phone, inst_id, inst_name, inst_level in reviewers:
    if inst_id:
        has_institution += 1
        level_str = inst_level if inst_level else "未定级"
        if inst_level == '三甲':
            sanjia_count += 1
            status = "[OK]"
        else:
            non_sanjia_count += 1
            status = "[需修正]"
        print(f"    {status} [{id:>3}] {name:<20} | {phone:<15} | {inst_name[:40]:<40} | {level_str}")
    else:
        no_institution += 1
        print(f"    [需修正] [{id:>3}] {name:<20} | {phone:<15} | 无机构")

print(f"\n[3] 统计:")
print(f"  有机构: {has_institution} 人")
print(f"  无机构: {no_institution} 人")
if has_institution > 0:
    print(f"  三甲医院: {sanjia_count} 人 ({sanjia_count/has_institution*100:.1f}%)")
    print(f"  非三甲: {non_sanjia_count} 人 ({non_sanjia_count/has_institution*100:.1f}%)")

# 4. 获取可用的三甲医院
cursor.execute("""
    SELECT COUNT(*) 
    FROM institutions 
    WHERE level = '三甲'
""")
sanjia_hospitals = cursor.fetchone()[0]
print(f"\n[4] 可用三甲医院: {sanjia_hospitals} 家")

cursor.close()
conn.close()

print("\n" + "=" * 100)
