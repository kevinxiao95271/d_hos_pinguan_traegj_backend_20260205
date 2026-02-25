# -*- coding: utf-8 -*-
"""
简单测试登录
"""
import requests
import json

BASE_URL = "http://localhost:6031"

print("测试登录API")
print("=" * 80)

# 测试1: POST /api/auth/login-with-password
print("\n[测试1] POST /api/auth/login-with-password")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login-with-password",
        json={
            "phone": "13600001234",
            "password": "test001234"
        },
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers.get('Content-Type')}")
    print(f"响应体: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n解析后的JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 查询王可心的报名记录（直接从数据库）
print("\n\n[测试2] 查询数据库中的报名记录")
try:
    import pymysql
    
    db_config = {
        'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
        'port': 63606,
        'user': 'root',
        'password': 'Yiguo9527_',
        'database': 'd_hos_pinguan_traegj_20260205',
        'charset': 'utf8mb4'
    }
    
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 查询王可心的报名
    cursor.execute("""
        SELECT 
            r.id,
            r.project_name,
            r.status,
            r.competition_id,
            c.name as competition_name,
            r.institution_id,
            i.name as institution_name
        FROM registrations r
        LEFT JOIN competitions c ON r.competition_id = c.id
        LEFT JOIN institutions i ON r.institution_id = i.id
        WHERE r.applicant_id = 9
        ORDER BY r.id DESC
    """)
    
    registrations = cursor.fetchall()
    
    if registrations:
        print(f"找到 {len(registrations)} 个报名记录:")
        for reg in registrations:
            print(f"\n  报名ID: {reg[0]}")
            print(f"  项目名: {reg[1]}")
            print(f"  状态: {reg[2]}")
            print(f"  赛事ID: {reg[3]}")
            print(f"  赛事名: {reg[4]}")
            print(f"  机构ID: {reg[5]}")
            print(f"  机构名: {reg[6]}")
    else:
        print("  没有找到报名记录")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
