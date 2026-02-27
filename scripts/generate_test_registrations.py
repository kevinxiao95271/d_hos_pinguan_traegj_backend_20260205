# -*- coding: utf-8 -*-
"""
生成100+条测试报名记录，覆盖各种品管工具和主题类型
"""
import pymysql
import random
from datetime import datetime, timedelta

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
print("生成测试报名记录")
print("=" * 100)

# 1. 获取字典数据
print("\n[1] 获取字典数据...")

cursor.execute("SELECT code, label FROM dictionary_items WHERE type = 'subject_type' AND active = 1")
subject_types = cursor.fetchall()
print(f"  主题类型: {len(subject_types)} 种")

cursor.execute("SELECT code, label FROM dictionary_items WHERE type = 'method' AND active = 1")
methods = cursor.fetchall()
print(f"  品管工具/方法: {len(methods)} 种")

cursor.execute("SELECT code, label FROM dictionary_items WHERE type = 'experience_improve' AND active = 1")
experience_improves = cursor.fetchall()
print(f"  改善就医感受: {len(experience_improves)} 种")

cursor.execute("SELECT code, label FROM dictionary_items WHERE type = 'quality_topic' AND active = 1")
quality_topics = cursor.fetchall()
print(f"  医疗质量主题: {len(quality_topics)} 种")

# 2. 获取现有用户和机构
print("\n[2] 获取用户和机构...")

cursor.execute("SELECT id FROM user_accounts WHERE role = 'CONTESTANT' LIMIT 30")
contestant_ids = [row[0] for row in cursor.fetchall()]
print(f"  参赛者用户: {len(contestant_ids)} 个")

cursor.execute("SELECT id, name FROM institutions LIMIT 50")
institutions = cursor.fetchall()
print(f"  机构: {len(institutions)} 个")

# 3. 获取赛事
cursor.execute("SELECT id FROM competitions LIMIT 1")
competition_result = cursor.fetchone()
if not competition_result:
    print("  未找到赛事，无法创建报名")
    cursor.close()
    conn.close()
    exit(1)

competition_id = competition_result[0]
print(f"  赛事ID: {competition_id}")

# 4. 生成报名记录
print("\n[3] 生成报名记录...")

group_types = ['BASIC', 'COMPREHENSIVE', 'ADVANCED']
statuses = ['DRAFT', 'SUBMITTED']

target_count = 120  # 生成120条
created_count = 0
failed_count = 0

for i in range(target_count):
    try:
        # 随机选择用户和机构
        applicant_id = random.choice(contestant_ids) if contestant_ids else None
        institution_id, institution_name = random.choice(institutions) if institutions else (None, None)
        
        # 随机选择字典项
        subject_type = random.choice(subject_types)
        method = random.choice(methods)
        experience_improve = random.choice(experience_improves)
        quality_topic = random.choice(quality_topics)
        
        # 随机生成报名信息
        group_type = random.choice(group_types)
        status = random.choice(statuses)
        project_name = f"{subject_type[1]}-{method[1]}-{institution_name if institution_name else '测试机构'}-{i+1}"
        
        # 创建报名记录
        cursor.execute("""
            INSERT INTO registrations 
            (project_name, group_type, status, competition_id, applicant_id, institution_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            project_name[:100],  # 限制长度
            group_type,
            status,
            competition_id,
            applicant_id,
            institution_id,
            datetime.now() - timedelta(days=random.randint(0, 10))
        ))
        
        registration_id = cursor.lastrowid
        
        # 创建活动说明
        cursor.execute("""
            INSERT INTO activity_infos
            (registration_id, theme, keywords, subject_type_code, method_code, 
             experience_improve_code, quality_topic_code, avg_work_years, avg_age, 
             cross_department, related_to_digital_ai)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            registration_id,
            f"{subject_type[1]}主题研究",
            f"{method[1]},品管,改进",
            subject_type[0],
            method[0],
            experience_improve[0],
            quality_topic[0],
            random.randint(3, 15),
            random.randint(25, 45),
            random.choice([True, False]),
            random.choice([True, False])
        ))
        
        # 创建项目总结
        cursor.execute("""
            INSERT INTO project_summaries
            (registration_id, theme, plan, problem, action, success, discussion, operation, presentation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            registration_id,
            f"{subject_type[1]}项目总结",
            f"计划使用{method[1]}方法",
            "发现的问题描述",
            "采取的行动措施",
            "取得的成功结果",
            "讨论与分析",
            "标准化操作",
            "成果展示"
        ))
        
        conn.commit()
        created_count += 1
        
        if (i + 1) % 20 == 0:
            print(f"  已创建: {created_count} 条")
            
    except Exception as e:
        failed_count += 1
        if failed_count <= 5:
            print(f"  失败 [{i+1}]: {str(e)[:80]}")
        conn.rollback()

# 5. 统计结果
print(f"\n[4] 生成完成")
print(f"  成功: {created_count} 条")
print(f"  失败: {failed_count} 条")

# 6. 验证数据分布
print(f"\n[5] 数据分布验证...")

cursor.execute("""
    SELECT 
        ai.method_code,
        COUNT(*) as count
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    GROUP BY ai.method_code
    ORDER BY count DESC
    LIMIT 10
""")

method_stats = cursor.fetchall()
print(f"\n品管工具分布 (Top 10):")
for stat in method_stats:
    cursor.execute("SELECT label FROM dictionary_items WHERE code = %s", (stat[0],))
    label_result = cursor.fetchone()
    label = label_result[0] if label_result else stat[0]
    print(f"  {label:<30} {stat[1]:>3} 条")

cursor.execute("""
    SELECT 
        ai.subject_type_code,
        COUNT(*) as count
    FROM registrations r
    JOIN activity_infos ai ON r.id = ai.registration_id
    GROUP BY ai.subject_type_code
    ORDER BY count DESC
    LIMIT 10
""")

subject_stats = cursor.fetchall()
print(f"\n主题类型分布 (Top 10):")
for stat in subject_stats:
    cursor.execute("SELECT label FROM dictionary_items WHERE code = %s", (stat[0],))
    label_result = cursor.fetchone()
    label = label_result[0] if label_result else stat[0]
    print(f"  {label:<30} {stat[1]:>3} 条")

cursor.execute("SELECT COUNT(*) FROM registrations")
total = cursor.fetchone()[0]
print(f"\n总报名记录数: {total}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print(f"测试数据生成完成！")
print("=" * 100)
