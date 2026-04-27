import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 查现有同 uscc 或同名是否已存在
cur.execute("""
    SELECT id, name, uscc, code, region, level FROM institutions
    WHERE uscc = '12330500MB0269683G' OR name = '湖州市卫生健康发展中心'
""")
rows = cur.fetchall()
if rows:
    print("已存在记录：")
    for r in rows:
        print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  code={r[3]}  {r[4]}  {r[5]}")
else:
    print("未找到重复记录，可以插入。")

# 查 code 最大值，用于生成下一个
cur.execute("SELECT MAX(CAST(code AS UNSIGNED)) FROM institutions WHERE code REGEXP '^[0-9]+$'")
max_code = cur.fetchone()[0] or 0
new_code = str(max_code + 1).zfill(6)
print(f"\n建议 code = {new_code}")

# 生成 INSERT SQL（不执行，先看）
sql = f"""
INSERT INTO institutions (name, code, uscc, region, level, created_at)
VALUES ('湖州市卫生健康发展中心', '{new_code}', '12330500MB0269683G', '湖州市', '未定级', NOW())
"""
print(f"\n待执行 SQL：{sql.strip()}")

conn.close()
