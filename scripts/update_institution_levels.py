# -*- coding: utf-8 -*-
"""
批量更新数据库中的机构等级信息
规则：Excel空值->DB填"无等级"；Excel有值->DB原样使用Excel的值
"""
import pandas as pd
import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"

print("=" * 100, flush=True)
print("批量更新数据库中的机构等级信息", flush=True)
print("=" * 100, flush=True)

# 1. 读取差异报告
print("\n[1/5] 读取等级差异报告...", flush=True)
diff_file = os.path.join(project_root, '等级差异详细报告.csv')
df_diff = pd.read_csv(diff_file, encoding='utf-8-sig')

print(f"   差异记录总数: {len(df_diff)}", flush=True)
print(f"   字段: {list(df_diff.columns)}", flush=True)

# 2. 准备更新数据
print("\n[2/5] 准备更新数据...", flush=True)

# 统计更新类型
update_types = df_diff.groupby(['Excel等级(期望DB值)', 'DB等级(实际值)']).size().sort_values(ascending=False)

print(f"\n   更新类型统计:", flush=True)
for (excel_val, db_val), count in update_types.head(10).items():
    excel_display = excel_val if str(excel_val) != 'nan' else '[空]'
    db_display = db_val if str(db_val) != 'nan' else '[空]'
    print(f"      {db_display} -> {excel_display}: {count} 条", flush=True)

# 3. 连接数据库并执行更新
print(f"\n[3/5] 连接数据库并执行更新...", flush=True)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    total_updated = 0
    failed_updates = []
    
    # 批量更新（每100条提交一次）
    batch_size = 100
    
    print(f"   开始更新 {len(df_diff)} 条记录...", flush=True)
    
    for idx, row in df_diff.iterrows():
        db_id = int(row['DB记录ID'])
        new_level = str(row['Excel等级(期望DB值)'])
        institution_name = row['机构名称']
        
        try:
            # 更新SQL
            update_sql = """
                UPDATE const_init_institutions 
                SET level = %s 
                WHERE id = %s
            """
            cursor.execute(update_sql, (new_level, db_id))
            total_updated += 1
            
            # 每100条提交一次
            if total_updated % batch_size == 0:
                conn.commit()
                percent = (total_updated / len(df_diff)) * 100
                print(f"   进度: {total_updated} / {len(df_diff)} ({percent:.1f}%)", flush=True)
            
        except Exception as e:
            failed_updates.append({
                'id': db_id,
                'name': institution_name,
                'error': str(e)
            })
            print(f"   [WARN] 更新失败 ID={db_id}, {institution_name}: {e}", flush=True)
    
    # 提交剩余的更新
    conn.commit()
    
    print(f"\n   [OK] 成功更新 {total_updated} 条记录", flush=True)
    
    if failed_updates:
        print(f"   [WARN] 失败 {len(failed_updates)} 条", flush=True)
        for fail in failed_updates[:10]:
            print(f"      ID={fail['id']}: {fail['name']} - {fail['error']}", flush=True)
    
except Exception as e:
    conn.rollback()
    print(f"\n   [ERROR] 更新失败，已回滚: {e}", flush=True)
    raise

finally:
    cursor.close()

# 4. 验证更新结果
print(f"\n[4/5] 验证更新结果...", flush=True)

cursor = conn.cursor()
try:
    # 随机抽查一些更新的记录
    sample_ids = df_diff['DB记录ID'].head(20).tolist()
    
    if sample_ids:
        placeholders = ','.join(['%s'] * len(sample_ids))
        verify_sql = f"""
            SELECT id, name, level 
            FROM const_init_institutions 
            WHERE id IN ({placeholders})
        """
        cursor.execute(verify_sql, sample_ids)
        results = cursor.fetchall()
        
        print(f"\n   抽查前20条记录:")
        print(f"   {'ID':<10} {'机构名称':<40} {'当前等级':<15}")
        print("   " + "-" * 80)
        
        for record_id, name, level in results:
            name_display = name[:38] if len(name) > 38 else name
            level_display = level if level else '[空]'
            print(f"   {record_id:<10} {name_display:<40} {level_display:<15}")
    
    # 统计更新后的等级分布
    count_sql = """
        SELECT 
            CASE 
                WHEN level IS NULL OR level = '' THEN '[空值]'
                ELSE level 
            END as level_group,
            COUNT(*) as count
        FROM const_init_institutions
        GROUP BY level_group
        ORDER BY count DESC
    """
    cursor.execute(count_sql)
    level_distribution = cursor.fetchall()
    
    print(f"\n   更新后DB等级分布:")
    for level, count in level_distribution:
        print(f"      {level}: {count}")
    
finally:
    cursor.close()
    conn.close()

# 5. 生成更新报告
print(f"\n[5/5] 生成更新报告...")

report = f"""
更新完成报告
{'=' * 100}

更新时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

[更新统计]
  总更新记录数: {total_updated}
  成功: {total_updated - len(failed_updates)}
  失败: {len(failed_updates)}

[主要更新类型]
"""

for (excel_val, db_val), count in update_types.head(10).items():
    excel_display = excel_val if str(excel_val) != 'nan' else '[空]'
    db_display = db_val if str(db_val) != 'nan' else '[空]'
    report += f"  {db_display} -> {excel_display}: {count} 条\n"

report += f"""
[更新后等级分布]
"""
for level, count in level_distribution:
    report += f"  {level}: {count}\n"

if failed_updates:
    report += f"""
[失败记录]
"""
    for fail in failed_updates[:20]:
        report += f"  ID={fail['id']}: {fail['name']} - {fail['error']}\n"

report += f"""
{'=' * 100}
"""

report_file = os.path.join(project_root, '等级更新报告.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n   已生成更新报告: {report_file}")

print(f"\n" + "=" * 100)
print("更新完成！")
print("=" * 100)
print(f"\n总结:")
print(f"  - 成功更新 {total_updated} 条记录")
print(f"  - 失败 {len(failed_updates)} 条")
print(f"  - 详细报告: {report_file}")
