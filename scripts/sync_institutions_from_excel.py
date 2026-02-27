# -*- coding: utf-8 -*-
"""
从Excel同步机构数据到数据库
按"机构名称+社会信用代码"为唯一key
"""
import os
import pandas as pd
import pymysql
from datetime import datetime

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("从Excel同步机构数据到数据库")
print("=" * 100)

# 1. 读取Excel文件
print("\n[步骤1] 读取Excel文件...")
print("-" * 100)

file_path = os.path.join(project_root, excel_file)

try:
    df = pd.read_excel(file_path)
    
    print(f"成功读取Excel文件")
    print(f"  总行数: {len(df)}")
    print(f"  总列数: {len(df.columns)}")
    
    # 确认实际列名
    print(f"\n实际列名:")
    for i, col in enumerate(df.columns):
        print(f"  [{i+1}] {col}")
    
    print(f"\n列名映射:")
    col_mapping = {
        '医疗机构名称': 'name',          # 列1
        '区（市、县）': 'region',         # 列3
        '医疗机构': 'level',              # 列5（这是等级列！）
        '统一社会信用代码': 'uscc'        # 列7
    }
    
    for excel_col, db_col in col_mapping.items():
        if excel_col in df.columns:
            print(f"  {excel_col:<20} -> {db_col}")
        else:
            print(f"  {excel_col:<20} -> [缺失]")
            
