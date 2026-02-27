# -*- coding: utf-8 -*-
"""
检查Excel中重复的USCC及其影响
"""
import pandas as pd
import pymysql
import os

# 配置
db_config = {
    'host': 'gz-cynosdbmysql-grp-f2dfgir9.sql.tencentcdb.com',
    'port': 29805,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'pinguan_db',
    'charset': 'utf8mb4'
}

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("检查Excel中重复USCC的影响")
print("=" * 100)

# 1. 读取Excel
print("\n[步骤1] 读取Excel文件...")
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)
print(f"Excel总记录数: {len(df)}")

# 列顺序：0=机构名称, 6=统一社会信用代码, 4=医疗机构等级
col_name = 0
col_uscc = 6
col_level = 4

# 2. 统计重复USCC
print("\n[步骤2] 统计重复的USCC...")
uscc_column = df.iloc[:, col_uscc].astype(str).str.strip()
uscc_counts = uscc_column.value_counts()
duplicates = uscc_counts[uscc_counts > 1]

print(f"总USCC数: {len(uscc_counts)}")
print(f"重复USCC数量: {len(duplicates)}")
print(f"涉及记录数: {duplicates.sum()}")

# 3. 详细分析重复USCC
print("\n[步骤3] 重复USCC详细信息")
print("=" * 100)

duplicate_details = []

for uscc, count in duplicates.items():
    # 跳过空值和nan
    if uscc == 'nan' or uscc == '' or pd.isna(uscc):
        continue
    
    # 找到所有使用该USCC的机构
    mask = df.iloc[:, col_uscc].astype(str).str.strip() == uscc
    records = df[mask]
    
    detail = {
        'uscc': uscc,
        'count': count,
        'records': []
    }
    
    for idx, row in records.iterrows():
        name = str(row.iloc[col_name]).strip()
        level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '未定级'
        
        detail['records'].append({
            'name': name,
            'level': level,
            'is_branch': any(keyword in name for keyword in ['门诊部', '医务室', '卫生所', '诊所', '卫生站'])
        })
    
    duplicate_details.append(detail)

# 排序：按重复次数降序
duplicate_details.sort(key=lambda x: x['count'], reverse=True)

print(f"\n共发现 {len(duplicate_details)} 个重复的USCC\n")

# 显示前20个重复USCC
for i, detail in enumerate(duplicate_details[:20], 1):
    print(f"{i}. USCC: {detail['uscc']} (重复{detail['count']}次)")
    
    # 识别主医院和分支机构
    main_hospital = None
    branches = []
    
    for record in detail['records']:
        if record['is_branch']:
            branches.append(record)
        else:
            if main_hospital is None:
                main_hospital = record
            else:
                # 多个非分支机构
                branches.append(record)
    
    if main_hospital:
        print(f"   [主医院] {main_hospital['name']} - 等级: {main_hospital['level']}")
    
    for branch in branches:
        branch_type = "[分支机构]" if branch['is_branch'] else "[其他]"
        print(f"   {branch_type} {branch['name']} - 等级: {branch['level']}")
    
    print()

# 4. 检查数据库中的影响
print("\n[步骤4] 检查数据库中受影响的记录")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 检查数据库中是否有重复USCC的记录
cursor.execute("""
    SELECT uscc, COUNT(*) as count, GROUP_CONCAT(name SEPARATOR ' | ') as names
    FROM const_init_institutions
    WHERE uscc IS NOT NULL AND uscc != ''
    GROUP BY uscc
    HAVING COUNT(*) > 1
""")

db_duplicates = cursor.fetchall()
print(f"数据库中重复USCC数量: {len(db_duplicates)}")

if len(db_duplicates) > 0:
    print("\n数据库中的重复USCC:")
    for dup in db_duplicates:
        print(f"  USCC: {dup['uscc']} - 出现{dup['count']}次")
        print(f"    机构: {dup['names']}")
        print()

# 5. 具体检查"平阳县人民医院"案例
print("\n[步骤5] 平阳县人民医院案例分析")
print("=" * 100)

# Excel中的数据
print("\nExcel中的'平阳县人民医院'相关记录:")
mask = df.iloc[:, col_name].astype(str).str.contains('平阳县人民医院', na=False)
pyxian_records = df[mask]

for idx, row in pyxian_records.iterrows():
    name = str(row.iloc[col_name]).strip()
    uscc = str(row.iloc[col_uscc]).strip()
    level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '空值'
    print(f"  - {name}")
    print(f"    USCC: {uscc}")
    print(f"    等级: {level}")
    print()

# 数据库中的数据
print("\n数据库中的'平阳县人民医院'相关记录:")
cursor.execute("""
    SELECT id, name, code, uscc, level
    FROM const_init_institutions
    WHERE name LIKE '%平阳县人民医院%'
    ORDER BY name
""")

db_pyxian = cursor.fetchall()
for record in db_pyxian:
    print(f"  - {record['name']}")
    print(f"    ID: {record['id']}")
    print(f"    Code: {record['code']}")
    print(f"    USCC: {record['uscc']}")
    print(f"    等级: {record['level'] or '空值'}")
    print()

# 6. 总结影响
print("\n[步骤6] 影响总结")
print("=" * 100)

print(f"""
发现的问题:
1. Excel中有 {len(duplicate_details)} 个重复的USCC
2. 涉及总记录数: {sum(d['count'] for d in duplicate_details)}
3. 数据库中重复USCC: {len(db_duplicates)} 个

影响分析:
1. 数据导入时的影响:
   - 由于USCC是唯一约束，第二条及以后的记录无法插入
   - 或者会更新已存在的记录，导致数据覆盖
   
2. 对等级对比的影响:
   - 如果主医院和分支机构共享USCC，等级对比会不准确
   - 示例: 平阳县人民医院(三级) vs 平阳县人民医院驻xx门诊部(未定级)
   - 导入脚本可能只保留了一条记录
   
3. 数据完整性影响:
   - 分支机构（门诊部、医务室等）可能被忽略
   - 或主医院数据被分支机构数据覆盖

建议解决方案:
1. 使用"机构名称+USCC"作为唯一标识（目前已实现）
2. 对于分支机构，考虑:
   - 使用不同的USCC（如果有）
   - 或在名称中明确标注分支类型
   - 或在数据库中添加parent_institution_id字段
""")

cursor.close()
conn.close()

print("\n检查完成!")
