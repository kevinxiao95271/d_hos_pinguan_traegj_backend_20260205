import csv
import pymysql
from collections import Counter


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
            cur.execute("select id, name from competitions order by id desc limit 1")
            comp_id, comp_name = cur.fetchone()

            cur.execute("select code, label from dictionary_items where active = 1")
            code_to_label = dict(cur.fetchall())

            cur.execute(
                """
                select r.id, r.project_name, r.status, a.subject_type_code, a.method_code
                from registrations r
                left join activity_infos a on a.registration_id = r.id
                where r.competition_id = %s
                order by r.id
                """,
                (comp_id,),
            )
            rows = cur.fetchall()

        subject_counts = Counter()
        method_counts = Counter()
        noisy_subject = []
        noisy_method = []

        for rid, project_name, status, subject_code, method_code in rows:
            s_code = (subject_code or "").strip()
            m_code = (method_code or "").strip()

            s_label = "未知" if not s_code else code_to_label.get(s_code, s_code)
            m_label = "未知" if not m_code else code_to_label.get(m_code, m_code)

            subject_counts[s_label] += 1
            method_counts[m_label] += 1

            if s_label == "未知" or (s_code and s_code not in code_to_label):
                noisy_subject.append((rid, project_name, status, subject_code, s_label))
            if m_label == "未知" or (m_code and m_code not in code_to_label):
                noisy_method.append((rid, project_name, status, method_code, m_label))

        noisy_map = {}
        for rid, project_name, status, subject_code, subject_label in noisy_subject:
            noisy_map.setdefault(rid, {
                "registration_id": rid,
                "project_name": project_name,
                "status": status,
                "subject_type_code": subject_code,
                "subject_type_label": subject_label,
                "method_code": None,
                "method_label": None,
            })
        for rid, project_name, status, method_code, method_label in noisy_method:
            noisy_map.setdefault(rid, {
                "registration_id": rid,
                "project_name": project_name,
                "status": status,
                "subject_type_code": None,
                "subject_type_label": None,
                "method_code": method_code,
                "method_label": method_label,
            })
            noisy_map[rid]["method_code"] = method_code
            noisy_map[rid]["method_label"] = method_label

        output_path = "scripts/stats_noise_latest.csv"
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "registration_id",
                    "project_name",
                    "status",
                    "subject_type_code",
                    "subject_type_label",
                    "method_code",
                    "method_label",
                ],
            )
            writer.writeheader()
            for row in sorted(noisy_map.values(), key=lambda x: x["registration_id"]):
                writer.writerow(row)

        print(f"competition_id={comp_id}, competition_name={comp_name}")
        print(f"registrations={len(rows)}")
        print(f"subject_counts={dict(subject_counts)}")
        print(f"method_counts={dict(method_counts)}")
        print(f"noisy_subject_count={len(noisy_subject)}")
        print(f"noisy_method_count={len(noisy_method)}")
        print(f"noisy_project_union_count={len(noisy_map)}")
        print(f"noisy_csv={output_path}")
        print("sample_noisy_projects_top20:")
        for row in sorted(noisy_map.values(), key=lambda x: x["registration_id"])[:20]:
            print(
                row["registration_id"],
                row["project_name"],
                row["status"],
                row["subject_type_code"],
                row["method_code"],
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
