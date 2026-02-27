# -*- coding: utf-8 -*-
"""
检查所有 experience_improve 字典项的 label 是否正确
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
print("检查所有 experience_improve 字典项的 label")
print("=" * 120)

# 用户提供的正确标签列表
correct_labels = [
    "预约诊疗服务更加便捷",
    "门诊就诊流程更加优化",
    "患者住院体验更加舒适",
    "院后医疗服务更加连续",
    "院前院内衔接更加高效",
    "舒心就医环境更加温馨",
    "互联网诊疗更加可及",
    "其他（非相关主题）"
]

print(f"\n用户提供的正确标签（共 {len(correct_labels)} 个）:")
for i, label in enumerate(correct_labels, 1):
    print(f"  {i}. {label}")

# 查询数据库中所有 experience_improve 类型的字典项
cursor.execute("""
    SELECT id, code, label
    FROM dictionary_items
    WHERE type = 'experience_improve'
    ORDER BY id
""")

db_items = cursor.fetchall()

print(f"\n{'=' * 120}")
print(f"数据库中的 experience_improve 字典项（共 {len(db_items)} 个）:")
print(f"{'=' * 120}")

print(f"\n{'ID':<6} {'Code':<45} {'当前Label':<40} {'状态'}")
print(f"{'-' * 120}")

error_count = 0
correct_count = 0

for item in db_items:
    item_id = item['id']
    code = item['code']
    label = item['label']
    
    # 检查 label 是否在正确列表中
    if label in correct_labels:
        status = "OK"
        correct_count += 1
    else:
        status = "ERROR"
        error_count += 1
    
    print(f"{item_id:<6} {code:<45} {label:<40} {status}")

print(f"\n{'=' * 120}")
print(f"统计:")
print(f"{'=' * 120}")
print(f"  总数: {len(db_items)}")
print(f"  正确: {correct_count}")
print(f"  错误: {error_count}")

# 检查哪些正确的标签在数据库中缺失
print(f"\n{'=' * 120}")
print(f"检查是否有正确标签在数据库中缺失:")
print(f"{'=' * 120}")

db_labels = [item['label'] for item in db_items]
missing_labels = [label for label in correct_labels if label not in db_labels]

if missing_labels:
    print(f"\n  缺失的标签 (共 {len(missing_labels)} 个):")
    for label in missing_labels:
        print(f"    - {label}")
else:
    print(f"\n  [OK] 所有正确标签都在数据库中")

# 检查哪些数据库中的标签是多余的/错误的
print(f"\n{'=' * 120}")
print(f"检查数据库中哪些标签是错误的:")
print(f"{'=' * 120}")

wrong_items = [item for item in db_items if item['label'] not in correct_labels]

if wrong_items:
    print(f"\n  错误的字典项 (共 {len(wrong_items)} 个):")
    for item in wrong_items:
        print(f"    - ID={item['id']}, code={item['code']}, label={item['label']}")
        
        # 查询有多少记录在使用这个 code
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM activity_infos
            WHERE experience_improve_code = %s
        """, (item['code'],))
        
        usage_count = cursor.fetchone()['count']
        print(f"      使用次数: {usage_count}")
else:
    print(f"\n  [OK] 所有字典项的标签都正确")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print(f"问题总结:")
print(f"{'=' * 120}")

if error_count > 0:
    print(f"\n  发现 {error_count} 个字典项的 label 不正确，需要修复。")
    print(f"\n  建议修复方案:")
    print(f"    1. 对于 'experience_improve_20260205144626' 这样的错误 code，应该删除")
    print(f"    2. 对于其他 label 不正确但 code 合理的项，应该更新 label")
    print(f"    3. 更新前需要先确认每个 code 应该对应哪个正确的 label")
else:
    print(f"\n  [OK] 所有字典项的 label 都正确！")

print(f"\n{'=' * 120}")
