import pymysql

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="information_schema",
    charset="utf8mb4",
)

dbs = ["d_hos_pinguan_traegj_20260205", "pgds"]

with conn.cursor() as cur:
    for db in dbs:
        print(f"=== {db} ===")
        cur.execute(
            """
            SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE,
                   GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS cols
            FROM STATISTICS
            WHERE TABLE_SCHEMA=%s
            GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
            HAVING cols LIKE '%%uscc%%'
            ORDER BY TABLE_NAME, INDEX_NAME
            """,
            (db,),
        )
        rows = cur.fetchall()
        print("uscc indexes:", len(rows))
        for r in rows:
            print(r)

        cur.execute(
            """
            SELECT TABLE_NAME, COLUMN_NAME
            FROM COLUMNS
            WHERE TABLE_SCHEMA=%s AND COLUMN_NAME='uscc'
            ORDER BY TABLE_NAME
            """,
            (db,),
        )
        print("tables with uscc column:", cur.fetchall())
        print()

conn.close()
