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

OUT_CSV = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\init_prod_const_init_institutions_unique_uscc.csv"


def main():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.code, t.uscc, t.name, t.region, t.city, t.level
                FROM const_init_institutions t
                JOIN (
                    SELECT uscc, MIN(id) AS keep_id
                    FROM const_init_institutions
                    GROUP BY uscc
                ) k ON t.id = k.keep_id
                ORDER BY t.id
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["code", "uscc", "name", "region", "city", "level"])
        w.writerows(rows)

    print(f"output={OUT_CSV}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
