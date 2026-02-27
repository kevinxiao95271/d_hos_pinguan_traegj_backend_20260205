# -*- coding: utf-8 -*-
"""
【只读分析】检查USCC重复问题及其影响
不做任何数据修改，只生成分析报告
"""
import pymysql
import pandas as pd
import os

# 新的数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'pinguan_db',
    'charset': 'utf8mb4'
}

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("【只读分析】USCC重复问题分析报告")
print("=" * 100)
print("\n注意: 本脚本只做分析，不会修改任何数据！\n")

# ==================== Part 1: Excel数据分析 ====================
print("\n" + "=" * 100)
print("Part 1: Excel数据分析")
print("=" * 100)

file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

print(f"\n[基础信息]")
print(f"  Excel总记录数: {len(df)}")
print(f"  Excel总列数: {len(df.columns)}")

# 列索引
col_name = 0
col_uscc = 6
col_level = 4
col_region = 1

# 统计重复USCC
uscc_column = df.iloc[:, col_uscc].astype(str).str.strip()
uscc_counts = uscc_column.value_counts()
duplicates = uscc_counts[uscc_counts > 1]

# 排除空值和000...
duplicates_clean = duplicates[~duplicates.index.isin(['nan', '', '000000000000000000'])]
duplicates_000 = uscc_counts.get('000000000000000000', 0)

print(f"\n[重复USCC统计]")
print(f"  总USCC数(不重复): {len(uscc_counts)}")
print(f"  重复的USCC数量: {len(duplicates)}")
print(f"  涉及的总记录数: {duplicates.sum()}")
print(f"  特殊值'000000000000000000': {duplicates_000} 条记录")
print(f"  有效重复USCC数量(排除000...): {len(duplicates_clean)}")

# 分析重复USCC的详细信息
print(f"\n[重复USCC类型分析]")

duplicate_analysis = []
for uscc, count in duplicates.items():
    if uscc == 'nan' or uscc == '' or uscc == '000000000000000000':
        continue
    
    mask = df.iloc[:, col_uscc].astype(str).str.strip() == uscc
    records = df[mask]
    
    main_hospitals = []
    branches = []
    
    for idx, row in records.iterrows():
        name = str(row.iloc[col_name]).strip()
        level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '未定级'
        
        # 判断是否为分支机构
        is_branch = any(keyword in name for keyword in ['门诊部', '医务室', '卫生所', '诊所', '卫生站', '医疗点'])
        
        if is_branch:
            branches.append({'name': name, 'level': level})
        else:
            main_hospitals.append({'name': name, 'level': level})
    
    duplicate_analysis.append({
        'uscc': uscc,
        'count': count,
        'main_count': len(main_hospitals),
        'branch_count': len(branches),
        'main_hospitals': main_hospitals,
        'branches': branches
    })

# 分类统计
single_main_multi_branch = [d for d in duplicate_analysis if d['main_count'] == 1 and d['branch_count'] > 0]
multi_main = [d for d in duplicate_analysis if d['main_count'] > 1]
only_branches = [d for d in duplicate_analysis if d['main_count'] == 0]

print(f"  类型1: 1个主医院 + 多个分支 = {len(single_main_multi_branch)} 个USCC")
print(f"  类型2: 多个主医院共享USCC = {len(multi_main)} 个USCC")
print(f"  类型3: 只有分支机构 = {len(only_branches)} 个USCC")