except Exception as e:
    print(f"读取Excel失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 2. 数据预处理
print("\n[步骤2] 数据预处理...")
print("-" * 100)

# 使用列索引而不是列名（避免列名编码问题）
# 列1: 医疗机构名称
# 列3: 区（市、县）
# 列5: 医疗机构（等级）
# 列7: 统一社会信用代码

col_name = df.columns[0]      # 医疗机构名称
col_region = df.columns[2]    # 区（市、县）
col_level = df.columns[4]     # 医疗机构（等级）
col_uscc = df.columns[6]      # 统一社会信用代码

print(f"使用列索引:")
print(f"  列1 ({col_name}) -> name")
print(f"  列3 ({col_region}) -> region")
print(f"  列5 ({col_level}) -> level")
print(f"  列7 ({col_uscc}) -> uscc")

# 清理数据
df_clean = df.copy()

# 处理空值
df_clean[col_name] = df_clean[col_name].fillna('')
df_clean[col_uscc] = df_clean[col_uscc].fillna('')

# 过滤掉没有名称或代码的记录
df_clean = df_clean[
    (df_clean[col_name] != '') & 
    (df_clean[col_uscc] != '')
]

print(f"\n有效记录数: {len(df_clean)}")
print(f"过滤掉的记录: {len(df) - len(df_clean)}")

# 统计等级分布
print(f"\nExcel中的等级分布:")
level_counts = df_clean[col_level].value_counts(dropna=False)
null_count = df_clean[col_level].isna().sum()

print(f"  空值(NULL): {null_count} 个")
for level, count in level_counts.items():
    if pd.notna(level):
        print(f"  {level}: {count} 个")

# 3. 连接数据库
print("\n[步骤3] 连接数据库...")
print("-" * 100)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("数据库连接成功")
    
    # 检查表结构
    cursor.execute("SHOW TABLES LIKE 'const_init_institutions'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("错误: const_init_institutions 表不存在")
        exit(1)
    
    print("目标表: const_init_institutions")
    
except Exception as e:
    print(f"数据库连接失败: {e}")
    exit(1)

# 4. 查询现有数据
print("\n[步骤4] 查询现有数据...")
print("-" * 100)

try:
    cursor.execute("SELECT COUNT(*) as count FROM const_init_institutions")
    result = cursor.fetchone()
    db_count_before = result['count']
    
    print(f"数据库当前记录数: {db_count_before}")
    
    # 获取所有现有的 name+uscc 组合（包含region用于对比）
    cursor.execute("SELECT name, uscc, id, region FROM const_init_institutions")
    existing_records = cursor.fetchall()
    
    existing_keys = {(r['name'], r['uscc']): {'id': r['id'], 'region': r['region']} for r in existing_records}
    print(f"现有唯一key数: {len(existing_keys)}")
    
except Exception as e:
    print(f"查询失败: {e}")
    cursor.close()
    conn.close()
    exit(1)

# 5. 同步数据
print("\n[步骤5] 开始同步数据...")
print("-" * 100)
print("注意: 只更新level字段，不更新region字段")

insert_count = 0
update_count = 0
error_count = 0
region_diff_list = []  # 记录region差异

print(f"处理 {len(df_clean)} 条记录...")

for idx, row in df_clean.iterrows():
    try:
        name = str(row[col_name]).strip()
        uscc = str(row[col_uscc]).strip()
        
        # 构建唯一key
        key = (name, uscc)
        
        # 准备数据
        excel_region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
        excel_level = str(row[col_level]).strip() if pd.notna(row[col_level]) else None
        
        # 如果level为空，设为None（数据库中为NULL）
        if excel_level == '' or excel_level == 'nan':
            excel_level = None
        
        # 判断是插入还是更新
        if key in existing_keys:
            # 更新（只更新level）
            record_info = existing_keys[key]
            record_id = record_info['id']
            db_region = record_info['region']
            
            sql = """
                UPDATE const_init_institutions 
                SET level = %s
                WHERE id = %s
            """
            
            cursor.execute(sql, (excel_level, record_id))
            update_count += 1
            
            # 对比region差异
            if excel_region != db_region:
                region_diff_list.append({
                    'name': name,
                    'uscc': uscc,
                    'excel_region': excel_region,
                    'db_region': db_region
                })
            
        else:
            # 插入（新记录使用Excel的region）
            sql = """
                INSERT INTO const_init_institutions (name, uscc, region, level)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(sql, (name, uscc, excel_region, excel_level))
            insert_count += 1
        
        # 每1000条提交一次
        if (idx + 1) % 1000 == 0:
            conn.commit()
            print(f"  已处理: {idx + 1}/{len(df_clean)} 条 (插入:{insert_count}, 更新:{update_count}, region差异:{len(region_diff_list)})")
        
    except Exception as e:
        error_count += 1
        if error_count <= 10:  # 只显示前10个错误
            print(f"  [错误] 处理第 {idx+1} 行失败: {e}")

# 最后提交
conn.commit()

print(f"\n同步完成!")
print(f"  插入: {insert_count} 条")
print(f"  更新: {update_count} 条 (只更新level)")
print(f"  错误: {error_count} 条")
print(f"  region差异: {len(region_diff_list)} 条")

# 6. 验证结果
print("\n[步骤6] 验证结果...")
print("-" * 100)

try:
    cursor.execute("SELECT COUNT(*) as count FROM const_init_institutions")
    result = cursor.fetchone()
    db_count_after = result['count']
    
    print(f"数据库同步后记录数: {db_count_after}")
    print(f"变化: {db_count_after - db_count_before:+d}")
    
    # 统计等级分布
    cursor.execute("""
        SELECT 
            CASE 
                WHEN level IS NULL OR level = '' THEN '[空值]'
                ELSE level 
            END as level_display,
            COUNT(*) as count
        FROM const_init_institutions
        GROUP BY level_display
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    
    print(f"\n数据库中的等级分布:")
    for row in results:
        print(f"  {row['level_display']:<20}: {row['count']:>6} 个")
    
except Exception as e:
    print(f"验证失败: {e}")

# 7. 生成region差异报告
if region_diff_list:
    print("\n[步骤7] 生成region差异报告...")
    print("-" * 100)
    
    report_file = os.path.join(project_root, "region差异报告.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("Region差异报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"发现 {len(region_diff_list)} 条region差异\n\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'序号':<6} {'机构名称':<40} {'Excel':<20} {'数据库':<20}\n")
        f.write("-" * 100 + "\n")
        
        for i, diff in enumerate(region_diff_list, 1):
            name = diff['name'][:38] + '..' if len(diff['name']) > 40 else diff['name']
            excel_r = diff['excel_region'] or '[空]'
            db_r = diff['db_region'] or '[空]'
            f.write(f"{i:<6} {name:<40} {excel_r:<20} {db_r:<20}\n")
    
    print(f"差异报告已保存: {report_file}")
    
    # 显示前10条差异
    print(f"\n前10条差异示例:")
    for i, diff in enumerate(region_diff_list[:10], 1):
        excel_r = diff['excel_region'] or '[空]'
        db_r = diff['db_region'] or '[空]'
        print(f"  {i}. {diff['name'][:30]}")
        print(f"     Excel: {excel_r}  |  数据库: {db_r}")
else:
    print("\n[OK] 没有发现region差异")

# 8. 清理
cursor.close()
conn.close()

print("\n" + "=" * 100)
print("数据同步完成")
print("=" * 100)
