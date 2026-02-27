# -*- coding: utf-8 -*-
"""
为所有评审专家分配三甲医院，并创建更多评审专家
"""
import pymysql
import random
from datetime import datetime

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
print("为评审专家分配三甲医院")
print("=" * 100)

# 1. 获取所有三甲医院
print("\n[1] 获取三甲医院...")
cursor.execute("""
    SELECT id, name, region 
    FROM institutions 
    WHERE level = '三甲'
    ORDER BY RAND()
""")
sanjia_hospitals = list(cursor.fetchall())
print(f"  三甲医院总数: {len(sanjia_hospitals)}")

if len(sanjia_hospitals) == 0:
    print("  错误: 没有找到三甲医院！")
    cursor.close()
    conn.close()
    exit(1)

# 2. 获取现有评审专家
print("\n[2] 获取现有评审专家...")
cursor.execute("""
    SELECT id, name, phone, institution_id
    FROM user_accounts
    WHERE role = 'REVIEWER'
    ORDER BY id
""")
existing_reviewers = cursor.fetchall()
print(f"  现有评审专家: {len(existing_reviewers)} 人")

# 3. 为现有评审专家分配三甲医院
print("\n[3] 为现有评审专家分配三甲医院...")
updated_count = 0

for user_id, name, phone, current_inst_id in existing_reviewers:
    # 随机选择一个三甲医院
    inst_id, inst_name, region = random.choice(sanjia_hospitals)
    
    try:
        cursor.execute("""
            UPDATE user_accounts
            SET institution_id = %s
            WHERE id = %s
        """, (inst_id, user_id))
        
        updated_count += 1
        conn.commit()
        print(f"  [OK] {name:<20} -> {inst_name[:40]}")
        
    except Exception as e:
        print(f"  [失败] {name}: {str(e)[:60]}")
        conn.rollback()

print(f"  更新完成: {updated_count}/{len(existing_reviewers)}")

# 4. 创建更多评审专家（如果需要）
print("\n[4] 是否需要创建更多评审专家？")
target_reviewer_count = 30  # 目标：30个评审专家
need_create = target_reviewer_count - len(existing_reviewers)

if need_create > 0:
    print(f"  需要新建: {need_create} 个评审专家")
    
    # 专家姓名库
    surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', 
                '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '高', '罗',
                '郑', '梁', '谢', '宋', '唐', '许', '邓', '冯', '曹', '彭']
    given_names = ['教授', '主任', '院长', '专家', '博士', '研究员']
    
    # 专家职称
    titles = ['主任医师', '主任护师', '主任药师', '教授', '研究员', '副主任医师']
    
    # 专家背景
    backgrounds = [
        '医疗质量管理专家',
        '临床医学专家',
        '护理管理专家',
        '药学管理专家',
        '医院管理专家',
        '公共卫生专家',
        '医学教育专家',
        '医疗安全专家',
        '品质管理专家',
        'PDCA专家'
    ]
    
    created_count = 0
    failed_count = 0
    
    for i in range(need_create):
        # 生成专家信息
        surname = random.choice(surnames)
        given_name = random.choice(given_names)
        name = surname + given_name
        
        # 生成手机号（138开头 + 8位随机数）
        phone = f"138{random.randint(10000000, 99999999)}"
        
        # 随机选择职称和背景
        title = random.choice(titles)
        background = random.choice(backgrounds)
        
        # 随机选择三甲医院
        inst_id, inst_name, region = random.choice(sanjia_hospitals)
        
        # 生成密码（默认：reviewer2026）
        # 使用$2a$格式的bcrypt hash (与Java jbcrypt 0.4兼容)
        default_password_hash = '$2a$12$GY.YQo43WBXuqe5rqejb6.majZeAAmaleHTgvWIpHLyiD30J4oAe2'
        
        try:
            cursor.execute("""
                INSERT INTO user_accounts
                (phone, password, name, role, title, expert_background, institution_id, enabled, created_at)
                VALUES (%s, %s, %s, 'REVIEWER', %s, %s, %s, 1, %s)
            """, (phone, default_password_hash, name, title, background, inst_id, datetime.now()))
            
            created_count += 1
            conn.commit()
            
            if (i + 1) % 5 == 0:
                print(f"  已创建: {created_count}/{need_create}")
                
        except Exception as e:
            failed_count += 1
            if failed_count <= 3:
                print(f"  创建失败 [{name}]: {str(e)[:60]}")
            conn.rollback()
    
    print(f"\n  创建结果:")
    print(f"    成功: {created_count} 个")
    print(f"    失败: {failed_count} 个")
else:
    print(f"  当前已有 {len(existing_reviewers)} 个评审专家，无需创建")

# 5. 验证结果
print(f"\n[5] 验证结果...")
cursor.execute("""
    SELECT COUNT(*) 
    FROM user_accounts 
    WHERE role = 'REVIEWER'
""")
total_reviewers = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM user_accounts u
    JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER' AND i.level = '三甲'
""")
reviewers_in_sanjia = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM user_accounts 
    WHERE role = 'REVIEWER' AND institution_id IS NULL
""")
reviewers_no_institution = cursor.fetchone()[0]

print(f"  评审专家总数: {total_reviewers}")
print(f"  来自三甲医院: {reviewers_in_sanjia} 人 ({reviewers_in_sanjia/total_reviewers*100:.1f}%)")
print(f"  无机构: {reviewers_no_institution} 人")

if reviewers_in_sanjia == total_reviewers:
    print(f"\n  [成功] 所有评审专家都已分配到三甲医院！")
else:
    print(f"\n  [警告] 还有 {total_reviewers - reviewers_in_sanjia} 个专家未分配到三甲医院")

# 6. 显示部分评审专家
print(f"\n[6] 评审专家样例 (前10个):")
cursor.execute("""
    SELECT 
        u.name,
        u.phone,
        u.title,
        i.name as institution_name,
        i.level
    FROM user_accounts u
    JOIN institutions i ON u.institution_id = i.id
    WHERE u.role = 'REVIEWER'
    ORDER BY u.id
    LIMIT 10
""")

reviewers_sample = cursor.fetchall()
for name, phone, title, inst_name, level in reviewers_sample:
    print(f"  {name:<15} | {title:<15} | {inst_name[:35]:<35} | {level}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("评审专家机构分配完成！")
print("=" * 100)
