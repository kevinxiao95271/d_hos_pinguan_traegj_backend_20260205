# -*- coding: utf-8 -*-
"""
删除uk_uscc约束，添加uk_name_uscc约束，导入未导入的6044条记录
"""
import pandas as pd
import pymysql
import os
import uuid

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
excel_file = "2026.1全省医疗机构目录.xlsx"
missing_file = os.path.join(project_root, '最终验证-未导入记录.xlsx')

print("=" * 100, flush=True)
print("导入未导入的机构记录", flush=True)
print("=" * 100, flush=True)

# 从region推断city的函数
def get_city_from_region(region):
    """从region推断city"""
    if pd.isna(region) or region == '':
        return None
    
    region = str(region).strip()
    
    # 浙江省11个地级市
    cities = {
        '杭州': ['杭州', '上城', '拱墅', '西湖', '滨江', '萧山', '余杭', '临平', '钱塘', '富阳', '临安',
                '桐庐', '淳安', '建德'],
        '宁波': ['宁波', '海曙', '江北', '北仑', '镇海', '鄞州', '奉化', '余姚', '慈溪', '宁海', '象山'],
        '温州': ['温州', '鹿城', '龙湾', '瓯海', '洞头', '瑞安', '乐清', '龙港', '永嘉', '平阳', '苍南',
                '文成', '泰顺'],
        '嘉兴': ['嘉兴', '南湖', '秀洲', '海宁', '平湖', '桐乡', '嘉善', '海盐'],
        '湖州': ['湖州', '吴兴', '南浔', '德清', '长兴', '安吉'],
        '绍兴': ['绍兴', '越城', '柯桥', '上虞', '诸暨', '嵊州', '新昌'],
        '金华': ['金华', '婺城', '金东', '兰溪', '义乌', '东阳', '永康', '武义', '浦江', '磐安'],
        '衢州': ['衢州', '柯城', '衢江', '江山', '常山', '开化', '龙游'],
        '舟山': ['舟山', '定海', '普陀', '岱山', '嵊泗'],
        '台州': ['台州', '椒江', '黄岩', '路桥', '温岭', '临海', '玉环', '天台', '仙居', '三门'],
        '丽水': ['丽水', '莲都', '龙泉', '青田', '云和', '庆元', '缙云', '遂昌', '松阳', '景宁']
    }
    
    # 检查region是否包含任何市或县区名
    for city, areas in cities.items():
        for area in areas:
            if area in region:
                return city
    
    return None

