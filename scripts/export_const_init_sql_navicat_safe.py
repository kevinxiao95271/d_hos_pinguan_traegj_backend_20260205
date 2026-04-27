import pymysql

DB = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

OUT_SQL = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\init_prod_const_init_institutions_navicat_safe.sql"
BATCH = 500


def lit(v):
    if v is None:
        return "NULL"
    b = str(v).encode("utf-8").hex()
    return f"CONVERT(0x{b} USING utf8mb4)"


def main():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT code, uscc, name, region, city, level, created_at
                FROM const_init_institutions
                ORDER BY id
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- const_init_institutions navicat-safe 初始化SQL\n")
        f.write("SET NAMES utf8mb4;\n")
        f.write("SET character_set_client = utf8mb4;\n")
        f.write("SET character_set_connection = utf8mb4;\n")
        f.write("SET character_set_results = utf8mb4;\n")
        f.write("START TRANSACTION;\n\n")
        f.write("TRUNCATE TABLE `const_init_institutions`;\n\n")

        for i in range(0, len(rows), BATCH):
            batch = rows[i : i + BATCH]
            f.write("INSERT INTO `const_init_institutions` (`code`, `uscc`, `name`, `region`, `city`, `level`, `created_at`) VALUES\n")
            vals = []
            for r in batch:
                vals.append("(" + ", ".join(lit(v) for v in r) + ")")
            f.write(",\n".join(vals))
            f.write(";\n\n")

        f.write("COMMIT;\n")
        f.write(f"-- summary: rows={len(rows)}\n")

    print(f"output={OUT_SQL}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
