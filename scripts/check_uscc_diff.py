import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

cases = [
    (698,  '蔡斌',   '浙江大学医学院附属邵逸夫医院', '绍兴市人民医院'),
    (708,  '杨春波', '浙江大学医学院附属妇产科医院', '宁波市镇海区人民医院'),
    (919,  '陈丽萍', '杭州市临平区妇幼保健院',       '宁波大学附属妇女儿童医院'),
    (495,  '汪芳',   '宁波大学附属妇女儿童医院',     '杭州市富阳区中医院'),
    (1105, '王婷婷', '象山县红十字台胞医院',         '温州市中医院'),
    (832,  '王惠',   '绍兴市人民医院',               '杭州市富阳区第一人民医院'),
    (1213, '陈婷婷', '浙江省台州医院',               '永嘉县人民医院'),
    (821,  '徐丹',   '台州市第一人民医院',           '安吉县妇幼保健院'),
    (804,  '潘红英', '丽水市中心医院',               '浙江大学医学院附属邵逸夫医院'),
]

print(f"{'uid':>5}  {'姓名':^6}  {'当前机构':^22}  {'当前USCC':^20}  {'历史机构':^22}  {'历史USCC':^20}  {'USCC相同?'}")
print("-" * 130)

for uid, name, curr_inst, his_inst in cases:
    # 当前机构 USCC 从 institutions 表
    cur.execute(
        "SELECT uscc FROM institutions WHERE name COLLATE utf8mb4_general_ci = %s LIMIT 1",
        (curr_inst,)
    )
    row = cur.fetchone()
    curr_uscc = row[0] if row else 'NOT FOUND'

    # 历史机构 USCC 从 const_init_institutions 表
    cur.execute(
        "SELECT uscc FROM const_init_institutions WHERE name COLLATE utf8mb4_general_ci = %s LIMIT 1",
        (his_inst,)
    )
    row = cur.fetchone()
    his_uscc = row[0] if row else 'NOT FOUND'

    same = '✅ 同USCC' if curr_uscc == his_uscc and curr_uscc != 'NOT FOUND' else ('❌ 不同' if 'NOT FOUND' not in (curr_uscc, his_uscc) else '⚠️ 未找到')
    print(f"{uid:>5}  {name:^6}  {curr_inst:^22}  {curr_uscc:^20}  {his_inst:^22}  {his_uscc:^20}  {same}")

conn.close()