# 1. 连接数据库
print("\n[1/6] 连接数据库...", flush=True)
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    # 2. 检查并删除uk_uscc约束
    print("\n[2/6] 修改数据库约束...", flush=True)
    
    # 检查是否存在uk_uscc约束
    cursor.execute("""
        SELECT CONSTRAINT_NAME 
        FROM information_schema.TABLE_CONSTRAINTS 
        WHERE TABLE_SCHEMA = %s 
          AND TABLE_NAME = 'const_init_institutions' 
          AND CONSTRAINT_TYPE = 'UNIQUE'
    """, (DB_CONFIG['database'],))
    
    constraints = cursor.fetchall()
    print(f"   当前唯一约束: {[c[0] for c in constraints]}", flush=True)
    
    # 删除uk_uscc约束
    if any('uk_uscc' in str(c[0]) for c in constraints):
        print("   删除 uk_uscc 约束...", flush=True)
        cursor.execute("ALTER TABLE const_init_institutions DROP KEY uk_uscc")
        conn.commit()
        print("   [OK] uk_uscc 约束已删除", flush=True)
    else:
        print("   [INFO] uk_uscc 约束不存在", flush=True)
    
    # 添加uk_name_uscc约束
    if not any('uk_name_uscc' in str(c[0]) for c in constraints):
        print("   添加 uk_name_uscc (name, uscc) 联合唯一约束...", flush=True)
        cursor.execute("ALTER TABLE const_init_institutions ADD UNIQUE KEY uk_name_uscc (name, uscc)")
        conn.commit()
        print("   [OK] uk_name_uscc 约束已添加", flush=True)
    else:
        print("   [INFO] uk_name_uscc 约束已存在", flush=True)
    
    # 3. 读取Excel完整数据
    print("\n[3/6] 读取Excel数据...", flush=True)
    file_path = os.path.join(project_root, excel_file)
    df_excel = pd.read_excel(file_path)
    
    col_name = 0
    col_region = 1
    col_type = 2
    col_nature = 3
    col_level = 4
    col_business = 5
    col_uscc = 6
    
    print(f"   Excel总记录数: {len(df_excel)}", flush=True)
    
    # 4. 读取未导入记录清单
    print("\n[4/6] 读取未导入记录清单...", flush=True)
    df_missing = pd.read_excel(missing_file)
    print(f"   未导入记录数: {len(df_missing)}", flush=True)
    
    # 创建未导入记录的(名字+USCC)映射
    missing_keys = set(
        df_missing['机构名称'].astype(str).str.strip() + '|||' + 
        df_missing['统一社会信用代码'].astype(str).str.strip()
    )
    
    # 5. 从Excel中提取需要导入的完整记录
    print("\n[5/6] 准备导入数据...", flush=True)
    
    df_excel['名字'] = df_excel.iloc[:, col_name].astype(str).str.strip()
    df_excel['USCC'] = df_excel.iloc[:, col_uscc].astype(str).str.strip()
    df_excel['匹配键'] = df_excel['名字'] + '|||' + df_excel['USCC']
    
    # 筛选出需要导入的记录
    df_to_import = df_excel[df_excel['匹配键'].isin(missing_keys)].copy()
    
    print(f"   准备导入记录数: {len(df_to_import)}", flush=True)
    
    # 处理各字段
    def process_level(level):
        """处理等级字段：空值填"无等级"，有值保持原样"""
        if pd.isna(level):
            return '无等级'
        level_str = str(level).strip()
        if level_str == '' or level_str == 'nan':
            return '无等级'
        return level_str
    
    # 6. 批量导入
    print("\n[6/6] 批量导入数据...", flush=True)
    
    total_imported = 0
    total_failed = 0
    failed_records = []
    
    insert_sql = """
        INSERT INTO const_init_institutions 
        (code, name, region, city, uscc, level, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    
    batch_size = 100
    
    for idx, row in df_to_import.iterrows():
        try:
            name = str(row.iloc[col_name]).strip()
            region = str(row.iloc[col_region]).strip() if pd.notna(row.iloc[col_region]) else None
            uscc = str(row.iloc[col_uscc]).strip()
            level = process_level(row.iloc[col_level])
            
            # 从region推断city
            city = get_city_from_region(region) if region else None
            
            # 生成机构编码
            code = 'INST_' + str(uuid.uuid4()).replace('-', '')[:8].upper()
            
            # 执行插入
            cursor.execute(insert_sql, (code, name, region, city, uscc, level))
            total_imported += 1
            
            # 每100条提交一次
            if total_imported % batch_size == 0:
                conn.commit()
                percent = (total_imported / len(df_to_import)) * 100
                print(f"   进度: {total_imported} / {len(df_to_import)} ({percent:.1f}%)", flush=True)
            
        except Exception as e:
            total_failed += 1
            failed_records.append({
                'name': name,
                'uscc': uscc,
                'error': str(e)
            })
            if total_failed <= 10:
                print(f"   [WARN] 导入失败: {name} - {e}", flush=True)
    
    # 提交剩余的记录
    conn.commit()
    
    print(f"\n   [OK] 导入完成！", flush=True)
    print(f"   成功: {total_imported}", flush=True)
    print(f"   失败: {total_failed}", flush=True)
    
    if total_failed > 0:
        print(f"\n   失败记录示例:", flush=True)
        for fail in failed_records[:10]:
            print(f"      {fail['name']}: {fail['error']}", flush=True)
    
    # 7. 验证导入结果
    print("\n" + "=" * 100, flush=True)
    print("验证导入结果", flush=True)
    print("=" * 100, flush=True)
    
    cursor.execute("SELECT COUNT(*) FROM const_init_institutions")
    total_count = cursor.fetchone()[0]
    print(f"\n   DB当前总记录数: {total_count}", flush=True)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN level IS NULL OR level = '' THEN '[空值]'
                ELSE level 
            END as level_group,
            COUNT(*) as count
        FROM const_init_institutions
        GROUP BY level_group
        ORDER BY count DESC
    """)
    level_distribution = cursor.fetchall()
    
    print(f"\n   等级分布:", flush=True)
    for level, count in level_distribution:
        print(f"      {level}: {count}", flush=True)
    
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM const_init_institutions
        WHERE city IS NOT NULL AND city != ''
    """)
    city_filled = cursor.fetchone()[0]
    print(f"\n   City字段已填充: {city_filled} / {total_count} ({city_filled/total_count*100:.1f}%)", flush=True)
    
    # 生成报告
    report = f"""
导入完成报告
{'=' * 100}

执行时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

[约束修改]
  - 已删除: UNIQUE KEY uk_uscc
  - 已添加: UNIQUE KEY uk_name_uscc (name, uscc)

[导入统计]
  准备导入: {len(df_to_import)}
  成功导入: {total_imported}
  导入失败: {total_failed}

[导入后DB状态]
  总记录数: {total_count}
  City字段已填充: {city_filled} ({city_filled/total_count*100:.1f}%)

[等级分布]
"""
    for level, count in level_distribution:
        report += f"  {level}: {count}\n"
    
    if total_failed > 0:
        report += f"\n[失败记录]\n"
        for fail in failed_records[:20]:
            report += f"  {fail['name']}: {fail['error']}\n"
    
    report += f"\n{'=' * 100}\n"
    
    report_file = os.path.join(project_root, '导入未导入记录报告.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n已生成报告: {report_file}", flush=True)
    
except Exception as e:
    conn.rollback()
    print(f"\n[ERROR] 执行失败: {e}", flush=True)
    raise

finally:
    cursor.close()
    conn.close()

print(f"\n" + "=" * 100, flush=True)
print("完成！", flush=True)
print("=" * 100, flush=True)
