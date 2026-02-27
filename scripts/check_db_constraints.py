# -*- coding: utf-8 -*-
"""
【只读分析】检查数据库约束和挂靠机构入库情况
"""
import pymysql

# 正确的数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("【只读分析】数据库约束和挂靠机构检查")
print("=" * 100)
print("\n注意: 本脚本只做查询分析，不会修改任何数据！\n")

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("OK: Database connected successfully\n")
    
    # ==================== Part 1: 表结构和约束 ====================
    print("=" * 100)
    print("Part 1: const_init_institutions 表结构和约束")
    print("=" * 100)
    
    cursor.execute("SHOW CREATE TABLE const_init_institutions")
    result = cursor.fetchone()
    create_sql = result['Create Table']
    
    print("\n[完整建表语句]")
    print(create_sql)
    
    # 分析约束
    print("\n\n[约束分析]")
    has_pk = 'PRIMARY KEY' in create_sql
    has_uk_code = 'UNIQUE KEY `uk_code`' in create_sql or 'UNIQUE KEY uk_code' in create_sql
    has_uk_uscc = 'UNIQUE KEY `uk_uscc`' in create_sql or 'UNIQUE KEY uk_uscc' in create_sql
    
    print(f"1. PRIMARY KEY (id): {'YES' if has_pk else 'NO'}")
    print(f"2. UNIQUE KEY uk_code: {'YES' if has_uk_code else 'NO'}")
    print(f"3. UNIQUE KEY uk_uscc: {'YES' if has_uk_uscc else 'NO'}")
    
    if has_uk_uscc:
        print("\nWARNING: uk_uscc constraint exists - branch institutions cannot share USCC!")
    else:
        print("\nOK: No uk_uscc constraint - branch institutions can share parent USCC")
    
    # ==================== Part 2: 数据统计 ====================
    print("\n" + "=" * 100)
    print("Part 2: 数据统计")
    print("=" * 100)
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) as total FROM const_init_institutions")
    total = cursor.fetchone()['total']
    print(f"\n[基础统计]")
    print(f"总记录数: {total}")
    
    # 检查USCC重复情况
    cursor.execute("""
        SELECT COUNT(DISTINCT uscc) as unique_uscc,
               COUNT(*) as total_records
        FROM const_init_institutions
        WHERE uscc IS NOT NULL AND uscc != ''
    """)
    uscc_stats = cursor.fetchone()
    print(f"不同的USCC数: {uscc_stats['unique_uscc']}")
    print(f"总记录数(有USCC): {uscc_stats['total_records']}")
    print(f"平均每个USCC对应记录数: {uscc_stats['total_records'] / uscc_stats['unique_uscc']:.2f}")
    
    # ==================== Part 3: 检查重复USCC ====================
    print("\n" + "=" * 100)
    print("Part 3: 检查重复USCC（挂靠机构是否入库）")
    print("=" * 100)
    
    cursor.execute("""
        SELECT uscc, COUNT(*) as count
        FROM const_init_institutions
        WHERE uscc IS NOT NULL AND uscc != '' AND uscc != '000000000000000000'
        GROUP BY uscc
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 20
    """)
    
    duplicates = cursor.fetchall()
    print(f"\n[重复USCC统计]")
    print(f"重复USCC数量: {len(duplicates)}")
    
    if len(duplicates) > 0:
        print(f"\nOK: Duplicate USCC found - branch institutions are successfully stored!")
        print(f"\nTop 10 duplicate USCC details:\n")
        
        for i, dup in enumerate(duplicates[:10], 1):
            print(f"{i}. USCC: {dup['uscc']} (共{dup['count']}条记录)")
            
            # 查询这个USCC的所有记录
            cursor.execute("""
                SELECT id, name, code, level
                FROM const_init_institutions
                WHERE uscc = %s
                ORDER BY name
                LIMIT 5
            """, (dup['uscc'],))
            
            records = cursor.fetchall()
            for j, rec in enumerate(records, 1):
                print(f"   {j}) {rec['name']}")
                print(f"      ID: {rec['id']}, Code: {rec['code']}, 等级: {rec['level'] or '无'}")
            
            if dup['count'] > 5:
                print(f"   ... 还有{dup['count']-5}条记录")
            print()
    else:
        print(f"\nNO: No duplicate USCC found")
        print(f"   Branch institutions may not be stored, or were overwritten")
    
    # ==================== Part 4: 平阳县人民医院案例 ====================
    print("\n" + "=" * 100)
    print("Part 4: 平阳县人民医院案例检查")
    print("=" * 100)
    
    cursor.execute("""
        SELECT id, name, code, uscc, level, region
        FROM const_init_institutions
        WHERE name LIKE '%平阳县人民医院%'
        ORDER BY name
    """)
    
    pyxian_records = cursor.fetchall()
    print(f"\n找到 {len(pyxian_records)} 条记录:\n")
    
    if len(pyxian_records) > 0:
        # 按USCC分组
        uscc_groups = {}
        for rec in pyxian_records:
            uscc = rec['uscc']
            if uscc not in uscc_groups:
                uscc_groups[uscc] = []
            uscc_groups[uscc].append(rec)
        
        for uscc, records in uscc_groups.items():
            if len(records) > 1:
                print(f"【共享USCC】: {uscc} (共{len(records)}条记录)")
            else:
                print(f"【独立USCC】: {uscc}")
            
            for rec in records:
                print(f"   - {rec['name']}")
                print(f"     ID: {rec['id']}")
                print(f"     Code: {rec['code']}")
                print(f"     等级: {rec['level'] or '无'}")
                print(f"     地区: {rec['region'] or '无'}")
                print()
    else:
        print("未找到相关记录")
    
    # ==================== Part 5: 检查卫生室/门诊部 ====================
    print("\n" + "=" * 100)
    print("Part 5: 检查挂靠的小型医疗机构")
    print("=" * 100)
    
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM const_init_institutions
        WHERE name LIKE '%卫生室%' 
           OR name LIKE '%门诊部%' 
           OR name LIKE '%医务室%'
           OR name LIKE '%卫生所%'
    """)
    
    small_count = cursor.fetchone()['count']
    print(f"\n卫生室/门诊部/医务室/卫生所 总数: {small_count}")
    
    # 随机抽取几个样本
    cursor.execute("""
        SELECT id, name, code, uscc, level
        FROM const_init_institutions
        WHERE name LIKE '%卫生室%'
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    if samples:
        print(f"\n随机抽取10个卫生室样本:")
        for i, s in enumerate(samples, 1):
            print(f"{i}. {s['name']}")
            print(f"   USCC: {s['uscc']}, 等级: {s['level'] or '无'}")
        
        # 检查这些样本的USCC是否有重复
        print(f"\n检查这些卫生室的USCC是否共享:")
        uscc_list = [s['uscc'] for s in samples]
        for uscc in uscc_list[:3]:  # 只检查前3个
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM const_init_institutions
                WHERE uscc = %s
            """, (uscc,))
            count = cursor.fetchone()['count']
            if count > 1:
                print(f"   USCC {uscc}: {count} records (has branches)")
            else:
                print(f"   USCC {uscc}: 1 record only (independent)")
    
    # ==================== Part 6: 总结 ====================
    print("\n" + "=" * 100)
    print("Part 6: 总结")
    print("=" * 100)
    
    print(f"""
