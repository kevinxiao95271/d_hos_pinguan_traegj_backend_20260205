# -*- coding: utf-8 -*-
"""
验证Excel文件并根据Excel数据修复字典表
"""
import pandas as pd
import requests
import os
import sys

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("验证Excel文件并修复等级字典")
print("=" * 100)

# 1. 查找Excel文件
print("\n[步骤1] 查找Excel文件...")
print("-" * 100)

excel_paths = [
    r"2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
    r"./2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx",
    r"医疗机构目录.xlsx",
    r"./医疗机构目录.xlsx",
]

excel_file = None
for path in excel_paths:
    if os.path.exists(path):
        excel_file = path
        print(f"找到Excel文件: {path}")
        break

if not excel_file:
    print("\n[错误] 找不到Excel文件")
    print("\n请将文件复制到项目根目录:")
    print('  copy "D:\\iWork\\iYuo\\浙江\\品管大赛\\工作群文件\\2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx" "D:\\AiCode\\cursor\\d_hos_pinguan_traegj_backend_20260205\\"')
    print("\n或者重命名为: 医疗机构目录.xlsx")
    sys.exit(1)

# 2. 读取Excel文件
print(f"\n[步骤2] 读取Excel文件...")
print("-" * 100)

try:
    # 尝试读取所有sheet
    xl_file = pd.ExcelFile(excel_file)
    print(f"Excel文件包含 {len(xl_file.sheet_names)} 个sheet:")
    for i, sheet in enumerate(xl_file.sheet_names):
        print(f"  [{i+1}] {sheet}")
    
    # 读取第一个sheet
    df = pd.read_excel(excel_file, sheet_name=0)
    print(f"\n成功读取第一个sheet: {xl_file.sheet_names[0]}")
    print(f"  总行数: {len(df)}")
    print(f"  总列数: {len(df.columns)}")
    
    print(f"\n  列名:")
    for i, col in enumerate(df.columns):
        sample_value = df[col].dropna().head(1).values
        sample = sample_value[0] if len(sample_value) > 0 else "空"
        print(f"    [{i+1}] {col:<30} 样本值: {str(sample)[:50]}")
    
