# -*- coding: utf-8 -*-
"""
查找所有类似的错误字典项 (带时间戳后缀的)
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
print("查找所有带时间戳后缀的错误字典项")
print("=" * 120)

# 查找所有code包含 _202602 的字典项 (这种通常是错误的)
cursor.execute("""
    SELECT id, type, code, label
    FROM dictionary_items
    WHERE code LIKE '%_202602%'
    ORDER BY type, code
""")

wrong_items = cursor.fetchall()

if wrong_items:
    print(f"\n  找到 {len(wrong_items)} 个可能错误的字典项:")
    print(f"  {'ID':<6} {'Type':<25} {'Code':<45} {'Label'}")
    print(f"  {'-' * 120}")
    
    for item in wrong_items:
        print(f"  {item['id']:<6} {item['type']:<25} {item['code']:<45} {item['label']}")
        
        # 查询使用次数
        # 根据 type 确定查询哪个字段
        if item['type'] == 'subject_type':
            field_name = 'subject_type_code'
        elif item['type'] == 'method':
            field_name = 'method_code'
        elif item['type'] == 'experience_improve':
            field_name = 'experience_improve_code'
        elif item['type'] == 'quality_topic':
            field_name = 'quality_topic_code'
        else:
            field_name = None
        
        if field_name:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM activity_infos
                WHERE {field_name} = %s
            """, (item['code'],))
            
            usage_count = cursor.fetchone()['count']
            print(f"         使用次数: {usage_count}")
else:
    print(f"\n  [OK] 未找到带时间戳后缀的字典项")

# 查找所有 label 中包含数字时间戳的 (可能是错误的)
print(f"\n{'=' * 120}")
print("查找所有 label 中包含时间戳的字典项")
print("=" * 120)

cursor.execute("""
    SELECT id, type, code, label
    FROM dictionary_items
    WHERE label REGEXP '[0-9]{14}'
    ORDER BY type, code
""")

label_wrong_items = cursor.fetchall()

if label_wrong_items:
    print(f"\n  找到 {len(label_wrong_items)} 个 label 可能错误的字典项:")
    print(f"  {'ID':<6} {'Type':<25} {'Code':<45} {'Label'}")
    print(f"  {'-' * 120}")
    
    for item in label_wrong_items:
        print(f"  {item['id']:<6} {item['type']:<25} {item['code']:<45} {item['label']}")
else:
    print(f"\n  [OK] 未找到 label 中包含时间戳的字典项")

cursor.close()
conn.close()

print(f"\n{'=' * 120}")
print("[总结]")
print("=" * 120)

print(f"\n  这些错误的字典项看起来都是数据导入时生成的临时/错误数据")
print(f"  后缀 20260205144626 表示时间戳: 2026年2月5日 14:46:26")
print(f"\n  建议:")
print(f"    1. 查找所有使用这些错误 code 的记录")
print(f"    2. 将它们映射到正确的 code (如 'other')")
print(f"    3. 删除这些错误的字典项")

print(f"\n{'=' * 120}")
