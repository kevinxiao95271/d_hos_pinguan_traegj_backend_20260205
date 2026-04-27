import pymysql

DB = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

SQL_FILE = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\init_prod_const_init_institutions.sql"


def main():
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_text = f.read()

    insert_stmts = []
    for part in sql_text.split(";\n"):
        p = part.strip()
        if p.startswith("INSERT INTO `const_init_institutions`"):
            insert_stmts.append(p + ";")

    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS const_init_institutions_validate_tmp")
            cur.execute("CREATE TABLE const_init_institutions_validate_tmp LIKE const_init_institutions")

            ok = 0
            for i, s in enumerate(insert_stmts, start=1):
                s = s.replace("`const_init_institutions`", "`const_init_institutions_validate_tmp`", 1)
                try:
                    cur.execute(s)
                    ok += 1
                except Exception as e:
                    print(f"FAILED at batch {i}: {e}")
                    print(s[:400])
                    raise

            conn.rollback()
            print(f"OK batches={ok}, rows_approx={ok*1000}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