# ==================== Part 2: 数据库现状分析 ====================
print("\n" + "=" * 100)
print("Part 2: 数据库现状分析")
print("=" * 100)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("\n✓ 数据库连接成功")
    
    # 2.1 总记录数
    cursor.execute("SELECT COUNT(*) as total FROM const_init_institutions")
    db_total = cursor.fetchone()['total']
    print(f"\n[数据库基础信息]")
    print(f"  数据库总记录数: {db_total}")
    print(f"  Excel记录数: {len(df)}")
    print(f"  差异: {len(df) - db_total} 条记录")
    
    # 2.2 检查数据库中的重复USCC
    print(f"\n[数据库重复USCC检查]")
    cursor.execute("""
        SELECT uscc, COUNT(*) as count
        FROM const_init_institutions
        WHERE uscc IS NOT NULL AND uscc != '' AND uscc != '000000000000000000'
        GROUP BY uscc
        HAVING COUNT(*) > 1
    """)
    
    db_duplicates = cursor.fetchall()
    print(f"  数据库中重复USCC数量(排除000...): {len(db_duplicates)}")
    
    if len(db_duplicates) > 0:
        print(f"\n  【发现问题】数据库中有重复USCC！")
        print(f"  前10个重复USCC:")
        for i, dup in enumerate(db_duplicates[:10], 1):
            cursor.execute("""
                SELECT name, level FROM const_init_institutions 
                WHERE uscc = %s 
                ORDER BY name
            """, (dup['uscc'],))
            names = cursor.fetchall()
            print(f"    {i}. USCC: {dup['uscc']} (重复{dup['count']}次)")
            for j, n in enumerate(names[:3], 1):
                print(f"       {j}) {n['name']} [{n['level'] or '无等级'}]")
            if len(names) > 3:
                print(f"       ... 还有{len(names)-3}条")
    else:
        print(f"  ✓ 数据库中没有重复USCC（除了000...）")
    
    # 2.3 检查000...的记录
    cursor.execute("""
        SELECT COUNT(*) as count FROM const_init_institutions
        WHERE uscc = '000000000000000000'
    """)
    db_000_count = cursor.fetchone()['count']
    print(f"\n[特殊USCC '000000000000000000']")
    print(f"  Excel中的数量: {duplicates_000}")
    print(f"  数据库中的数量: {db_000_count}")
    
    # 2.4 检查表约束
    print(f"\n[数据库表约束检查]")
    cursor.execute("SHOW CREATE TABLE const_init_institutions")
    create_table = cursor.fetchone()
    create_sql = create_table['Create Table']
    
    has_uk_uscc = 'UNIQUE KEY `uk_uscc`' in create_sql or 'UNIQUE KEY uk_uscc' in create_sql
    has_uk_code = 'UNIQUE KEY `uk_code`' in create_sql or 'UNIQUE KEY uk_code' in create_sql
    
    print(f"  UNIQUE KEY uk_uscc: {'✓ 存在' if has_uk_uscc else '✗ 不存在'}")
    print(f"  UNIQUE KEY uk_code: {'✓ 存在' if has_uk_code else '✗ 不存在'}")
    
    # ==================== Part 3: 平阳县人民医院案例 ====================
    print("\n" + "=" * 100)
    print("Part 3: 平阳县人民医院案例深入分析")
    print("=" * 100)
    
    # 3.1 Excel中的数据
    print(f"\n[Excel中的数据]")
    mask = df.iloc[:, col_name].astype(str).str.contains('平阳县人民医院', na=False)
    pyxian_excel = df[mask]
    
    print(f"  找到 {len(pyxian_excel)} 条记录:")
    uscc_groups = {}
    for idx, row in pyxian_excel.iterrows():
        name = str(row.iloc[col_name]).strip()
        uscc = str(row.iloc[col_uscc]).strip()
        level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '空值'
        
        if uscc not in uscc_groups:
            uscc_groups[uscc] = []
        uscc_groups[uscc].append({'name': name, 'level': level})
    
    for uscc, records in uscc_groups.items():
        if len(records) > 1:
            print(f"\n  ⚠️ 【共享USCC】: {uscc} (共{len(records)}条记录)")
        else:
            print(f"\n  ✓ 【独立USCC】: {uscc}")
        
        for rec in records:
            print(f"     - {rec['name']}")
            print(f"       等级: {rec['level']}")
    
    # 3.2 数据库中的数据
    print(f"\n[数据库中的数据]")
    cursor.execute("""
        SELECT id, name, code, uscc, level
        FROM const_init_institutions
        WHERE name LIKE '%平阳县人民医院%'
        ORDER BY name
    """)
    
    pyxian_db = cursor.fetchall()
    print(f"  找到 {len(pyxian_db)} 条记录:")
    
    db_uscc_groups = {}
    for rec in pyxian_db:
        uscc = rec['uscc']
        if uscc not in db_uscc_groups:
            db_uscc_groups[uscc] = []
        db_uscc_groups[uscc].append(rec)
    
    for uscc, records in db_uscc_groups.items():
        if len(records) > 1:
            print(f"\n  ⚠️ 【共享USCC】: {uscc} (共{len(records)}条记录)")
        else:
            print(f"\n  ✓ 【独立USCC】: {uscc}")
        
        for rec in records:
            print(f"     - {rec['name']}")
            print(f"       ID: {rec['id']}, Code: {rec['code']}, 等级: {rec['level'] or '空值'}")
    
    # ==================== Part 4: 影响评估 ====================
    print("\n" + "=" * 100)
    print("Part 4: 影响评估与建议")
    print("=" * 100)
    
    print(f"\n[问题总结]")
    print(f"1. Excel数据问题:")
    print(f"   - 重复USCC数量: {len(duplicates)} 个")
    print(f"   - 涉及记录: {duplicates.sum()} 条")
    print(f"   - 其中'000000000000000000': {duplicates_000} 条")
    print(f"   - 有效重复: {len(duplicates_clean)} 个USCC")
    
    print(f"\n2. 数据库约束状态:")
    if has_uk_uscc:
        if len(db_duplicates) > 0:
            print(f"   ⚠️ 有UNIQUE约束，但数据库中存在重复USCC！")
            print(f"   ⚠️ 这表明约束可能被绕过或失效")
        else:
            print(f"   ✓ 有UNIQUE约束，且数据库中无重复USCC")
            print(f"   ✓ 但Excel中有{len(duplicates_clean)}个重复，导入时会失败或覆盖")
    else:
        print(f"   ✗ 没有UNIQUE约束")
        print(f"   ✗ 允许重复USCC存在")
    
    print(f"\n3. 实际影响:")
    print(f"   a) 等级对比脚本的影响:")
    print(f"      - 如果主医院和分支机构共享USCC")
    print(f"      - 等级对比时会出现混淆")
    print(f"      - 示例: 平阳县人民医院(三级) vs 门诊部(未定级)")
    
    print(f"\n   b) 数据导入的影响:")
    print(f"      - 如果使用单独USCC作为唯一标识: 只能保留1条")
    print(f"      - 如果使用(name+uscc)组合: 可以保留多条")
    print(f"      - 当前脚本使用(name+uscc)组合，所以多条都能保留")
    
    print(f"\n   c) 数据查询的影响:")
    print(f"      - 按USCC查询会返回多条记录")
    print(f"      - 可能导致业务逻辑混乱")
    
    print(f"\n[建议方案]")
    print(f"\n方案1: 保持现状（推荐）")
    print(f"  优点: 不需要修改数据")
    print(f"  前提: ")
    print(f"    - 确认使用(name+uscc)作为唯一标识")
    print(f"    - 接受分支机构共享主医院USCC的现实")
    print(f"  操作: 无需修改")
    
    print(f"\n方案2: 数据清洗")
    print(f"  操作: ")
    print(f"    - 为分支机构生成虚拟USCC")
    print(f"    - 格式: 原USCC + 分支标识（如-01, -02）")
    print(f"  优点: 每条记录有独立USCC")
    print(f"  缺点: ")
    print(f"    - 需要大量修改")
    print(f"    - 虚拟USCC与实际不符")
    print(f"    - 影响约{len(duplicates_clean) * 2}条记录")
    
    print(f"\n方案3: 增加parent_institution_id字段")
    print(f"  操作: ")
    print(f"    - 数据库增加字段记录父机构ID")
    print(f"    - 分支机构关联主医院")
    print(f"  优点: 保留完整的层级关系")
    print(f"  缺点: 需要修改表结构和业务逻辑")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ 数据库连接失败: {e}")
    print("  无法完成数据库部分的分析")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
print("分析完成！")
print("=" * 100)
print("\n注意: 本报告仅供分析，未做任何数据修改。")
print("请根据以上分析结果决定后续处理方案。")
