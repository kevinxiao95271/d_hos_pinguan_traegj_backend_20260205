import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 各年单独
cur.execute("""
SELECT year, COUNT(DISTINCT CONCAT(project_leader_name,'|',project_leader_phone)) AS uniq
FROM pinguan_his_data
WHERE year IN (2024,2025)
  AND project_leader_name  IS NOT NULL AND project_leader_name  != ''
  AND project_leader_phone IS NOT NULL AND project_leader_phone != ''
GROUP BY year ORDER BY year
""")
for r in cur.fetchall():
    print(f"{r[0]} 年项目负责人 name+phone 去重: {r[1]} 人")

# 跨年合并
cur.execute("""
SELECT COUNT(*) FROM (
  SELECT project_leader_name, project_leader_phone
  FROM pinguan_his_data
  WHERE year IN (2024,2025)
    AND project_leader_name  IS NOT NULL AND project_leader_name  != ''
    AND project_leader_phone IS NOT NULL AND project_leader_phone != ''
  GROUP BY project_leader_name, project_leader_phone
) u
""")
print(f"2024+2025 跨年合并去重: {cur.fetchone()[0]} 人")
conn.close()
