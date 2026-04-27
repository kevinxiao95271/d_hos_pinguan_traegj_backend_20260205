import csv
import pymysql

DB = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

OUT_CSV = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\init_prod_const_init_institutions_no_created_at.csv"


def main():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT code, uscc, name, region, city, level
                FROM const_init_institutions
                ORDER BY id
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "uscc", "name", "region", "city", "level"])
        writer.writerows(rows)

    print(f"output={OUT_CSV}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
