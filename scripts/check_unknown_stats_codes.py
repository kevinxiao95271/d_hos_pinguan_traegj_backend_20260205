import pymysql


def main():
    conn = pymysql.connect(
        host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
        port=63606,
        user="root",
        password="Yiguo9527_",
        database="d_hos_pinguan_traegj_20260205",
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            print("=== Unknown subject_type_code ===")
            cur.execute(
                """
                SELECT
                    ai.subject_type_code AS code,
                    COUNT(*) AS cnt
                FROM activity_infos ai
                LEFT JOIN dictionary_items d
                    ON d.code COLLATE utf8mb4_general_ci = ai.subject_type_code COLLATE utf8mb4_general_ci
                    AND d.active = 1
                WHERE d.id IS NULL
                GROUP BY ai.subject_type_code
                ORDER BY cnt DESC, ai.subject_type_code
                """
            )
            for row in cur.fetchall():
                print(row)

            print("\n=== Unknown method_code ===")
            cur.execute(
                """
                SELECT
                    ai.method_code AS code,
                    COUNT(*) AS cnt
                FROM activity_infos ai
                LEFT JOIN dictionary_items d
                    ON d.code COLLATE utf8mb4_general_ci = ai.method_code COLLATE utf8mb4_general_ci
                    AND d.active = 1
                WHERE d.id IS NULL
                GROUP BY ai.method_code
                ORDER BY cnt DESC, ai.method_code
                """
            )
            for row in cur.fetchall():
                print(row)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