数据库约束情况:
- PRIMARY KEY: {'存在' if has_pk else '不存在'}
- UNIQUE KEY uk_code: {'存在' if has_uk_code else '不存在'}
- UNIQUE KEY uk_uscc: {'存在' if has_uk_uscc else '不存在'}

重复USCC情况:
- 有重复USCC的数量: {len(duplicates)}
- 总USCC数: {uscc_stats['unique_uscc']}
- 总记录数: {uscc_stats['total_records']}

挂靠机构入库情况:
- 小型医疗机构数量: {small_count}
- Are branches stored: {'YES' if len(duplicates) > 0 else 'NO'}

结论:
""")
    
    if has_uk_uscc and len(duplicates) > 0:
        print("CONFLICT: uk_uscc constraint exists BUT duplicate USCC found")
        print("   Possible: constraint added after import, or disabled")
    elif has_uk_uscc and len(duplicates) == 0:
        print("EXPECTED: uk_uscc constraint exists and no duplicate USCC")
        print("   Branch institutions cannot share USCC with this constraint")
    elif not has_uk_uscc and len(duplicates) > 0:
        print("CORRECT: No uk_uscc constraint and duplicate USCC exists")
        print("   This design supports branch institutions sharing parent USCC")
    else:
        print("POSSIBLE: No uk_uscc constraint but no duplicate USCC")
        print("   Branch institutions may not be imported yet")
    
    cursor.close()
    conn.close()
    
    print("\n检查完成！")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
