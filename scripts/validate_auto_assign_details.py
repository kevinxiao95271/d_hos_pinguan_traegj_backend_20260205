import json
import math

import pymysql


def main() -> None:
    conn = pymysql.connect(
        host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
        port=63606,
        user="root",
        password="Yiguo9527_",
        database="d_hos_pinguan_traegj_20260205",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    result = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS c FROM registrations WHERE competition_id = 1")
            result["total_registrations_comp1"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(DISTINCT registration_id) AS c "
                "FROM review_tasks rt "
                "JOIN registrations r ON r.id = rt.registration_id "
                "WHERE r.competition_id = 1 AND rt.stage = 'BOOK'"
            )
            result["regs_with_book_task"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT r.id "
                "FROM registrations r "
                "LEFT JOIN review_tasks rt ON rt.registration_id = r.id AND rt.stage = 'BOOK' "
                "WHERE r.competition_id = 1 AND rt.id IS NULL "
                "ORDER BY r.id"
            )
            missing = [row["id"] for row in cursor.fetchall()]
            result["regs_without_book_task_count"] = len(missing)
            result["regs_without_book_task_ids_first20"] = missing[:20]

            cursor.execute(
                "SELECT COUNT(*) AS c "
                "FROM review_tasks rt "
                "JOIN registrations r ON r.id = rt.registration_id "
                "JOIN user_accounts u ON u.id = rt.reviewer_id "
                "WHERE r.competition_id = 1 AND rt.stage = 'BOOK' "
                "AND u.institution_id IS NOT NULL AND r.institution_id IS NOT NULL "
                "AND u.institution_id = r.institution_id"
            )
            result["same_institution_violations_book"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(*) AS c FROM ("
                "  SELECT rt.registration_id, rt.reviewer_id, COUNT(*) AS n "
                "  FROM review_tasks rt "
                "  JOIN registrations r ON r.id = rt.registration_id "
                "  WHERE r.competition_id = 1 "
                "  GROUP BY rt.registration_id, rt.reviewer_id "
                "  HAVING COUNT(*) > 1"
                ") t"
            )
            result["duplicate_reviewer_per_registration_pairs"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT setting_value FROM system_settings WHERE setting_key = 'reviewerMaxLoad' LIMIT 1"
            )
            row = cursor.fetchone()
            max_load = 20
            if row and row.get("setting_value"):
                try:
                    max_load = int(str(row["setting_value"]).strip())
                except ValueError:
                    max_load = 20
            result["reviewer_max_load"] = max_load

            cursor.execute(
                "SELECT MAX(cnt) AS mx FROM ("
                "  SELECT reviewer_id, COUNT(*) AS cnt "
                "  FROM review_tasks rt "
                "  JOIN registrations r ON r.id = rt.registration_id "
                "  WHERE r.competition_id = 1 "
                "  GROUP BY reviewer_id"
                ") t"
            )
            row = cursor.fetchone()
            result["max_reviewer_total_load_comp1"] = row["mx"] if row else 0

            cursor.execute(
                "SELECT COUNT(*) AS c FROM ("
                "  SELECT reviewer_id, COUNT(*) AS cnt "
                "  FROM review_tasks rt "
                "  JOIN registrations r ON r.id = rt.registration_id "
                "  WHERE r.competition_id = 1 "
                "  GROUP BY reviewer_id "
                "  HAVING COUNT(*) > %s"
                ") t",
                (max_load,),
            )
            result["reviewers_over_max_load_count"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(*) AS c "
                "FROM review_tasks "
                "WHERE stage = 'BOOK' "
                "AND created_at >= '2026-03-03 15:36:00' "
                "AND created_at < '2026-03-03 15:38:00'"
            )
            result["book_tasks_created_1536_1538"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS minute_mark, COUNT(*) AS cnt "
                "FROM review_tasks "
                "WHERE stage = 'BOOK' "
                "GROUP BY DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') "
                "ORDER BY minute_mark DESC "
                "LIMIT 20"
            )
            result["book_task_create_minute_top20"] = cursor.fetchall()

            cursor.execute(
                "SELECT COUNT(*) AS c "
                "FROM review_tasks "
                "WHERE stage = 'BOOK' "
                "AND created_at >= '2026-03-03 16:36:00' "
                "AND created_at < '2026-03-03 16:38:00'"
            )
            result["batch_1636_1638_count"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(DISTINCT registration_id) AS c "
                "FROM review_tasks "
                "WHERE stage = 'BOOK' "
                "AND created_at >= '2026-03-03 16:36:00' "
                "AND created_at < '2026-03-03 16:38:00'"
            )
            result["batch_1636_1638_distinct_registration_count"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(*) AS c "
                "FROM review_tasks rt "
                "JOIN registrations r ON r.id = rt.registration_id "
                "JOIN user_accounts u ON u.id = rt.reviewer_id "
                "WHERE rt.stage = 'BOOK' "
                "AND rt.created_at >= '2026-03-03 16:36:00' "
                "AND rt.created_at < '2026-03-03 16:38:00' "
                "AND u.institution_id IS NOT NULL AND r.institution_id IS NOT NULL "
                "AND u.institution_id = r.institution_id"
            )
            result["batch_1636_1638_same_institution_violations"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT COUNT(*) AS c FROM ("
                "  SELECT registration_id, reviewer_id, COUNT(*) AS n "
                "  FROM review_tasks "
                "  WHERE stage = 'BOOK' "
                "  AND created_at >= '2026-03-03 16:36:00' "
                "  AND created_at < '2026-03-03 16:38:00' "
                "  GROUP BY registration_id, reviewer_id "
                "  HAVING COUNT(*) > 1"
                ") t"
            )
            result["batch_1636_1638_duplicate_pairs"] = cursor.fetchone()["c"]

            cursor.execute(
                "SELECT reviewer_id, COUNT(*) AS cnt "
                "FROM review_tasks "
                "WHERE stage = 'BOOK' "
                "AND created_at >= '2026-03-03 16:36:00' "
                "AND created_at < '2026-03-03 16:38:00' "
                "GROUP BY reviewer_id "
                "ORDER BY cnt DESC, reviewer_id ASC"
            )
            batch_load_rows = cursor.fetchall()
            batch_histogram = {}
            for row in batch_load_rows:
                key = str(int(row["cnt"]))
                batch_histogram[key] = batch_histogram.get(key, 0) + 1
            result["batch_1636_1638_reviewer_distribution"] = {
                "reviewerCountWithTasks": len(batch_load_rows),
                "taskCount": sum(int(r["cnt"]) for r in batch_load_rows),
                "histogram": dict(sorted(batch_histogram.items(), key=lambda kv: int(kv[0]))),
                "top10LoadRows": batch_load_rows[:10],
            }

            cursor.execute(
                "SELECT reviewer_id, COUNT(*) AS cnt "
                "FROM review_tasks rt "
                "JOIN registrations r ON r.id = rt.registration_id "
                "WHERE r.competition_id = 1 "
                "GROUP BY reviewer_id "
                "ORDER BY cnt DESC, reviewer_id ASC"
            )
            total_load_rows = cursor.fetchall()
            total_loads = [int(row["cnt"]) for row in total_load_rows]
            reviewer_count = len(total_loads)
            task_count = sum(total_loads)
            avg = (task_count / reviewer_count) if reviewer_count > 0 else 0.0
            sorted_loads = sorted(total_loads)
            if reviewer_count == 0:
                median = 0.0
            elif reviewer_count % 2 == 1:
                median = float(sorted_loads[reviewer_count // 2])
            else:
                median = (sorted_loads[reviewer_count // 2 - 1] + sorted_loads[reviewer_count // 2]) / 2.0
            variance = (
                sum((x - avg) ** 2 for x in total_loads) / reviewer_count if reviewer_count > 0 else 0.0
            )
            stddev = math.sqrt(variance)
            cv = (stddev / avg) if avg > 0 else 0.0
            top1 = total_loads[0] if reviewer_count > 0 else 0
            top3 = sum(total_loads[:3]) if reviewer_count > 0 else 0
            top5 = sum(total_loads[:5]) if reviewer_count > 0 else 0
            top10 = sum(total_loads[:10]) if reviewer_count > 0 else 0
            top1_share = (top1 / task_count) if task_count > 0 else 0.0
            top3_share = (top3 / task_count) if task_count > 0 else 0.0
            top5_share = (top5 / task_count) if task_count > 0 else 0.0
            top10_share = (top10 / task_count) if task_count > 0 else 0.0

            histogram = {}
            for x in total_loads:
                key = str(x)
                histogram[key] = histogram.get(key, 0) + 1

            def gini(values):
                n = len(values)
                if n == 0:
                    return 0.0
                s = sum(values)
                if s == 0:
                    return 0.0
                sorted_vals = sorted(values)
                weighted = 0.0
                for i, val in enumerate(sorted_vals, start=1):
                    weighted += i * val
                return (2.0 * weighted) / (n * s) - (n + 1.0) / n

            result["reviewer_load_distribution_comp1"] = {
                "reviewerCountWithTasks": reviewer_count,
                "taskCount": task_count,
                "avg": round(avg, 4),
                "median": round(median, 4),
                "stddev": round(stddev, 4),
                "cv": round(cv, 4),
                "gini": round(gini(total_loads), 4),
                "top1Share": round(top1_share, 4),
                "top3Share": round(top3_share, 4),
                "top5Share": round(top5_share, 4),
                "top10Share": round(top10_share, 4),
                "histogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
                "top10LoadRows": total_load_rows[:10],
            }
    finally:
        conn.close()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
