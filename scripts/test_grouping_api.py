#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试面谈分组和书审分组接口"""

import requests
import json
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=== 1. 检查数据库表结构 ===\n")

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 查看 institutions 表结构
print("institutions 表结构:")
cursor.execute("DESCRIBE institutions")
for col in cursor.fetchall():
    print(f"  {col[0]}: {col[1]}")

print()

# 查看 registrations 表结构
print("registrations 表结构:")
cursor.execute("DESCRIBE registrations")
for col in cursor.fetchall():
    print(f"  {col[0]}: {col[1]}")

print()

# 查看是否有机构等级数据
print("查看 institutions 表的样例数据:")
cursor.execute("SELECT * FROM institutions LIMIT 3")
cursor.execute("SHOW COLUMNS FROM institutions")
columns = [col[0] for col in cursor.fetchall()]
cursor.execute("SELECT * FROM institutions LIMIT 3")
for row in cursor.fetchall():
    print(f"\n  机构:")
    for i, col in enumerate(columns):
        print(f"    {col}: {row[i]}")

cursor.close()
conn.close()

print("\n" + "="*50)
print("=== 2. 测试API接口 ===\n")

# 登录
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post("http://localhost:6031/api/auth/login", json=login_data)
token = response.json()['data']['token']
print(f"✓ 登录成功\n")

headers = {"Authorization": f"Bearer {token}"}

# 获取赛事列表
print("获取赛事列表...")
response = requests.get("http://localhost:6031/api/competitions", headers=headers)
competitions = response.json()
if competitions.get('success') and competitions.get('data'):
    comp_list = competitions['data']
    print(f"找到 {len(comp_list)} 个赛事")
    if comp_list:
        competition_id = comp_list[0]['id']
        print(f"使用赛事ID: {competition_id}\n")
        
        # 测试面谈分组接口
        print("=== 测试面谈分组接口 ===")
        url = f"http://localhost:6031/api/admin/registrations/interview-groups?competitionId={competition_id}"
        print(f"URL: {url}\n")
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"success: {result.get('success')}")
        
        if result.get('success') and result.get('data'):
            groups = result['data']
            print(f"分组数量: {len(groups)}\n")
            
            if groups:
                print("第一个分组的数据结构:")
                print(json.dumps(groups[0], indent=2, ensure_ascii=False))
                
                if groups[0].get('items'):
                    print("\n第一个分组的第一个项目:")
                    print(json.dumps(groups[0]['items'][0], indent=2, ensure_ascii=False))
                    
                    # 检查是否有机构等级字段
                    item = groups[0]['items'][0]
                    print(f"\n字段列表: {list(item.keys())}")
                    
                    if 'institutionLevel' in item:
                        print(f"✓ 有 institutionLevel 字段")
                    else:
                        print(f"✗ 没有 institutionLevel 字段")
        else:
            print(f"错误: {result.get('message')}")
else:
    print("未找到赛事")
