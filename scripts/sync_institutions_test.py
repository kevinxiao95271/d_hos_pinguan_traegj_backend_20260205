# -*- coding: utf-8 -*-
"""
测试同步脚本（只处理前100条）
"""
import os
import pandas as pd
import pymysql
from datetime import datetime
import sys

# 添加输出刷新
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

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

print("=" * 80)
print("测试同步脚本（前100条）")
print("=" * 80)

# 1. 读取Excel
print("\n[1] 读取Excel...")
sys.stdout.flush()

file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

print(f"总行数: {len(df)}")
print(f"列数: {len(df.columns)}")
sys.stdout.flush()

# 使用列索引
col_name = df.columns[0]
col_region = df.columns[2]
col_level = df.columns[4]
col_uscc = df.columns[6]

print(f"\n列映射:")
print(f"  名称: {col_name}")
print(f"  地区: {col_region}")
print(f"  等级: {col_level}")
print(f"  代码: {col_uscc}")
sys.stdout.flush()

# 2. 只取前100条测试
df_test = df.head(100).copy()
df_test[col_name] = df_test[col_name].fillna('')
df_test[col_uscc] = df_test[col_uscc].fillna('')
df_test = df_test[(df_test[col_name] != '') & (df_test[col_uscc] != '')]

print(f"\n测试记录数: {len(df_test)}")
sys.stdout.flush()

# 3. 连接数据库
print("\n[2] 连接数据库...")
sys.stdout.flush()

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("连接成功")
    sys.stdout.flush()
except Exception as e:
    print(f"连接失败: {e}")
    sys.stdout.flush()
    exit(1)

# 4. 查询现有数据
print("\n[3] 查询现有数据...")
sys.stdout.flush()

cursor.execute("SELECT name, uscc, id, region, level FROM const_init_institutions")
existing_records = cursor.fetchall()

existing_keys = {(r['name'], r['uscc']): r for r in existing_records}
print(f"数据库现有记录: {len(existing_keys)}")
sys.stdout.flush()

# 5. 同步测试
print("\n[4] 开始同步（前100条）...")
sys.stdout.flush()

insert_count = 0
update_count = 0
region_diff_count = 0

for idx, row in df_test.iterrows():
    name = str(row[col_name]).strip()
    uscc = str(row[col_uscc]).strip()
    key = (name, uscc)
    
    excel_region = str(row[col_region]).strip() if pd.notna(row[col_region]) else None
    excel_level = str(row[col_level]).strip() if pd.notna(row[col_level]) else None
    
    if excel_level == '' or excel_level == 'nan':
        excel_level = None
    
    if key in existing_keys:
        # 更新（只更新level）
        db_record = existing_keys[key]
        record_id = db_record['id']
        
        sql = "UPDATE const_init_institutions SET level = %s WHERE id = %s"
        cursor.execute(sql, (excel_level, record_id))
        update_count += 1
        
        # 检查region差异
        if excel_region != db_record['region']:
            region_diff_count += 1
            if region_diff_count <= 5:
                print(f"  [Region差异] {name[:30]}")
                print(f"    Excel: {excel_region}  |  DB: {db_record['region']}")
    else:
        # 插入（生成code）
        import uuid
        code = f"INST_{uuid.uuid4().hex[:8].upper()}"
        
        sql = "INSERT INTO const_init_institutions (code, name, uscc, region, level) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (code, name, uscc, excel_region, excel_level))
        insert_count += 1
    
    if (idx + 1) % 20 == 0:
        print(f"  进度: {idx+1}/{len(df_test)}")
        sys.stdout.flush()

conn.commit()

print(f"\n[5] 测试完成!")
print(f"  插入: {insert_count}")
print(f"  更新: {update_count}")
print(f"  region差异: {region_diff_count}")
sys.stdout.flush()

cursor.close()
conn.close()

print("\n" + "=" * 80)
sys.stdout.flush()
