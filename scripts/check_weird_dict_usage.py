import json
import pymysql

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)
cur = conn.cursor()

out = {}
cur.execute("select count(*) from dictionary_items where type='experience' and code='experience_8'")
out["dict_experience_8"] = cur.fetchone()[0]

cur.execute("select count(*) from dictionary_items where type='group_type' and code in ('BASIC','COMPREHENSIVE','ADVANCED')")
out["dict_group_type_3"] = cur.fetchone()[0]

cur.execute("select count(*) from activity_infos where experience_improve_code='experience_8'")
out["activity_use_experience_8"] = cur.fetchone()[0]

cur.execute("select count(*) from activity_infos where experience_improve_code in ('BASIC','COMPREHENSIVE','ADVANCED')")
out["activity_use_group_codes_as_experience"] = cur.fetchone()[0]

cur.execute(
    "select count(*) from activity_infos where subject_type_code in ('BASIC','COMPREHENSIVE','ADVANCED') or method_code in ('BASIC','COMPREHENSIVE','ADVANCED')"
)
out["activity_use_group_codes_subject_or_method"] = cur.fetchone()[0]

print(json.dumps(out, ensure_ascii=False))
conn.close()
