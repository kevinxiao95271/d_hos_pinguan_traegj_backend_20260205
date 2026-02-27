# -*- coding: utf-8 -*-
"""
对比Excel数据源和数据库中的医疗机构等级数据
"""
import pandas as pd
import requests
import os
import sys

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("医疗机构等级数据对比分析")
print("=" * 100)

# 1. 检查Excel文件
excel_paths = [
    r"D:\iWork\iYuo\浙江\品管大赛\工作群文件\2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
    r"2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
    r"./2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
    r"./scripts/2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
]

excel_file = None
for path in excel_paths:
    if os.path.exists(path):
        excel_file = path
        print(f"\n[找到Excel文件] {path}")
        break

if not excel_file:
    print("\n[错误] 找不到Excel文件，请将文件放到以下位置之一：")
    for path in excel_paths:
        print(f"  - {path}")
    print("\n或者直接放到项目根目录下")
    sys.exit(1)

# 2. 读取Excel文件
print(f"\n[步骤1] 读取Excel文件...")
print("-" * 100)

try:
    df = pd.read_excel(excel_file)
    print(f"成功读取Excel文件")
    print(f"  总行数: {len(df)}")
    print(f"  总列数: {len(df.columns)}")
    
    print(f"\n  列名:")
    for i, col in enumerate(df.columns):
        print(f"    [{i+1}] {col}")
    
except Exception as e:
    print(f"读取Excel文件失败: {e}")
    sys.exit(1)

# 3. 识别等级列
print(f"\n[步骤2] 识别等级字段...")
print("-" * 100)

level_col = None
possible_names = ['等级', '医院等级', '机构等级', '级别', 'level', '医疗机构等级']

for col in df.columns:
    col_lower = str(col).lower()
    if any(name in col_lower for name in ['等级', 'level', '级别']):
        level_col = col
        print(f"找到等级列: {col}")
        break

if not level_col:
    print("未找到等级列，请从以下列中选择：")
    for i, col in enumerate(df.columns):
        print(f"  [{i+1}] {col}")
    print("\n尝试使用第一列作为等级列...")
    level_col = df.columns[0]

# 4. 分析Excel中的等级数据
print(f"\n[步骤3] 分析Excel中的等级数据...")
print("-" * 100)

excel_levels = df[level_col].value_counts().sort_index()

print(f"\nExcel中的等级分布 (使用列: {level_col}):")
print(f"  不同等级数: {len(excel_levels)}")
print(f"  总机构数: {df[level_col].count()}")
print(f"  空值数: {df[level_col].isna().sum()}")

print(f"\n  详细分布:")
for level, count in excel_levels.items():
    if pd.notna(level):
        print(f"    {level:<20} : {count:>6} 个")

# 5. 获取数据库中的等级数据
print(f"\n[步骤4] 获取数据库中的等级数据...")
print("-" * 100)

try:
    # 使用institutions表的等级列表
    response = requests.get(f"{BASE_URL}/institutions/levels", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            db_levels = data.get('data', [])
            print(f"数据库(institutions)等级列表: {len(db_levels)} 种")
            for level in db_levels:
                print(f"    {level}")
    else:
        print(f"获取数据库等级失败: HTTP {response.status_code}")
        db_levels = []
        
except Exception as e:
    print(f"获取数据库等级出错: {e}")
    db_levels = []

# 获取const_init_institutions的数据进行对比
print(f"\n测试搜索功能，统计实际数据分布...")

test_levels = ['二级', '三级', '二甲', '三甲', '一级', '一甲']
db_level_counts = {}

for level in test_levels:
    try:
        response = requests.post(
            f"{BASE_URL}/institutions/search",
            json={
                "keyword": "",
                "region": "",
                "level": level,
                "page": 0,
                "size": 1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                total = data.get('data', {}).get('totalElements', 0)
                db_level_counts[level] = total
                print(f"  {level:<10} : {total:>6} 个")
    except:
        pass

# 6. 对比分析
print(f"\n[步骤5] 对比分析")
print("=" * 100)

excel_level_set = set([str(level) for level in excel_levels.index if pd.notna(level)])
db_level_set = set(db_levels)

print(f"\nExcel中的等级 ({len(excel_level_set)} 种):")
for level in sorted(excel_level_set):
    count = excel_levels.get(level, 0)
    print(f"  {level:<20} : {count:>6} 个")

print(f"\n数据库中的等级 ({len(db_level_set)} 种):")
for level in sorted(db_level_set):
    db_count = db_level_counts.get(level, '?')
    print(f"  {level:<20} : {db_count:>6} 个")

print(f"\n[对比结果]")
print("-" * 100)

# Excel有但数据库没有
missing_in_db = excel_level_set - db_level_set
if missing_in_db:
    print(f"\n[问题] Excel中有但数据库中缺失的等级 ({len(missing_in_db)} 种):")
    for level in sorted(missing_in_db):
        count = excel_levels.get(level, 0)
        print(f"  {level:<20} : {count:>6} 个 [缺失]")
else:
    print(f"\n[OK] Excel中的所有等级在数据库中都存在")

# 数据库有但Excel没有
extra_in_db = db_level_set - excel_level_set
if extra_in_db:
    print(f"\n[提示] 数据库中有但Excel中没有的等级 ({len(extra_in_db)} 种):")
    for level in sorted(extra_in_db):
        db_count = db_level_counts.get(level, '?')
        print(f"  {level:<20} : {db_count:>6} 个 [额外]")

# 7. 数量对比
print(f"\n[数量对比]")
print("-" * 100)

common_levels = excel_level_set & db_level_set
if common_levels:
    print(f"\n共同等级的数量对比:")
    print(f"  {'等级':<15} {'Excel':<10} {'数据库':<10} {'差异':<10}")
    print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10}")
    
    for level in sorted(common_levels):
        excel_count = excel_levels.get(level, 0)
        db_count = db_level_counts.get(level, '?')
        
        if isinstance(db_count, int):
            diff = db_count - excel_count
            diff_str = f"{diff:+d}"
        else:
            diff_str = "?"
        
        print(f"  {level:<15} {excel_count:<10} {str(db_count):<10} {diff_str:<10}")

# 8. 建议
print(f"\n[建议]")
print("=" * 100)

if missing_in_db:
    print(f"\n需要在数据库中添加以下等级的机构:")
    for level in sorted(missing_in_db):
        count = excel_levels.get(level, 0)
        print(f"  - {level} ({count} 个)")

if extra_in_db:
    print(f"\n数据库中有以下额外等级（可能是旧数据或测试数据）:")
    for level in sorted(extra_in_db):
        print(f"  - {level}")

print("\n" + "=" * 100)
print("对比完成")
print("=" * 100)
