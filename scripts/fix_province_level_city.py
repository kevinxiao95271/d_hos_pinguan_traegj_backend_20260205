# -*- coding: utf-8 -*-
"""
修正city='省级'的三级医院city字段
"""
import pymysql
import sys

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

print("=" * 100)
print("修正city='省级'的三级医院")
print("=" * 100)

conn = pymysql.connect(**db_config)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 查询city='省级'的三级医院
cursor.execute("""
    SELECT id, name, city
    FROM const_init_institutions
    WHERE level = '三级' AND city = '省级'
    ORDER BY name
""")

hospitals = cursor.fetchall()

print(f"\n找到 {len(hospitals)} 家需要修正的医院\n")

# 城市判断规则
city_mapping = {
    '浙江大学': '杭州市',
    '浙江医学院': '杭州市',
    '浙江医院': '杭州市',
    '浙江省': '杭州市',
    '浙江中医药大学': '杭州市',
    '温州医科大学': '温州市',
    '温州': '温州市',
}

update_count = 0

for hospital in hospitals:
    name = hospital['name']
    
    # 推断城市
    new_city = '杭州市'  # 默认省会
    for keyword, city in city_mapping.items():
        if keyword in name:
            new_city = city
            break
    
    # 更新
    sql = "UPDATE const_init_institutions SET city = %s WHERE id = %s"
    cursor.execute(sql, (new_city, hospital['id']))
    update_count += 1
    
    print(f"  [更新] {name[:60]}")
    print(f"         省级 -> {new_city}")

conn.commit()

# 验证
print(f"\n" + "=" * 100)
print("验证结果")
print("=" * 100)

cursor.execute("""
    SELECT COUNT(*) as count
    FROM const_init_institutions
    WHERE level = '三级' AND city = '省级'
""")

result = cursor.fetchone()
print(f"\n更新后，city='省级'的三级医院: {result['count']} 家")
print(f"成功更新: {update_count} 家")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("修正完成")
print("=" * 100)
