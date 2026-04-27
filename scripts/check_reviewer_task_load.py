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
                select
                  u.id,
                  u.name,
                  u.phone,
                  count(t.id) as task_cnt
                from user_accounts u
                left join review_tasks t on t.reviewer_id = u.id
                where u.role = 'REVIEWER'
                group by u.id, u.name, u.phone
                having count(t.id) > 0
                order by task_cnt desc, u.id
                limit 20
                """
            )
            rows = cur.fetchall()
            print("reviewers_with_tasks:", len(rows))
            for row in rows:
                print(row)

            cur.execute("select count(*) from review_tasks")
            print("total_review_tasks:", cur.fetchone()[0])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
