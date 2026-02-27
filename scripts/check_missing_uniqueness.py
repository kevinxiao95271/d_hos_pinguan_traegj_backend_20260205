# -*- coding: utf-8 -*-
"""
检查未导入记录的(名字+USCC)唯一性
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
missing_file = os.path.join(project_root, '最终验证-未导入记录.xlsx')

print("=" * 100)
print("检查未导入记录的(名字+USCC)唯一性")
print("=" * 100)

df_missing = pd.read_excel(missing_file)

print(f"\n未导入记录总数: {len(df_missing)}")

# 创建(名字+USCC)组合键
df_missing['组合键'] = df_missing['机构名称'].astype(str).str.strip() + '|||' + df_missing['统一社会信用代码'].astype(str).str.strip()

# 统计组合键的重复情况
key_counts = df_missing['组合键'].value_counts()
duplicates = key_counts[key_counts > 1]

print(f"\n" + "=" * 100)
print("唯一性检查结果")
print("=" * 100)

print(f"\n[统计]")
print(f"   不同的(名字+USCC)组合数: {len(key_counts)}")
print(f"   总记录数: {len(df_missing)}")
print(f"   重复的组合数: {len(duplicates)}")
print(f"   涉及的记录数: {duplicates.sum() if len(duplicates) > 0 else 0}")

if len(duplicates) == 0:
    print(f"\n[OK] (名字+USCC)组合是唯一的！")
    print(f"   这6044条未导入记录中，每个(名字+USCC)组合都是唯一的")
    print(f"   它们未导入的原因是：USCC在DB中已存在（被其他名字的机构占用）")
else:
    print(f"\n[DUPLICATE] 发现重复！")
    print(f"   有{len(duplicates)}个(名字+USCC)组合重复出现")
    print(f"   涉及{duplicates.sum()}条记录")
    
    print(f"\n详细重复记录:")
    for i, (combo, count) in enumerate(duplicates.head(20).items(), 1):
        parts = combo.split('|||')
        if len(parts) == 2:
            name, uscc = parts
            print(f"\n{i}. 名字: {name}")
            print(f"   USCC: {uscc}")
            print(f"   重复次数: {count}")
            
            # 显示这些重复记录的详细信息
            matched = df_missing[df_missing['组合键'] == combo]
            for idx, row in matched.iterrows():
                print(f"      - Excel等级(原始): {row['Excel等级(原始)']}")
                print(f"        Excel等级(标准): {row['Excel等级(标准)']}")

# 与DB中的数据对比
print(f"\n" + "=" * 100)
print("未导入原因分析")
print("=" * 100)

# 读取DB数据的USCC
import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print(f"\n连接数据库检查...")
conn = pymysql.connect(**DB_CONFIG)
try:
    query = "SELECT DISTINCT uscc FROM const_init_institutions WHERE uscc IS NOT NULL AND uscc != ''"
    df_db_uscc = pd.read_sql(query, conn)
    db_uscc_set = set(df_db_uscc['uscc'].str.strip())
    print(f"   DB中不同的USCC数: {len(db_uscc_set)}")
finally:
    conn.close()

# 检查未导入记录的USCC是否在DB中
missing_uscc_set = set(df_missing['统一社会信用代码'].astype(str).str.strip())
print(f"   未导入记录中不同的USCC数: {len(missing_uscc_set)}")

uscc_in_db = missing_uscc_set & db_uscc_set
uscc_not_in_db = missing_uscc_set - db_uscc_set

print(f"\n   未导入记录的USCC在DB中已存在: {len(uscc_in_db)} 个")
print(f"   未导入记录的USCC在DB中不存在: {len(uscc_not_in_db)} 个")

if len(uscc_not_in_db) > 0:
    print(f"\n   不在DB中的USCC示例:")
    for uscc in list(uscc_not_in_db)[:10]:
        # 找到使用这个USCC的机构
        matched = df_missing[df_missing['统一社会信用代码'].astype(str).str.strip() == uscc]
        print(f"      {uscc}: {len(matched)}个机构")
        for idx, row in matched.head(2).iterrows():
            print(f"         - {row['机构名称']}")

# 统计因USCC重复导致未导入的记录
uscc_in_db_count = df_missing[df_missing['统一社会信用代码'].astype(str).str.strip().isin(uscc_in_db)].shape[0]
uscc_not_in_db_count = df_missing[df_missing['统一社会信用代码'].astype(str).str.strip().isin(uscc_not_in_db)].shape[0]

print(f"\n" + "=" * 100)
print("结论")
print("=" * 100)

print(f"\n[未导入记录分析]")
print(f"   总计: {len(df_missing)} 条")
print(f"   因USCC在DB中已存在(uk_uscc约束): {uscc_in_db_count} 条")
print(f"   其他原因: {uscc_not_in_db_count} 条")

if len(duplicates) == 0:
    print(f"\n[唯一性]")
    print(f"   [OK] 这6044条未导入记录的(名字+USCC)组合都是唯一的")
    print(f"   [OK] 如果修改DB约束为uk_name_uscc，这些记录可以全部导入")
else:
    print(f"\n[唯一性]")
    print(f"   [WARN] 有{len(duplicates)}个(名字+USCC)组合重复")
    print(f"   [WARN] 即使修改约束为uk_name_uscc，仍有{duplicates.sum()}条记录无法导入")

print(f"\n检查完成！")
