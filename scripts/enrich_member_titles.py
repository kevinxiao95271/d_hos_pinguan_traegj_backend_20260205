# -*- coding: utf-8 -*-
"""
为现有报名记录添加成员信息，包含多样化的职称
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
print("为报名记录添加成员信息（职称均匀分布）")
print("=" * 100)

# 定义多样化的职称（医护常见职称）
titles = [
    '主任医师', '副主任医师', '主治医师', '住院医师',
    '主任护师', '副主任护师', '主管护师', '护师', '护士',
    '主任药师', '副主任药师', '主管药师', '药师',
    '主任技师', '副主任技师', '主管技师', '技师',
    '主任检验师', '副主任检验师', '主管检验师', '检验师',
    '主任康复师', '副主任康复师', '主管康复师', '康复师',
    '教授', '副教授', '讲师', '助教',
    '研究员', '副研究员', '助理研究员',
    '高级工程师', '工程师', '助理工程师'
]

# 成员角色
member_roles = ['PARTICIPANT', 'MENTOR', 'MENTOR', 'MENTOR']  # 1个负责人，3个辅导员/成员

# 常见姓氏和名字
surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', 
            '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '高', '罗']
given_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
               '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞']

departments = [
    '内科', '外科', '妇产科', '儿科', '急诊科', '重症医学科',
    '护理部', '药剂科', '检验科', '放射科', '病理科', '麻醉科',
    '康复医学科', '中医科', '感染科', '肿瘤科', '神经内科', '心血管内科',
    '消化内科', '呼吸内科', '内分泌科', '肾内科', '血液科',
    '骨科', '普外科', '胸外科', '泌尿外科', '神经外科', '烧伤科',
    '眼科', '耳鼻喉科', '口腔科', '皮肤科', '精神科'
]

# 1. 获取所有报名ID
print("\n[1] 获取报名列表...")
cursor.execute("SELECT id FROM registrations")
registration_ids = [row[0] for row in cursor.fetchall()]
print(f"  找到 {len(registration_ids)} 条报名记录")

# 2. 检查现有成员
cursor.execute("SELECT COUNT(*) FROM registration_members")
existing_count = cursor.fetchone()[0]
print(f"  现有成员记录: {existing_count} 条")

if existing_count > 0:
    print(f"\n是否清空现有成员数据重新生成？")
    cursor.execute("DELETE FROM registration_members")
    conn.commit()
    print(f"  已清空现有成员数据")

# 3. 为每个报名创建成员
print(f"\n[2] 生成成员数据...")
created_count = 0
title_stats = {}

for reg_id in registration_ids:
    # 为每个报名创建2-5个成员
    member_count = random.randint(2, 5)
    
    for i in range(member_count):
        # 第一个成员是负责人（PARTICIPANT），其他是辅导员（MENTOR）
        role = 'PARTICIPANT' if i == 0 else 'MENTOR'
        
        # 随机选择职称
        title = random.choice(titles)
        title_stats[title] = title_stats.get(title, 0) + (1 if role == 'PARTICIPANT' else 0)
        
        # 生成随机姓名
        name = random.choice(surnames) + random.choice(given_names)
        
        # 随机选择科室
        department = random.choice(departments)
        
        try:
            cursor.execute("""
                INSERT INTO registration_members
                (registration_id, role, name, title, department)
                VALUES (%s, %s, %s, %s, %s)
            """, (reg_id, role, name, title, department))
            
            created_count += 1
            
        except Exception as e:
            print(f"  创建成员失败 [报名ID: {reg_id}]: {str(e)[:80]}")
            conn.rollback()
            continue
    
    conn.commit()
    
    if reg_id % 20 == 0:
        print(f"  已处理: {registration_ids.index(reg_id) + 1}/{len(registration_ids)}")

print(f"\n[3] 生成完成")
print(f"  成功创建成员: {created_count} 个")

# 4. 统计项目负责人职称分布
print(f"\n[4] 项目负责人职称分布:")
sorted_titles = sorted(title_stats.items(), key=lambda x: x[1], reverse=True)
for title, count in sorted_titles[:20]:
    print(f"  {title:<20} {count:>3} 人")

# 5. 验证数据
cursor.execute("""
    SELECT COUNT(DISTINCT registration_id) 
    FROM registration_members 
    WHERE role = 'PARTICIPANT'
""")
leader_count = cursor.fetchone()[0]
print(f"\n有项目负责人的报名数: {leader_count}")

cursor.execute("SELECT COUNT(*) FROM registration_members")
total_members = cursor.fetchone()[0]
print(f"总成员数: {total_members}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print(f"成员数据生成完成！")
print("=" * 100)
