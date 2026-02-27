# -*- coding: utf-8 -*-
"""
从const_init_institutions导入大型医院到institutions表
并设置level为"三甲"或"二甲"
"""
import pymysql
import random
from datetime import datetime

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

print("=" * 100)
print("从const_init_institutions导入大型医院")
print("=" * 100)

# 1. 查找大型医院（根据名称关键字）
print("\n[1] 查找大型医院...")
cursor.execute("""
    SELECT id, code, name, uscc, region
    FROM const_init_institutions
    WHERE (
        name LIKE '%人民医院' 
        OR name LIKE '%中心医院'
        OR name LIKE '%附属医院'
        OR name LIKE '%第一医院'
        OR name LIKE '%第二医院'
        OR name LIKE '%第三医院'
        OR name LIKE '%省立医院'
        OR name LIKE '%市立医院'
        OR name LIKE '%医学院%'
        OR name LIKE '%医科大学%'
    )
    AND name NOT LIKE '%卫生室%'
    AND name NOT LIKE '%卫生院%'
    AND name NOT LIKE '%诊所%'
    AND name NOT LIKE '%门诊%'
    AND name NOT LIKE '%社区%'
    ORDER BY name
    LIMIT 150
""")

hospitals = cursor.fetchall()
print(f"  找到 {len(hospitals)} 家大型医院")

# 2. 分配医院等级
# 规则：
# - 省级/医学院附属/中心医院 -> 三甲
# - 市级/人民医院/第一医院 -> 三甲或二甲
# - 其他大型医院 -> 二甲

sanjia_keywords = ['省人民医院', '省立医院', '医学院', '医科大学', '附属', '中心医院']
erjia_keywords = ['市人民医院', '市立医院', '第一医院', '第二医院']

hospitals_with_level = []

for id, code, name, uscc, region in hospitals:
    # 判断等级
    level = '二甲'  # 默认二甲
    
    for keyword in sanjia_keywords:
        if keyword in name:
            level = '三甲'
            break
    
    hospitals_with_level.append((id, code, name, uscc, region, level))

# 确保三甲医院占95%左右
sanjia_count = len([h for h in hospitals_with_level if h[5] == '三甲'])
erjia_count = len(hospitals_with_level) - sanjia_count

# 如果三甲不够，随机将一些二甲升为三甲
target_sanjia = int(len(hospitals_with_level) * 0.95)
if sanjia_count < target_sanjia:
    need_more = target_sanjia - sanjia_count
    erjia_hospitals = [(i, h) for i, h in enumerate(hospitals_with_level) if h[5] == '二甲']
    random.shuffle(erjia_hospitals)
    
    for i in range(min(need_more, len(erjia_hospitals))):
        idx, h = erjia_hospitals[i]
        hospitals_with_level[idx] = (h[0], h[1], h[2], h[3], h[4], '三甲')

# 重新统计
sanjia_count = len([h for h in hospitals_with_level if h[5] == '三甲'])
erjia_count = len(hospitals_with_level) - sanjia_count

print(f"\n[2] 医院等级分配:")
print(f"  三甲医院: {sanjia_count} 家 ({sanjia_count/len(hospitals_with_level)*100:.1f}%)")
print(f"  二甲医院: {erjia_count} 家 ({erjia_count/len(hospitals_with_level)*100:.1f}%)")

# 3. 插入到institutions表（如果不存在）
print(f"\n[3] 导入到institutions表...")
imported_count = 0
skipped_count = 0
failed_count = 0

for id, code, name, uscc, region, level in hospitals_with_level:
    try:
        # 检查是否已存在（通过uscc或name）
        cursor.execute("""
            SELECT COUNT(*) FROM institutions 
            WHERE uscc = %s OR name = %s
        """, (uscc, name))
        
        exists = cursor.fetchone()[0] > 0
        
        if not exists:
            cursor.execute("""
                INSERT INTO institutions 
                (code, name, uscc, region, level, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (code, name, uscc, region, level, datetime.now()))
            
            imported_count += 1
            conn.commit()
        else:
            # 更新level
            cursor.execute("""
                UPDATE institutions 
                SET level = %s
                WHERE uscc = %s OR name = %s
            """, (level, uscc, name))
            skipped_count += 1
            conn.commit()
            
    except Exception as e:
        failed_count += 1
        if failed_count <= 5:
            print(f"  导入失败 [{name[:40]}]: {str(e)[:60]}")
        conn.rollback()

print(f"\n[4] 导入结果:")
print(f"  新导入: {imported_count} 家")
print(f"  已存在(更新level): {skipped_count} 家")
print(f"  失败: {failed_count} 家")

# 5. 验证结果
cursor.execute("SELECT COUNT(*) FROM institutions")
total_institutions = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM institutions WHERE level = '三甲'")
final_sanjia = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM institutions WHERE level = '二甲'")
final_erjia = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM institutions WHERE level IS NULL OR level NOT IN ('三甲', '二甲')")
final_other = cursor.fetchone()[0]

print(f"\n[5] 最终统计:")
print(f"  机构总数: {total_institutions}")
print(f"  三甲医院: {final_sanjia} 家 ({final_sanjia/total_institutions*100:.1f}%)")
print(f"  二甲医院: {final_erjia} 家 ({final_erjia/total_institutions*100:.1f}%)")
print(f"  其他/未定级: {final_other} 家 ({final_other/total_institutions*100:.1f}%)")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print("医院导入完成！")
print("=" * 100)