except Exception as e:
    print(f"读取Excel文件失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 识别等级列
print(f"\n[步骤3] 识别等级列...")
print("-" * 100)

level_col = None
for col in df.columns:
    col_str = str(col).lower()
    if '等级' in col_str or 'level' in col_str or '级别' in col_str:
        level_col = col
        print(f"找到等级列: {col}")
        break

if not level_col:
    print("\n未自动识别到等级列，请手动选择:")
    for i, col in enumerate(df.columns):
        print(f"  [{i+1}] {col}")
    
    choice = input("\n请输入列编号 (直接回车使用列名包含'医疗'的列): ")
    if choice.strip():
        level_col = df.columns[int(choice) - 1]
    else:
        # 尝试找包含"医疗"的列附近的列
        for i, col in enumerate(df.columns):
            if '医疗' in str(col) and i + 1 < len(df.columns):
                level_col = df.columns[i + 1]
                print(f"使用列: {level_col}")
                break

if not level_col:
    level_col = df.columns[0]
    print(f"使用第一列: {level_col}")

# 4. 分析Excel中的等级数据
print(f"\n[步骤4] 分析Excel中的等级分布...")
print("-" * 100)

# 统计等级分布
excel_levels = df[level_col].value_counts().sort_index()

print(f"\nExcel中的等级数据统计:")
print(f"  等级列: {level_col}")
print(f"  总机构数: {len(df)}")
print(f"  有等级数据: {df[level_col].count()}")
print(f"  空值数: {df[level_col].isna().sum()}")
print(f"  不同等级数: {len(excel_levels)}")

print(f"\n  详细分布:")
print(f"  {'等级':<20} {'数量':<10} {'占比':<10}")
print(f"  {'-'*20} {'-'*10} {'-'*10}")

total = df[level_col].count()
for level, count in excel_levels.items():
    if pd.notna(level):
        percent = count * 100 / total
        print(f"  {str(level):<20} {count:<10} {percent:>6.2f}%")

# 提取实际存在的等级（去除空值）
excel_level_list = [str(level) for level in excel_levels.index if pd.notna(level)]

print(f"\n  Excel中存在的等级列表:")
for level in excel_level_list:
    print(f"    - {level}")

# 5. 获取当前数据库等级数据
print(f"\n[步骤5] 获取当前数据库等级数据...")
print("-" * 100)

try:
    response = requests.get(f"{BASE_URL}/institutions/levels", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            db_levels = data.get('data', [])
            print(f"数据库中的等级: {len(db_levels)} 种")
            for level in db_levels:
                print(f"    - {level}")
    else:
        print(f"获取数据库等级失败: HTTP {response.status_code}")
        db_levels = []
        
except Exception as e:
    print(f"获取数据库等级出错: {e}")
    db_levels = []

# 6. 获取字典表数据
print(f"\n[步骤6] 获取字典表中的等级数据...")
print("-" * 100)

try:
    response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            dict_items = data.get('data', [])
            print(f"字典表中的等级: {len(dict_items)} 种")
            
            dict_levels = {}
            for item in dict_items:
                code = item.get('code')
                label = item.get('label')
                item_id = item.get('id')
                dict_levels[code] = {'id': item_id, 'label': label}
                print(f"    - {code:<15} (label: {label}, id: {item_id})")
    else:
        print(f"获取字典等级失败: HTTP {response.status_code}")
        dict_items = []
        dict_levels = {}
        
except Exception as e:
    print(f"获取字典等级出错: {e}")
    dict_items = []
    dict_levels = {}

# 7. 对比分析
print(f"\n[步骤7] 对比分析")
print("=" * 100)

excel_set = set(excel_level_list)
dict_set = set(dict_levels.keys())
db_set = set(db_levels)

print(f"\n各数据源等级对比:")
print(f"  Excel:    {sorted(excel_set)}")
print(f"  数据库:   {sorted(db_set)}")
print(f"  字典表:   {sorted(dict_set)}")

# 字典表需要删除的等级
to_delete = dict_set - excel_set
if to_delete:
    print(f"\n[需要删除] 字典表中有但Excel中没有的等级 ({len(to_delete)} 种):")
    for level in sorted(to_delete):
        item_id = dict_levels[level]['id']
        label = dict_levels[level]['label']
        print(f"    - {level:<15} (label: {label}, id: {item_id})")
else:
    print(f"\n[OK] 字典表中没有多余的等级")

# 字典表需要添加的等级
to_add = excel_set - dict_set
if to_add:
    print(f"\n[需要添加] Excel中有但字典表中缺失的等级 ({len(to_add)} 种):")
    for level in sorted(to_add):
        count = excel_levels.get(level, 0)
        print(f"    - {level:<15} (Excel中有 {count} 个)")
else:
    print(f"\n[OK] Excel中的所有等级都在字典表中")

# 8. 询问是否执行修复
print(f"\n[步骤8] 修复确认")
print("=" * 100)

if not to_delete and not to_add:
    print("\n[太棒了] 字典表与Excel完全一致，无需修复！")
    sys.exit(0)

print(f"\n修复计划:")
if to_delete:
    print(f"  - 删除 {len(to_delete)} 个多余的等级: {sorted(to_delete)}")
if to_add:
    print(f"  - 添加 {len(to_add)} 个缺失的等级: {sorted(to_add)}")

confirm = input("\n是否执行修复? (yes/no): ")

if confirm.lower() not in ['yes', 'y']:
    print("取消修复，退出")
    sys.exit(0)

# 9. 执行修复
print(f"\n[步骤9] 执行修复...")
print("-" * 100)

# 登录
print("\n登录管理员账号...")
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200 or not login_response.json().get('success'):
    print("登录失败！")
    sys.exit(1)

token = login_response.json()['data']['token']
print("登录成功！")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 删除多余的等级
if to_delete:
    print(f"\n删除多余的等级...")
    for level in sorted(to_delete):
        item_id = dict_levels[level]['id']
        try:
            response = requests.delete(
                f"{BASE_URL}/dictionaries/{item_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  [OK] 已删除: {level}")
                else:
                    print(f"  [FAIL] 删除失败: {level} - {data.get('message')}")
            else:
                print(f"  [FAIL] 删除失败: {level} - HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] 删除出错: {level} - {e}")

# 添加缺失的等级
if to_add:
    print(f"\n添加缺失的等级...")
    for level in sorted(to_add):
        try:
            response = requests.post(
                f"{BASE_URL}/dictionaries",
                headers=headers,
                json={
                    "type": "institution_level",
                    "code": level,
                    "label": level,  # label和code相同
                    "status": "ACTIVE"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  [OK] 已添加: {level}")
                else:
                    print(f"  [FAIL] 添加失败: {level} - {data.get('message')}")
            else:
                print(f"  [FAIL] 添加失败: {level} - HTTP {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] 添加出错: {level} - {e}")

# 10. 验证修复结果
print(f"\n[步骤10] 验证修复结果...")
print("-" * 100)

try:
    response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            new_dict_items = data.get('data', [])
            new_dict_codes = [item.get('code') for item in new_dict_items]
            
            print(f"\n修复后字典表中的等级 ({len(new_dict_items)} 种):")
            for item in new_dict_items:
                print(f"    - {item.get('code'):<15} (label: {item.get('label')})")
            
            # 验证是否与Excel一致
            new_dict_set = set(new_dict_codes)
            
            if new_dict_set == excel_set:
                print(f"\n[成功] 字典表已与Excel完全一致！")
            else:
                missing = excel_set - new_dict_set
                extra = new_dict_set - excel_set
                
                if missing:
                    print(f"\n[警告] 仍有缺失: {missing}")
                if extra:
                    print(f"\n[警告] 仍有多余: {extra}")
                    
except Exception as e:
    print(f"验证失败: {e}")

print("\n" + "=" * 100)
print("完成")
print("=" * 100)
