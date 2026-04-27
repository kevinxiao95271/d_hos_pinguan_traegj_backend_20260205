import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 1. 总行数 & 年份分布
cur.execute("""
SELECT year, COUNT(*) AS total_rows
FROM pinguan_his_data
WHERE year IN (2024, 2025)
GROUP BY year ORDER BY year
""")
print("=== 总行数（每个报名项目一行）===")
for r in cur.fetchall():
    print(f"  {r[0]} 年: {r[1]} 行")

# 2. 按 hospital_contact (name+phone) 去重
cur.execute("""
SELECT year,
  COUNT(DISTINCT CONCAT(COALESCE(hospital_contact_name,''), '|', COALESCE(hospital_contact_phone,''))) AS contact_uniq
FROM pinguan_his_data
WHERE year IN (2024, 2025)
GROUP BY year ORDER BY year
""")
print("\n=== 联络员 name+phone 去重唯一人数 ===")
for r in cur.fetchall():
    print(f"  {r[0]} 年: {r[1]} 人")

# 3. 按 project_leader (name+phone) 去重
cur.execute("""
SELECT year,
  COUNT(DISTINCT CONCAT(COALESCE(project_leader_name,''), '|', COALESCE(project_leader_phone,''))) AS leader_uniq
FROM pinguan_his_data
WHERE year IN (2024, 2025)
GROUP BY year ORDER BY year
""")
print("\n=== 项目负责人 name+phone 去重唯一人数 ===")
for r in cur.fetchall():
    print(f"  {r[0]} 年: {r[1]} 人")

# 4. 联络员+负责人 合并后整体去重
cur.execute("""
SELECT year, COUNT(*) AS uniq_people
FROM (
  SELECT year, name, phone
  FROM (
    SELECT year, hospital_contact_name AS name, hospital_contact_phone AS phone
    FROM pinguan_his_data WHERE year IN (2024, 2025)
    UNION ALL
    SELECT year, project_leader_name, project_leader_phone
    FROM pinguan_his_data WHERE year IN (2024, 2025)
  ) t
  WHERE name IS NOT NULL AND name != ''
    AND phone IS NOT NULL AND phone != ''
  GROUP BY year, name, phone
) u
GROUP BY year ORDER BY year
""")
print("\n=== 联络员+负责人合并后 name+phone 去重唯一人数 ===")
for r in cur.fetchall():
    print(f"  {r[0]} 年: {r[1]} 人")

# 5. 两年合并去重（跨年同一个人只算一次）
cur.execute("""
SELECT COUNT(*) AS total_uniq
FROM (
  SELECT name, phone
  FROM (
    SELECT hospital_contact_name AS name, hospital_contact_phone AS phone
    FROM pinguan_his_data WHERE year IN (2024, 2025)
    UNION ALL
    SELECT project_leader_name, project_leader_phone
    FROM pinguan_his_data WHERE year IN (2024, 2025)
  ) t
  WHERE name IS NOT NULL AND name != ''
    AND phone IS NOT NULL AND phone != ''
  GROUP BY name, phone
) u
""")
print("\n=== 2024+2025 跨年合并去重 唯一人数 ===")
print(f"  共 {cur.fetchone()[0]} 人")

conn.close()
