import os
import pymysql


DB_CONFIG = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

PROJECT_ROOT = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
OUT_DICT_SQL = os.path.join(PROJECT_ROOT, "scripts", "init_prod_dictionary_items.sql")
OUT_COMP_SQL = os.path.join(PROJECT_ROOT, "scripts", "init_prod_competitions.sql")


def q(v):
    if v is None:
        return "NULL"
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return "'" + s + "'"


def fmt_dt(v):
    if v is None:
        return "NULL"
    return q(v.strftime("%Y-%m-%d %H:%M:%S"))


def build_dictionary_sql(rows, has_sort_order):
    lines = []
    lines.append("-- dictionary_items 初始化（导出自当前环境）")
    lines.append("START TRANSACTION;")
    lines.append("")
    if rows:
        vals = []
        for r in rows:
            if has_sort_order:
                val_items = [
                    q(r["type"]),
                    q(r["code"]),
                    q(r["label"]),
                    str(int(r["active"])),
                    str(int(r["sort_order"])),
                    fmt_dt(r["created_at"]),
                ]
            else:
                val_items = [
                    q(r["type"]),
                    q(r["code"]),
                    q(r["label"]),
                    str(int(r["active"])),
                    fmt_dt(r["created_at"]),
                ]
            vals.append("(" + ", ".join(val_items) + ")")
        if has_sort_order:
            lines.append(
                "INSERT INTO dictionary_items (type, code, label, active, sort_order, created_at) VALUES\n"
                + ",\n".join(vals)
                + "\nON DUPLICATE KEY UPDATE\n"
                + "label = VALUES(label),\n"
                + "active = VALUES(active),\n"
                + "sort_order = VALUES(sort_order);"
            )
        else:
            lines.append(
                "INSERT INTO dictionary_items (type, code, label, active, created_at) VALUES\n"
                + ",\n".join(vals)
                + "\nON DUPLICATE KEY UPDATE\n"
                + "label = VALUES(label),\n"
                + "active = VALUES(active);"
            )
    else:
        lines.append("-- 无字典数据")
    lines.append("")
    lines.append("COMMIT;")
    lines.append("")
    lines.append(f"-- summary: dictionary_items={len(rows)}")
    return "\n".join(lines)


def build_competitions_sql(rows):
    lines = []
    lines.append("-- competitions 初始化（导出自当前环境）")
    lines.append("START TRANSACTION;")
    lines.append("")
    if rows:
        vals = []
        for r in rows:
            vals.append(
                "("
                + ", ".join(
                    [
                        str(int(r["id"])),
                        q(r["name"]),
                        q(r["stage"]),
                        fmt_dt(r["register_start"]),
                        fmt_dt(r["register_end"]),
                        fmt_dt(r["book_review_start"]),
                        fmt_dt(r["book_review_end"]),
                        fmt_dt(r["interview_start"]),
                        fmt_dt(r["interview_end"]),
                        fmt_dt(r["final_start"]),
                        fmt_dt(r["final_end"]),
                        fmt_dt(r["created_at"]),
                    ]
                )
                + ")"
            )
        lines.append(
            "INSERT INTO competitions (\n"
            + "  id, name, stage,\n"
            + "  register_start, register_end,\n"
            + "  book_review_start, book_review_end,\n"
            + "  interview_start, interview_end,\n"
            + "  final_start, final_end,\n"
            + "  created_at\n"
            + ") VALUES\n"
            + ",\n".join(vals)
            + "\nON DUPLICATE KEY UPDATE\n"
            + "name = VALUES(name),\n"
            + "stage = VALUES(stage),\n"
            + "register_start = VALUES(register_start),\n"
            + "register_end = VALUES(register_end),\n"
            + "book_review_start = VALUES(book_review_start),\n"
            + "book_review_end = VALUES(book_review_end),\n"
            + "interview_start = VALUES(interview_start),\n"
            + "interview_end = VALUES(interview_end),\n"
            + "final_start = VALUES(final_start),\n"
            + "final_end = VALUES(final_end);"
        )
    else:
        lines.append("-- 无赛事数据")
    lines.append("")
    lines.append("COMMIT;")
    lines.append("")
    lines.append(f"-- summary: competitions={len(rows)}")
    return "\n".join(lines)


def main():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS c
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'dictionary_items'
                  AND COLUMN_NAME = 'sort_order'
                """
            )
            has_sort_order = cur.fetchone()["c"] > 0

            if has_sort_order:
                cur.execute(
                    """
                    SELECT type, code, label, active, sort_order, created_at
                    FROM dictionary_items
                    ORDER BY type, sort_order, id
                    """
                )
            else:
                cur.execute(
                    """
                    SELECT type, code, label, active, created_at
                    FROM dictionary_items
                    ORDER BY type, id
                    """
                )
            dict_rows = cur.fetchall()

            cur.execute(
                """
                SELECT id, name, stage,
                       register_start, register_end,
                       book_review_start, book_review_end,
                       interview_start, interview_end,
                       final_start, final_end,
                       created_at
                FROM competitions
                ORDER BY id
                """
            )
            comp_rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_DICT_SQL, "w", encoding="utf-8") as f:
        f.write(build_dictionary_sql(dict_rows, has_sort_order))

    with open(OUT_COMP_SQL, "w", encoding="utf-8") as f:
        f.write(build_competitions_sql(comp_rows))

    print(f"dictionary_sql={OUT_DICT_SQL} rows={len(dict_rows)}")
    print(f"competitions_sql={OUT_COMP_SQL} rows={len(comp_rows)}")


if __name__ == "__main__":
    main()
