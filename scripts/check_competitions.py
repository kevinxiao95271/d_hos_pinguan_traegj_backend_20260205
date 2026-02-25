# -*- coding: utf-8 -*-
"""
查询赛事并创建测试赛事
"""
import pymysql
from datetime import datetime, timedelta

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

# 查询现有赛事
cursor.execute("SELECT id, name, stage FROM competitions ORDER BY id")
competitions = cursor.fetchall()

if competitions:
    print("现有赛事:")
    for comp in competitions:
        print(f"  ID: {comp[0]}, 名称: {comp[1]}, 阶段: {comp[2]}")
else:
    print("没有赛事，创建测试赛事...")
    
    now = datetime.now()
    register_start = now - timedelta(days=30)
    register_end = now + timedelta(days=30)
    
    cursor.execute("""
        INSERT INTO competitions 
        (name, stage, register_start, register_end, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        "2026浙江省品管大赛",
        "REGISTRATION",
        register_start,
        register_end,
        now
    ))
    conn.commit()
    
    comp_id = cursor.lastrowid
    print(f"已创建测试赛事，ID: {comp_id}")

cursor.close()
conn.close()
