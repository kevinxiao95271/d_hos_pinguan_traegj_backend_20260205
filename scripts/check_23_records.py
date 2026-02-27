# -*- coding: utf-8 -*-
"""
检查那23条USCC不为空但显示未导入的记录
看看它们是否真的在DB中
"""
import pandas as pd
import pymysql
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# 这23条记录的名字和USCC
records_to_check = [
    ('浙一医院潘方仁分院', '12330000470003222e'),
    ('淳安县浪川乡卫生院双源分院', '12330127470421969l'),
    ('浙江省皮肤病医院拱墅区综合门诊部', '12330000470051814x'),
    ('建德市大洋镇卫生院', '12330182470483684p'),
    ('建德市李家镇卫生院', '1233018247048373XM'),
    ('建德市更楼街道桥岭村卫生室', '12330182470483676w'),
    ('建德市乾潭镇下包村卫生室', '12330182470483721x'),
    ('宁波市海曙区古林镇古林村卫生室', '12330227419611847l'),
    ('宁海县前童镇卫生院', '12330226419591989h'),
    ('宁海县梅林街道社区卫生服务中心', '12330226419591831X'),
    ('宁海县越溪乡七市村卫生室', '12330226419591874B'),
    ('温州市瓯海区泽雅镇周岙村卫生室', '12330304470621338h'),
    ('嘉善县姚庄镇卫生院', '12330421471000031K'),
    ('嘉兴市秀洲区洪合镇民和社区卫生服务站', '12330411740524176C'),
    ('嘉兴市秀洲区王江泾镇市泾村卫生室', '12330411470970108k'),
    ('义乌市后宅街道金城社区卫生服务站', '12330782471771901X'),
    ('永康市唐先镇雅堂村长塘头自然村卫生室', '54330784me0204557d'),
    ('衢州市衢江区廿里镇中心卫生院', '12330821350110058L'),
    ('普陀区沈家门街道社区卫生服务中心西大社区卫生服务站', '12330903472170315M'),
    ('三门县健跳镇毛叶村卫生室', '12331022769610107p'),
    ('路桥区金清镇德升村卫生室', '12331004472710174T'),
    ('台州市中心医院', '12331000MB0X59176W'),
    ('松阳县玉岩镇大树村卫生室', '12332528472520258C'),
]

print("=" * 100)
print("检查23条记录是否真的在DB中")
print("=" * 100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    found_in_db = 0
    not_found_in_db = 0
    
    print(f"\n{'序号':<5} {'机构名称':<45} {'Excel USCC':<20} {'DB状态':<10}")
    print("-" * 100)
    
    for idx, (name, uscc) in enumerate(records_to_check, 1):
        # 精确匹配
        cursor.execute("""
            SELECT id, name, uscc, level 
            FROM const_init_institutions 
            WHERE name = %s AND uscc = %s
        """, (name, uscc))
        
        result = cursor.fetchone()
        
        name_display = name[:43] if len(name) > 43 else name
        uscc_display = uscc[:18]
        
        if result:
            found_in_db += 1
            db_id, db_name, db_uscc, db_level = result
            status = f"[存在] ID={db_id}"
            print(f"{idx:<5} {name_display:<45} {uscc_display:<20} {status:<10}")
        else:
            not_found_in_db += 1
            status = "[不存在]"
            print(f"{idx:<5} {name_display:<45} {uscc_display:<20} {status:<10}")
            
            # 检查是否只是USCC大小写不同
            cursor.execute("""
                SELECT id, name, uscc 
                FROM const_init_institutions 
                WHERE name = %s AND LOWER(uscc) = LOWER(%s)
            """, (name, uscc))
            
            case_result = cursor.fetchone()
            if case_result:
                print(f"      -> [大小写不同] DB中的USCC: {case_result[2]}")
    
    print(f"\n统计:")
    print(f"   在DB中找到: {found_in_db} 条")
    print(f"   在DB中未找到: {not_found_in_db} 条")
    
    if not_found_in_db > 0:
        print(f"\n这{not_found_in_db}条记录是真正未导入的！")
    
finally:
    cursor.close()
    conn.close()

print(f"\n检查完成！")
