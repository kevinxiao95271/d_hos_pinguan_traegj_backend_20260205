import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    UPDATE institutions
    SET region = '吴兴区', city = '湖州'
    WHERE id = 36310
""")
conn.commit()
print(f"测试库更新成功，affected={cur.rowcount}")

cur.execute("SELECT id, name, code, uscc, region, city, level, is_ext FROM institutions WHERE id = 36310")
r = cur.fetchone()
print(f"\n当前记录：")
print(f"  id={r[0]}  name={r[1]}")
print(f"  code={r[2]}  uscc={r[3]}")
print(f"  region={r[4]}  city={r[5]}  level={r[6]}  is_ext={r[7]}")

print(f"""
生产环境 INSERT SQL（幂等）：

INSERT INTO institutions (name, code, uscc, region, city, level, is_ext, created_at)
SELECT '湖州市卫生健康发展中心', '{r[2]}', '12330500MB0269683G', '吴兴区', '湖州', '未定级', 0, NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM institutions
    WHERE uscc = '12330500MB0269683G' AND name = '湖州市卫生健康发展中心'
);
""")
conn.close()
