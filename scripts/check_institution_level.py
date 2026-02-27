# -*- coding: utf-8 -*-
"""
检查医院等级数据一致性
"""
import pymysql
import requests

# 数据库连接
db_config = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': 'kevin1234',
    'database': 'pinguan',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("医院等级数据一致性检查")
print("=" * 100)

# 1. 检查字典表中的医院等级数据
print("\n[步骤1] 检查字典表 - 医院等级类型")
print("-" * 100)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 查询医院等级字典
    sql = """
        SELECT code, label, type, status
        FROM dictionary_items
        WHERE type = 'institution_level'
        ORDER BY code
    """
    
    cursor.execute(sql)
    dict_items = cursor.fetchall()
    
    if dict_items:
        print(f"找到 {len(dict_items)} 条医院等级字典数据:")
        for item in dict_items:
            print(f"  code: {item['code']:<20} label: {item['label']:<15} status: {item['status']}")
    else:
        print("  [警告] 字典表中没有 type='institution_level' 的数据！")
    
    # 2. 检查机构表中实际使用的等级值
    print(f"\n[步骤2] 检查机构表 - 实际存储的等级值")
    print("-" * 100)
    
    sql = """
        SELECT DISTINCT level, COUNT(*) as count
        FROM institutions
        GROUP BY level
        ORDER BY count DESC
    """
    
    cursor.execute(sql)
    actual_levels = cursor.fetchall()
    
    print(f"机构表中实际存储的等级值 (共 {len(actual_levels)} 种):")
    for item in actual_levels:
        level = item['level'] if item['level'] else '[NULL/空值]'
        print(f"  {level:<20} - {item['count']} 个机构")
    
    # 3. 对比分析
    print(f"\n[步骤3] 数据一致性分析")
    print("-" * 100)
    
    dict_codes = {item['code'] for item in dict_items}
    actual_level_values = {item['level'] for item in actual_levels if item['level']}
    
    # 检查机构表中的值是否都在字典中
    missing_in_dict = actual_level_values - dict_codes
    if missing_in_dict:
        print(f"\n[问题] 机构表中有 {len(missing_in_dict)} 个等级值不在字典表中:")
        for level in missing_in_dict:
            print(f"  - {level}")
    
    # 检查字典中的值是否都在机构表中使用
    unused_in_institutions = dict_codes - actual_level_values
    if unused_in_institutions:
        print(f"\n[提示] 字典表中有 {len(unused_in_institutions)} 个等级值未被机构使用:")
        for code in unused_in_institutions:
            print(f"  - {code}")
    
    if not missing_in_dict:
        print(f"\n[OK] 所有机构的等级值都在字典表中")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库查询出错: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试API返回的医院等级下拉列表
print(f"\n[步骤4] 测试API - 医院等级下拉列表")
print("-" * 100)

try:
    response = requests.get(
        f"{BASE_URL}/dictionaries/institution_level",
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            items = data.get('data', [])
            print(f"API返回 {len(items)} 个医院等级选项:")
            
            for item in items:
                code = item.get('code', '')
                label = item.get('label', '')
                status = item.get('status', '')
                print(f"  code: {code:<20} label: {label:<15} status: {status}")
        else:
            print(f"API返回失败: {data.get('message')}")
    else:
        print(f"API请求失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"API请求出错: {e}")

print("\n" + "=" * 100)
print("检查完成")
print("=" * 100)
