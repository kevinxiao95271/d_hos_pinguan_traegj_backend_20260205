# -*- coding: utf-8 -*-
"""
检查字典表中是否有重复的数据
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
print("检查字典表中的重复数据")
print("=" * 120)

# 检查的类型
types_to_check = [
    ('subject_type', '主题类型'),
    ('method', '运用手法'),
    ('experience_improve', '改善就医感受'),
    ('quality_topic', '医疗质量安全主题')
]

for type_code, type_name in types_to_check:
    print(f"\n{'=' * 120}")
    print(f"[{type_name}] type = '{type_code}'")
    print("-" * 120)
    
    # 查询该类型的所有数据
    cursor.execute("""
        SELECT id, type, code, label, active
        FROM dictionary_items
        WHERE type = %s
        ORDER BY code, id
    """, (type_code,))
    
    items = cursor.fetchall()
    
    print(f"\n  总数: {len(items)} 条")
    
    # 检查是否有重复的 code
    code_map = {}
    duplicates = []
    
    for item in items:
        code = item['code']
        if code in code_map:
            duplicates.append({
                'code': code,
                'items': [code_map[code], item]
            })
        else:
            code_map[code] = item
    
    if duplicates:
        print(f"\n  [WARNING] 发现 {len(duplicates)} 个重复的 code:")
        for dup in duplicates:
            print(f"\n    Code: {dup['code']}")
            for idx, item in enumerate(dup['items'], 1):
                print(f"      记录{idx}: id={item['id']}, label={item['label']}, active={item['active']}")
    else:
        print(f"\n  [OK] 没有重复的 code")
    
    # 检查是否有重复的 label
    label_map = {}
    label_duplicates = []
    
    for item in items:
        label = item['label']
        if label in label_map:
            label_duplicates.append({
                'label': label,
                'items': [label_map[label], item]
            })
        else:
            label_map[label] = item
    
    if label_duplicates:
        print(f"\n  [WARNING] 发现 {len(label_duplicates)} 个重复的 label:")
        for dup in label_duplicates:
            print(f"\n    Label: {dup['label']}")
            for idx, item in enumerate(dup['items'], 1):
                print(f"      记录{idx}: id={item['id']}, code={item['code']}, active={item['active']}")
    else:
        print(f"\n  [OK] 没有重复的 label")
    
    # 显示所有记录
    print(f"\n  所有记录:")
    print(f"  {'ID':<6} {'Code':<45} {'Label':<50} {'Active'}")
    print(f"  {'-' * 120}")
    
    for item in items:
        active_str = '是' if item['active'] == 1 else '否'
        print(f"  {item['id']:<6} {item['code']:<45} {item['label']:<50} {active_str}")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[总结]")
print("=" * 120)

print(f"\n  如果发现重复数据，可能的原因:")
print(f"    1. 数据导入时重复插入")
print(f"    2. 有新旧两套数据（如带/不带前缀）")
print(f"    3. active 字段控制不当")

print(f"\n  处理建议:")
print(f"    1. 如果 code 重复但 label 不同 → 可能是一个废弃一个新的，删除旧的")
print(f"    2. 如果 code 和 label 都一样 → 直接删除重复记录")
print(f"    3. 如果有 active = 0 的记录 → 可能是已废弃的，确认后删除")

print(f"\n{'=' * 120}")
