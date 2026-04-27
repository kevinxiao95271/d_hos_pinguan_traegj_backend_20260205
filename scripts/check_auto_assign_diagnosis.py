import pymysql


def q(cur, sql, args=None):
    cur.execute(sql, args or ())
    return cur.fetchall()


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
            print("registrations by status:")
            for row in q(
                cur,
                """
                select status, count(*) from registrations
                where competition_id=1
                group by status
                order by status
                """,
            ):
                print(row)

            print("\nreviewers by reviewer_group_code:")
            for row in q(
                cur,
                """
                select coalesce(reviewer_group_code,'<NULL>') as g, count(*)
                from user_accounts
                where role='REVIEWER'
                group by reviewer_group_code
                order by g
                """,
            ):
                print(row)

            print("\nbook tasks count:")
            print(q(cur, "select count(*) from review_tasks where stage='BOOK' and registration_id in (select id from registrations where competition_id=1)")[0][0])

            print("\nregistrations without BOOK tasks:")
            for row in q(
                cur,
                """
                select r.id, r.group_type, coalesce(r.group_code,'<NULL>') as group_code, r.status
                from registrations r
                where r.competition_id=1
                  and not exists (
                    select 1 from review_tasks t
                    where t.registration_id=r.id and t.stage='BOOK'
                  )
                order by r.id
                limit 50
                """,
            ):
                print(row)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
