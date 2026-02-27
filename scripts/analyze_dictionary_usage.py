# -*- coding: utf-8 -*-
"""
分析字典项的使用情况，找出重复的 label 并统计使用次数
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

print("=" * 140)
print("字典项重复数据使用情况分析")
print("=" * 140)

# 要检查的类型
types_to_check = [
    ('subject_type', 'subject_type_code', '主题类型'),
    ('method', 'method_code', '运用手法'),
    ('experience_improve', 'experience_improve_code', '改善就医感受'),
    ('quality_topic', 'quality_topic_code', '医疗质量安全主题')
]

all_to_delete = []
all_to_update = []

for dict_type, field_name, type_name in types_to_check:
    print(f"\n{'=' * 140}")
    print(f"[{type_name}] type='{dict_type}', 字段='{field_name}'")
    print("-" * 140)
    
    # 查询该类型的所有字典项
    cursor.execute("""
        SELECT id, code, label, active
        FROM dictionary_items
        WHERE type = %s
        ORDER BY label, id
    """, (dict_type,))
    
    items = cursor.fetchall()
    
    # 按 label 分组
    label_groups = {}
    for item in items:
        label = item['label']
        if label not in label_groups:
            label_groups[label] = []
        label_groups[label].append(item)
    
    # 找出重复的 label
    duplicate_labels = {label: items for label, items in label_groups.items() if len(items) > 1}
    
    print(f"\n  总数: {len(items)} 条")
    print(f"  唯一 label: {len(label_groups)} 个")
    print(f"  重复 label: {len(duplicate_labels)} 个")
    
    if duplicate_labels:
        print(f"\n  重复的 label 及其使用情况:")
        print(f"  {'-' * 140}")
        
        for label, dup_items in duplicate_labels.items():
            print(f"\n  Label: {label}")
            
            # 统计每个 code 的使用次数
            usage_stats = []
            
            for item in dup_items:
                code = item['code']
                
                # 查询使用次数
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM activity_infos
                    WHERE {field_name} = %s
                """, (code,))
                
                usage_count = cursor.fetchone()['count']
                
                usage_stats.append({
                    'id': item['id'],
                    'code': code,
                    'active': item['active'],
                    'usage_count': usage_count
                })
            
            # 显示统计信息
            for stat in usage_stats:
                active_str = 'active=1' if stat['active'] == 1 else 'active=0'
                usage_str = f"使用{stat['usage_count']}次" if stat['usage_count'] > 0 else "未使用"
                print(f"    - ID={stat['id']:<4}, code={stat['code']:<45}, {active_str}, {usage_str}")
            
            # 决策：保留哪个，删除哪个
            # 规则：保留使用次数多的，如果都未使用则保留语义化的新 code
            usage_stats_sorted = sorted(usage_stats, key=lambda x: (-x['usage_count'], len(x['code'])))
            
            keep_item = usage_stats_sorted[0]
            delete_items = usage_stats_sorted[1:]
            
            print(f"    [决策] 保留: {keep_item['code']} (使用{keep_item['usage_count']}次)")
            
            for delete_item in delete_items:
                if delete_item['usage_count'] > 0:
                    # 需要先更新数据
                    print(f"    [决策] 删除: {delete_item['code']} (需要先迁移{delete_item['usage_count']}条记录)")
                    all_to_update.append({
                        'field': field_name,
                        'old_code': delete_item['code'],
                        'new_code': keep_item['code'],
                        'count': delete_item['usage_count'],
                        'dict_id': delete_item['id']
                    })
                else:
                    # 直接删除
                    print(f"    [决策] 删除: {delete_item['code']} (未使用，可直接删除)")
                    all_to_delete.append({
                        'dict_id': delete_item['id'],
                        'code': delete_item['code']
                    })

# 总结
print(f"\n{'=' * 140}")
print("[清理方案总结]")
print("=" * 140)

print(f"\n【需要数据迁移的字典项】(共 {len(all_to_update)} 个)")
print(f"  {'字段':<35} {'旧Code':<45} {'新Code':<45} {'影响记录数'}")
print(f"  {'-' * 140}")

for item in all_to_update:
    print(f"  {item['field']:<35} {item['old_code']:<45} {item['new_code']:<45} {item['count']}")

print(f"\n【可直接删除的字典项】(共 {len(all_to_delete)} 个)")
print(f"  {'字典项ID':<10} {'Code':<45} {'说明'}")
print(f"  {'-' * 140}")

for item in all_to_delete:
    print(f"  {item['dict_id']:<10} {item['code']:<45} 未使用，可直接删除")

# 生成 SQL 脚本
print(f"\n{'=' * 140}")
print("[SQL 执行脚本]")
print("=" * 140)

if all_to_update:
    print(f"\n-- Step 1: 数据迁移 (更新 activity_infos 表)")
    print(f"-- 将旧 code 替换为新 code，共 {len(all_to_update)} 个字段需要更新")
    print()
    
    for item in all_to_update:
        print(f"-- 迁移 {item['old_code']} -> {item['new_code']} ({item['count']} 条记录)")
        print(f"UPDATE activity_infos SET {item['field']} = '{item['new_code']}' WHERE {item['field']} = '{item['old_code']}';")

if all_to_delete or all_to_update:
    print(f"\n-- Step 2: 删除字典项")
    print(f"-- 删除未使用的和已迁移的旧字典项，共 {len(all_to_delete) + len(all_to_update)} 条")
    print()
    
    delete_ids = [item['dict_id'] for item in all_to_delete] + [item['dict_id'] for item in all_to_update]
    
    if delete_ids:
        print(f"DELETE FROM dictionary_items WHERE id IN ({', '.join(map(str, delete_ids))});")

# 验证脚本
print(f"\n-- Step 3: 验证")
print(f"-- 验证是否还有重复的 label")
print()

for dict_type, field_name, type_name in types_to_check:
    print(f"-- 验证 {type_name}")
    print(f"SELECT label, COUNT(*) as count FROM dictionary_items WHERE type = '{dict_type}' GROUP BY label HAVING count > 1;")

cursor.close()
conn.close()

print(f"\n{'=' * 140}")
print("[总结]")
print("=" * 140)

print(f"\n  清理统计:")
print(f"    - 需要数据迁移: {len(all_to_update)} 个字典项")
print(f"    - 可直接删除: {len(all_to_delete)} 个字典项")
print(f"    - 总计删除: {len(all_to_delete) + len(all_to_update)} 个字典项")

total_records_to_migrate = sum(item['count'] for item in all_to_update)
print(f"\n  影响数据:")
print(f"    - 需要更新的 activity_infos 记录: {total_records_to_migrate} 条")

print(f"\n  执行建议:")
print(f"    1. 先执行数据迁移（UPDATE activity_infos）")
print(f"    2. 再删除旧字典项（DELETE FROM dictionary_items）")
print(f"    3. 最后验证（检查是否还有重复）")

print(f"\n{'=' * 140}")
