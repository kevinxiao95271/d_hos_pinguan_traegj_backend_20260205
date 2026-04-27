import pymysql, sys, io, uuid
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 生成 INST_XXXXXXXX 格式 code
new_code = 'INST_' + uuid.uuid4().hex[:8].upper()

cur.execute("""
    INSERT INTO institutions (name, code, uscc, region, level, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
""", ('湖州市卫生健康发展中心', new_code, '12330500MB0269683G', '湖州市', '未定级'))
conn.commit()

new_id = cur.lastrowid
print(f"插入成功！")
print(f"  id         = {new_id}")
print(f"  name       = 湖州市卫生健康发展中心")
print(f"  code       = {new_code}")
print(f"  uscc       = 12330500MB0269683G")
print(f"  region     = 湖州市")
print(f"  level      = 未定级")

conn.close()
