# -*- coding: utf-8 -*-
"""
检查前端硬编码的 code 值在清理方案中的影响
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
print("检查前端硬编码的 code 值")
print("=" * 120)

hardcoded_codes = [
    ('other', '各字典类型的"其他"选项'),
    ('subject_type_11', '主题类型的旧版"其他"')
]

print("\n前端硬编码说明:")
print("  这些 code 用于判断是否显示'其他'的文本输入框")
print("  例如: if (code === 'other') { showOtherInput = true }")

# 1. 检查这些 code 是否存在
print(f"\n{'=' * 120}")
print("[步骤1] 检查硬编码的 code 是否存在于字典表")
print("-" * 120)

for code, description in hardcoded_codes:
    cursor.execute("""
        SELECT id, type, code, label, active
        FROM dictionary_items
        WHERE code = %s
    """, (code,))
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n  Code: '{code}' ({description})")
        print(f"  找到 {len(results)} 条记录:")
        
        for item in results:
            print(f"    - ID={item['id']}, type={item['type']}, label={item['label']}, active={item['active']}")
            
            # 查询使用次数
            field_map = {
                'subject_type': 'subject_type_code',
                'method': 'method_code',
                'experience_improve': 'experience_improve_code',
                'quality_topic': 'quality_topic_code'
            }
            
            field_name = field_map.get(item['type'])
            if field_name:
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM activity_infos
                    WHERE {field_name} = %s
                """, (code,))
                
                usage_count = cursor.fetchone()['count']
                print(f"      使用次数: {usage_count}")
    else:
        print(f"\n  Code: '{code}' ({description})")
        print(f"  [WARNING] 字典表中不存在此 code！")

# 2. 检查 subject_type_11 是否有重复
print(f"\n{'=' * 120}")
print("[步骤2] 检查 subject_type_11 是否有重复的 label")
print("-" * 120)

cursor.execute("""
    SELECT id, code, label
    FROM dictionary_items
    WHERE code = 'subject_type_11'
""")

subject_11 = cursor.fetchone()

if subject_11:
    label = subject_11['label']
    print(f"\n  subject_type_11 的 label: {label}")
    
    # 查找是否有其他 code 也有相同的 label
    cursor.execute("""
        SELECT id, code, label
        FROM dictionary_items
        WHERE type = 'subject_type'
        AND label = %s
    """, (label,))
    
    same_label_items = cursor.fetchall()
    
    if len(same_label_items) > 1:
        print(f"\n  [WARNING] 发现重复的 label '{label}':")
        for item in same_label_items:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM activity_infos
                WHERE subject_type_code = %s
            """, (item['code'],))
            
            usage_count = cursor.fetchone()['count']
            print(f"    - code={item['code']:<20}, id={item['id']}, 使用{usage_count}次")
    else:
        print(f"\n  [OK] 没有重复的 label")
else:
    print(f"\n  [WARNING] subject_type_11 不存在于字典表")

# 3. 检查所有类型的 'other'
print(f"\n{'=' * 120}")
print("[步骤3] 检查各类型的 'other' 是否有重复")
print("-" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

for dict_type in types:
    cursor.execute("""
        SELECT id, code, label
        FROM dictionary_items
        WHERE type = %s
        AND code = 'other'
    """, (dict_type,))
    
    other_item = cursor.fetchone()
    
    if other_item:
        label = other_item['label']
        
        # 查找同 label 的其他 code
        cursor.execute("""
            SELECT id, code, label
            FROM dictionary_items
            WHERE type = %s
            AND label = %s
        """, (dict_type, label))
        
        same_label_items = cursor.fetchall()
        
        if len(same_label_items) > 1:
            print(f"\n  [{dict_type}] 'other' 有重复 label '{label}':")
            for item in same_label_items:
                field_map = {
                    'subject_type': 'subject_type_code',
                    'method': 'method_code',
                    'experience_improve': 'experience_improve_code',
                    'quality_topic': 'quality_topic_code'
                }
                
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM activity_infos
                    WHERE {field_map[dict_type]} = %s
                """, (item['code'],))
                
                usage_count = cursor.fetchone()['count']
                print(f"    - code={item['code']:<30}, id={item['id']}, 使用{usage_count}次")
        else:
            print(f"\n  [{dict_type}] 'other' [OK] no duplicate")
    else:
        print(f"\n  [{dict_type}] 没有 'other' code [WARNING]")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[总结与建议]")
print("=" * 120)

print(f"\n  前端硬编码的 code:")
print(f"    1. 'other' - 用于4个字典类型")
print(f"    2. 'subject_type_11' - 主题类型的旧版'其他'")

print(f"\n  清理方案调整:")
print(f"    1. 如果 'other' 有重复 → 保留 'other'，删除其他同label的code")
print(f"    2. 如果 'subject_type_11' 有重复:")
print(f"       - 如果前端只硬编码了 'subject_type_11' → 保留它，删除其他同label的")
print(f"       - 或者更新前端改为 'other'（推荐）")

print(f"\n  Frontend adjustment needed:")
print(f"    If 'subject_type_11' will be deleted:")
print(f"      - Change: if (code === 'subject_type_11') to if (code === 'other')")
print(f"      - Use 'other' uniformly for 'other option' check")

print(f"\n{'=' * 120}")
