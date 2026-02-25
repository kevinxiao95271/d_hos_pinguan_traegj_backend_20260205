#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入医疗机构数据
"""
import pandas as pd
import pymysql
from datetime import datetime
import re

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# Excel文件路径
EXCEL_PATH = r"D:\iWork\iYuo\浙江\品管大赛\工作群文件\2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx"

def is_valid_uscc(uscc):
    """检查USCC是否有效"""
    if pd.isna(uscc) or not uscc:
        return False
    uscc = str(uscc).strip()
    # 排除无效的USCC
    invalid_patterns = [
        r'^\*+$',  # 全是星号
        r'^0+$',   # 全是0
        r'^1+$',   # 全是1
        r'^[0-9]{1,10}$',  # 太短的纯数字
    ]
    for pattern in invalid_patterns:
        if re.match(pattern, uscc):
            return False
    # 有效的USCC应该是15-18位的字母数字组合
    if len(uscc) < 15 or len(uscc) > 18:
        return False
    return True

def generate_code(name, region, index):
    """生成机构代码"""
    # 使用拼音首字母 + 地区代码 + 序号
    # 这里简化处理，使用机构名称的hash值
    import hashlib
    hash_str = hashlib.md5(f"{name}{region}{index}".encode()).hexdigest()[:8]
    return f"INST_{hash_str}".upper()

def clean_and_prepare_data(df):
    """清理和准备数据"""
    print("\n" + "=" * 100)
    print("数据清理和准备")
    print("=" * 100)
    
    total_rows = len(df)
    print(f"\n原始数据行数: {total_rows}")
    
    # 显示原始列名
    print(f"\n原始列名: {list(df.columns)}")
    
    # 重命名列 - 先去除可能的空格
    df.columns = df.columns.str.strip()
    
    # 创建列名映射
    column_mapping = {}
    for col in df.columns:
        if '机构名称' in col or '名称' == col:
            column_mapping[col] = 'name'
        elif '级别' in col:
            column_mapping[col] = 'level'  # 这个级别是省级、市级等
        elif '区' in col or '市' in col or '县' in col:
            column_mapping[col] = 'region'
        elif '机构类型' in col or '类型' == col:
            column_mapping[col] = 'category'
        elif '机构等级' in col or '等级' in col:
            column_mapping[col] = 'grade'  # 这个等级是三甲、二甲等
        elif '经营' in col:
            column_mapping[col] = 'business_type'
        elif '信用代码' in col:
            column_mapping[col] = 'uscc'
    
    print(f"列名映射: {column_mapping}")
    df = df.rename(columns=column_mapping)
    
    # 确保必要的列存在
    required_cols = ['name', 'uscc']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"缺少必要的列: {col}")
    
    # 1. 处理机构名称
    df['name'] = df['name'].fillna('').str.strip()
    df = df[df['name'] != '']
    print(f"移除空机构名称后: {len(df)} 行")
    
    # 2. 处理USCC
    df['uscc'] = df['uscc'].astype(str).str.strip()
    df['uscc_valid'] = df['uscc'].apply(is_valid_uscc)
    
    valid_uscc_count = df['uscc_valid'].sum()
    print(f"有效USCC数量: {valid_uscc_count}")
    print(f"无效USCC数量: {len(df) - valid_uscc_count}")
    
    # 只保留有效USCC的记录
    df_valid = df[df['uscc_valid']].copy()
    print(f"保留有效USCC后: {len(df_valid)} 行")
    
    # 3. 处理USCC重复
    # 保留第一条，移除重复
    df_dedup = df_valid.drop_duplicates(subset=['uscc'], keep='first')
    removed_dup = len(df_valid) - len(df_dedup)
    if removed_dup > 0:
        print(f"移除USCC重复记录: {removed_dup} 行")
    
    # 4. 处理机构名称重复（同一个USCC下的机构名称应该相同）
    # 如果有不同机构名称但USCC相同的情况，优先保留第一条
    
    # 5. 生成机构代码
    df_dedup['code'] = df_dedup.apply(
        lambda row: generate_code(row['name'], row.get('region', ''), row.name),
        axis=1
    )
    
    # 6. 处理地区
    df_dedup['region'] = df_dedup['region'].fillna('').str.strip()
    df_dedup.loc[df_dedup['region'] == '', 'region'] = None
    
    # 7. 处理等级（将grade字段映射到level）
    # 机构等级可能是：三甲、三乙、二甲、二乙等
    if 'grade' in df_dedup.columns:
        df_dedup['level'] = df_dedup['grade'].fillna('').str.strip()
        df_dedup.loc[df_dedup['level'] == '', 'level'] = None
        df_dedup.loc[df_dedup['level'] == '未定等', 'level'] = None
    elif 'level' not in df_dedup.columns:
        # 如果既没有grade也没有level，就创建一个空的level列
        df_dedup['level'] = None
    
    # 8. 添加创建时间
    df_dedup['created_at'] = datetime.now()
    
    # 9. 选择需要的列
    df_final = df_dedup[['name', 'code', 'uscc', 'region', 'level', 'created_at']].copy()
    
    print(f"\n最终数据行数: {len(df_final)}")
    print(f"  - 有地区信息: {df_final['region'].notna().sum()}")
    print(f"  - 有等级信息: {df_final['level'].notna().sum()}")
    
    # 显示地区分布
    if df_final['region'].notna().any():
        print(f"\n地区分布（前10）:")
        for region, count in df_final['region'].value_counts().head(10).items():
            print(f"  {region}: {count}")
    
    # 显示等级分布
    if df_final['level'].notna().any():
        print(f"\n等级分布:")
        for level, count in df_final['level'].value_counts().items():
            print(f"  {level}: {count}")
    
    return df_final

def ensure_level_column(cursor):
    """确保institutions表有level字段"""
    print("\n" + "=" * 100)
    print("检查表结构")
    print("=" * 100)
    
    # 检查是否存在level字段
    cursor.execute("SHOW COLUMNS FROM institutions LIKE 'level'")
    result = cursor.fetchone()
    
    if not result:
        print("\nlevel字段不存在，正在添加...")
        cursor.execute("""
            ALTER TABLE institutions 
            ADD COLUMN level VARCHAR(32) NULL AFTER region
        """)
        print("[OK] level字段添加成功")
    else:
        print("\n[OK] level字段已存在")

def import_data(df, conn):
    """导入数据到数据库"""
    print("\n" + "=" * 100)
    print("导入数据")
    print("=" * 100)
    
    cursor = conn.cursor()
    
    # 确保表结构正确
    ensure_level_column(cursor)
    conn.commit()
    
    # 准备插入语句
    insert_sql = """
        INSERT INTO institutions (name, code, uscc, region, level, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            region = VALUES(region),
            level = VALUES(level)
    """
    
    success_count = 0
    error_count = 0
    
    print(f"\n开始导入 {len(df)} 条记录...")
    
    for idx, row in df.iterrows():
        try:
            # 将NaN转换为None
            region = row['region'] if pd.notna(row['region']) else None
            level = row['level'] if pd.notna(row['level']) else None
            
            cursor.execute(insert_sql, (
                row['name'],
                row['code'],
                row['uscc'],
                region,
                level,
                row['created_at']
            ))
            success_count += 1
            
            if (idx + 1) % 1000 == 0:
                conn.commit()
                print(f"  已处理: {idx + 1}/{len(df)}")
        
        except Exception as e:
            error_count += 1
            print(f"  错误 (行{idx}): {e}")
            if error_count >= 10:
                print("  错误过多，停止导入")
                break
    
    conn.commit()
    cursor.close()
    
    print(f"\n导入完成:")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    
    return success_count, error_count

def verify_import(conn):
    """验证导入结果"""
    print("\n" + "=" * 100)
    print("验证导入结果")
    print("=" * 100)
    
    cursor = conn.cursor()
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM institutions")
    total = cursor.fetchone()[0]
    print(f"\n总记录数: {total}")
    
    # 地区分布
    cursor.execute("""
        SELECT region, COUNT(*) as cnt 
        FROM institutions 
        WHERE region IS NOT NULL 
        GROUP BY region 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    print(f"\n地区分布（前10）:")
    for region, cnt in cursor.fetchall():
        print(f"  {region}: {cnt}")
    
    # 等级分布
    cursor.execute("""
        SELECT level, COUNT(*) as cnt 
        FROM institutions 
        WHERE level IS NOT NULL 
        GROUP BY level 
        ORDER BY cnt DESC
    """)
    print(f"\n等级分布:")
    for level, cnt in cursor.fetchall():
        print(f"  {level}: {cnt}")
    
    # 示例数据
    cursor.execute("SELECT id, name, uscc, region, level FROM institutions LIMIT 5")
    print(f"\n示例数据（前5条）:")
    for row in cursor.fetchall():
        id_, name, uscc, region, level = row
        print(f"  ID={id_}, 名称={name[:20]}, USCC={uscc}, 地区={region}, 等级={level}")
    
    cursor.close()

def main():
    print("=" * 100)
    print("医疗机构数据导入工具")
    print("=" * 100)
    
    # 1. 读取Excel文件
    print(f"\n正在读取Excel文件...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=0)
    print(f"[OK] 读取成功: {len(df)} 行, {len(df.columns)} 列")
    
    # 2. 清理和准备数据
    df_clean = clean_and_prepare_data(df)
    
    # 3. 连接数据库
    print(f"\n正在连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    print(f"[OK] 连接成功")
    
    try:
        # 4. 导入数据
        success, error = import_data(df_clean, conn)
        
        # 5. 验证结果
        if success > 0:
            verify_import(conn)
    
    finally:
        conn.close()
    
    print("\n" + "=" * 100)
    print("完成!")
    print("=" * 100)

if __name__ == '__main__':
    main()
