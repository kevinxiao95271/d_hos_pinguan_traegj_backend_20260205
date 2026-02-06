#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新评委数据为真实的中文名字和职称"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 真实的评委数据
REVIEWERS = [
    # ID, 姓名, 职称, 专家背景, 初审组, 终审组
    (3, '13800000002', '王建国', '主任医师', 'MEDICAL', 'A1', 'A1'),
    (6, '13800000021', '李明华', '主任医师', 'MEDICAL', 'A1', 'A1'),
    (7, '13800000022', '张秀英', '护理部主任', 'NURSING', 'A1', 'A1'),
    (14, '13800002001', '陈卫东', '副主任医师', 'MEDICAL', 'A1', 'A1'),
    (15, '13800002002', '刘芳', '主任护师', 'NURSING', 'A1', 'A1'),
    (16, '13800002003', '赵志强', '主任医师', 'MEDICAL', 'A1', 'A1'),
    (17, '13800002004', '孙丽娟', '副主任护师', 'NURSING', 'A1', 'A1'),
    (18, '13800002005', '周建平', '主任医师', 'MEDICAL', 'B2', 'B2'),
    (19, '13800002006', '吴晓明', '院长助理', 'MANAGEMENT', 'B2', 'B2'),
    (20, '13800002007', '郑海波', '副主任医师', 'MEDICAL', 'B2', 'B2'),
    (21, '13800002008', '马丽华', '护理部副主任', 'NURSING', 'B2', 'B2'),
    (22, '13800002009', '黄文龙', '主任医师', 'MEDICAL', 'B2', 'B2'),
    (23, '13800002010', '徐静', '主任护师', 'NURSING', 'B2', 'B2'),
    (24, '13800002011', '林建新', '医务科主任', 'MANAGEMENT', 'B1', 'B1'),
    (25, '13800002012', '钱志远', '副主任医师', 'MEDICAL', None, None),
    (63, '13799990001', '何晓东', '质控科主任', 'MANAGEMENT', None, None),
]

print("="*60)
print("更新评委数据为真实姓名和职称")
print("="*60)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    for reviewer_id, phone, name, title, bg, r_group, i_group in REVIEWERS:
        sql = """
            UPDATE user_accounts 
            SET name = %s, title = %s, expert_background = %s,
                reviewer_group_code = %s, interview_group_code = %s
            WHERE id = %s
        """
        cursor.execute(sql, (name, title, bg, r_group, i_group, reviewer_id))
        print(f"更新评委 ID={reviewer_id}: {name} - {title} ({bg})")
    
    conn.commit()
    print(f"\n成功更新 {len(REVIEWERS)} 位评委数据")
    
    # 统计
    print("\n专家背景分布:")
    cursor.execute("""
        SELECT expert_background, COUNT(*) 
        FROM user_accounts 
        WHERE role='REVIEWER' 
        GROUP BY expert_background
    """)
    for bg, cnt in cursor.fetchall():
        bg_name = {'MEDICAL': '医疗', 'NURSING': '护理', 'MANAGEMENT': '管理'}.get(bg, '未设置')
        print(f"  {bg_name}: {cnt}人")
    
    print("\n初审分组分布:")
    cursor.execute("""
        SELECT reviewer_group_code, COUNT(*) 
        FROM user_accounts 
        WHERE role='REVIEWER' 
        GROUP BY reviewer_group_code
    """)
    for group, cnt in cursor.fetchall():
        print(f"  {group or '未分组'}: {cnt}人")
    
except Exception as e:
    print(f"错误: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()

print("\n" + "="*60)
print("完成！重新获取评委列表即可看到更新后的数据")
print("="*60)
