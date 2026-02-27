# -*- coding: utf-8 -*-
"""
检查字典表中method类型的数据
"""
import pymysql
import requests

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("检查字典表method类型数据")
print("=" * 100)

# 1. 检查数据库中的method数据
print("\n[1] 检查数据库dictionary_items表...")
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("""
    SELECT code, label, type, active 
    FROM dictionary_items 
    WHERE type = 'method' 
    ORDER BY code
""")

method_items = cursor.fetchall()
print(f"  type='method'的记录数: {len(method_items)}")

if len(method_items) > 0:
    print(f"\n  前20条method数据:")
    print(f"  {'code':<30} {'label':<30} {'type':<15} {'active'}")
    print("-" * 100)
    for code, label, type_, active in method_items[:20]:
        active_str = "是" if active else "否"
        print(f"  {code:<30} {label:<30} {type_:<15} {active_str}")
else:
    print(f"  [警告] 没有找到type='method'的数据！")

cursor.close()
conn.close()

# 2. 测试API
print(f"\n[2] 测试API: GET /api/dictionaries/method")

try:
    response = requests.get("http://localhost:6031/api/dictionaries/method", timeout=30)
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  响应数据类型: {type(data)}")
        
        if isinstance(data, dict):
            print(f"  响应格式: 对象")
            if 'success' in data:
                print(f"    success: {data.get('success')}")
                if data.get('success') and 'data' in data:
                    items = data['data']
                    print(f"    data数组长度: {len(items) if isinstance(items, list) else 'N/A'}")
                else:
                    print(f"    message: {data.get('message', 'N/A')}")
            else:
                print(f"  响应内容: {str(data)[:200]}")
        elif isinstance(data, list):
            print(f"  响应格式: 数组")
            print(f"  数组长度: {len(data)}")
            if len(data) > 0:
                print(f"\n  前5条数据:")
                for i, item in enumerate(data[:5], 1):
                    print(f"    {i}. code={item.get('code')}, label={item.get('label')}")
        else:
            print(f"  响应格式: 其他({type(data)})")
    else:
        print(f"  请求失败: {response.text[:200]}")
        
except Exception as e:
    print(f"  请求异常: {str(e)}")

print("\n" + "=" * 100)
