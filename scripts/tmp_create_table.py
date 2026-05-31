import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

ddl = """
CREATE TABLE IF NOT EXISTS staff_session_assignments (
  id BIGINT NOT NULL AUTO_INCREMENT,
  staff_id BIGINT NOT NULL,
  session_code VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_staff_session (staff_id, session_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""
cur.execute(ddl)
conn.commit()
cur.execute("SHOW TABLES LIKE 'staff_session_assignments'")
print("表:", "已创建" if cur.fetchone() else "创建失败")

cur.close()
conn.close()
