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
                select type, count(*)
                from dictionary_items
                where active = 1
                group by type
                order by type
                """
            )
            print("types:", cur.fetchall())

            cur.execute(
                """
                select code, label
                from dictionary_items
                where active = 1
                  and (type like '%subject%' or type like '%method%')
                order by type, code
                """
            )
            rows = cur.fetchall()
            print("subject/method codes:", len(rows))
            for row in rows[:100]:
                print(row)

            cur.execute(
                """
                select id, name
                from competitions
                order by id desc
                limit 1
                """
            )
            latest = cur.fetchone()
            print("latest_comp:", latest)
            if latest:
                cid = latest[0]
                cur.execute(
                    """
                    select
                      sum(case when ai.id is null then 1 else 0 end) as missing_ai,
                      sum(case when ai.id is not null and (ai.subject_type_code is null or trim(ai.subject_type_code) = '') then 1 else 0 end) as blank_subject,
                      sum(case when ai.id is not null and (ai.method_code is null or trim(ai.method_code) = '') then 1 else 0 end) as blank_method,
                      count(*) as total_submitted
                    from registrations r
                    left join activity_infos ai on ai.registration_id = r.id
                    where r.competition_id = %s
                      and r.status = 'SUBMITTED'
                    """,
                    (cid,),
                )
                print("latest_stats:", cur.fetchone())

                cur.execute(
                    """
                    select r.id, r.project_name, r.status
                    from registrations r
                    left join activity_infos ai on ai.registration_id = r.id
                    where r.competition_id = %s
                      and r.status = 'SUBMITTED'
                      and ai.id is null
                    order by r.id
                    """
                    ,
                    (cid,),
                )
                print("submitted_missing_activity_infos:")
                for row in cur.fetchall():
                    print(row)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
