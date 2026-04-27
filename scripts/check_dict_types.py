import io
import sys
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    db="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)
cur = conn.cursor()
cols = ["subject_type_code", "method_code", "quality_topic_code", "experience_improve_code"]
for col in cols:
    cur.execute(
        f"SELECT DISTINCT d.type FROM activity_infos ai "
        f"JOIN dictionary_items d ON d.code = ai.{col} "
        f"ORDER BY d.type"
    )
    print(col, [r[0] for r in cur.fetchall()])
conn.close()
