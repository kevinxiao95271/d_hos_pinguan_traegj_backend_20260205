import pymysql

DB = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

OUT_SQL = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\init_prod_const_init_institutions.sql"
BATCH = 1000


def q(v):
    if v is None:
        return "NULL"
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return "'" + s + "'"


def main():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'const_init_institutions'
                ORDER BY ORDINAL_POSITION
                """
            )
            cols = [r[0] for r in cur.fetchall()]
            export_cols = [c for c in cols if c != "id"]
            col_sql = ", ".join(f"`{c}`" for c in export_cols)

            cur.execute(f"SELECT {col_sql} FROM const_init_institutions ORDER BY id")
            rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- const_init_institutions 全量初始化SQL\n")
        f.write("-- source: d_hos_pinguan_traegj_20260205.const_init_institutions\n")
        f.write("START TRANSACTION;\n\n")
        f.write("TRUNCATE TABLE `const_init_institutions`;\n\n")

        if rows:
            for i in range(0, len(rows), BATCH):
                batch = rows[i : i + BATCH]
                f.write(f"INSERT INTO `const_init_institutions` ({col_sql}) VALUES\n")
                values = []
                for r in batch:
                    values.append("(" + ", ".join(q(v) for v in r) + ")")
                f.write(",\n".join(values))
                f.write(";\n\n")

        f.write("COMMIT;\n")
        f.write(f"-- summary: rows={len(rows)}\n")

    print(f"output={OUT_SQL}")
    print(f"rows={len(rows)}")
    print(f"columns={','.join(export_cols)}")


if __name__ == "__main__":
    main()
