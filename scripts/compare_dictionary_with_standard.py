# -*- coding: utf-8 -*-
"""
对比数据库中的字典数据与标准列表
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
print("Dictionary Data Comparison - Database vs Standard")
print("=" * 120)

# 标准列表（用户提供）
standard_lists = {
    'subject_type': [
        '病人照护',
        '病历质量',
        '时间效率',
        '成本效益',
        '安全环境',
        '满意度',
        '教育训练',
        '医疗信息',
        '医疗质量与安全',
        '流程改造',
        '其他'
    ],
    'method': [
        '品管圈-问题解决',
        '品管圈-课题达成',
        '专案改善',
        '平衡计分卡',
        '根本原因分析',
        '失效模式与效应分析',
        '标杆学习',
        '5S',
        'QFD',
        '品质报告卡',
        '六西格玛管理',
        '循证医学',
        'PDCA',
        'FOCUS-PDCA',
        'TRM',
        '流程改造',
        '其他'
    ],
    'experience_improve': [
        '预约诊疗服务更加便捷',
        '门诊就诊流程更加优化',
        '患者住院体验更加舒适',
        '院后医疗服务更加连续',
        '院前院内衔接更加高效',
        '舒心就医环境更加温馨',
        '互联网诊疗更加可及',
        '其他（非相关主题）'
    ],
    'quality_topic': [
        '提高急性ST段抬高型心肌梗死再灌注治疗率',
        '提高急性脑梗死再灌注治疗率',
        '提高肿瘤治疗前临床 TNM 分期评估率',
        '降低住院患者围手术期死亡率',
        '提高静脉血栓栓塞症规范预防率',
        '提高感染性休克集束化治疗完成率',
        '提高医疗质量安全不良事件报告率',
        '提高住院患者静脉输液规范使用率',
        '提高四级手术术前多学科讨论完成率',
        '降低阴道分娩并发症发生率',
        '降低非计划重返手术室再手术率',
        '提高关键诊疗行为相关记录完整率',
        '提高医疗机构检查检验结果互认率',
        '其他'
    ]
}

type_names = {
    'subject_type': '主题类型',
    'method': '运用手法',
    'experience_improve': '改善就医感受提升患者体验',
    'quality_topic': '医疗质量安全'
}

all_match = True

for dict_type, standard_labels in standard_lists.items():
    print(f"\n{'=' * 120}")
    print(f"[{type_names[dict_type]}] ({dict_type})")
    print("=" * 120)
    
    # 从数据库查询
    cursor.execute("""
        SELECT id, code, label
        FROM dictionary_items
        WHERE type = %s AND active = 1
        ORDER BY CASE WHEN code = 'other' THEN 1 ELSE 0 END, id
    """, (dict_type,))
    
    db_items = cursor.fetchall()
    db_labels = [item['label'] for item in db_items]
    
    print(f"\n[Standard List] ({len(standard_labels)} items):")
    for i, label in enumerate(standard_labels, 1):
        print(f"  {i:2}. {label}")
    
    print(f"\n[Database List] ({len(db_labels)} items):")
    for i, item in enumerate(db_items, 1):
        print(f"  {i:2}. {item['label']:<50} (code={item['code']}, id={item['id']})")
    
    # 比对
    print(f"\n[Comparison]")
    
    # 数量比对
    if len(standard_labels) != len(db_labels):
        print(f"  [DIFF] Count mismatch: Standard={len(standard_labels)}, Database={len(db_labels)}")
        all_match = False
    else:
        print(f"  [OK] Count matches: {len(standard_labels)} items")
    
    # 内容比对
    standard_set = set(standard_labels)
    db_set = set(db_labels)
    
    # 标准中有但数据库缺失的
    missing_in_db = standard_set - db_set
    if missing_in_db:
        print(f"\n  [DIFF] Missing in Database ({len(missing_in_db)} items):")
        for label in sorted(missing_in_db):
            print(f"    - {label}")
        all_match = False
    
    # 数据库中有但标准中没有的
    extra_in_db = db_set - standard_set
    if extra_in_db:
        print(f"\n  [DIFF] Extra in Database ({len(extra_in_db)} items):")
        for label in sorted(extra_in_db):
            # 找到对应的code
            code = next((item['code'] for item in db_items if item['label'] == label), 'unknown')
            print(f"    - {label:<50} (code={code})")
        all_match = False
    
    # 完全匹配
    if not missing_in_db and not extra_in_db:
        print(f"  [OK] All labels match!")
        
        # 检查顺序
        if db_labels == standard_labels:
            print(f"  [OK] Order also matches!")
        else:
            print(f"  [INFO] Order differs (but this is fine, 'other' will be at end)")
    
    print()

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[FINAL RESULT]")
print("=" * 120)

if all_match:
    print(f"\n[SUCCESS] All dictionary types match the standard lists!")
    print(f"  - All labels are correct")
    print(f"  - No missing items")
    print(f"  - No extra items")
else:
    print(f"\n[DIFF FOUND] Some differences detected!")
    print(f"  Please review the differences above.")
    print(f"  Waiting for user confirmation before making changes.")

print(f"\n{'=' * 120}")
