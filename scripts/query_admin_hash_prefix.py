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
            cur.execute(
                """
                select phone, role, enabled, left(password, 4) as pfx
                from user_accounts
                where role in ('OPS', 'COMMITTEE_ADMIN')
                order by role, phone
                """
            )
            for row in cur.fetchall():
                print(row)

            print("--- seed phones ---")
            cur.execute(
                """
                select phone, role, enabled, (password is not null) as has_pwd, left(password, 4) as pfx
                from user_accounts
                where phone in (
                    '13800010001','13800010002','13800010003',
                    '13800020001','13800020002','13800020003'
                )
                order by phone
                """
            )
            for row in cur.fetchall():
                print(row)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
