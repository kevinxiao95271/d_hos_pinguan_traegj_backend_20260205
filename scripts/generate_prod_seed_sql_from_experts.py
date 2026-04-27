import csv
import os
import pymysql
import pandas as pd
import re


DB_CONFIG = {
    "host": "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port": 63606,
    "user": "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

PROJECT_ROOT = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
EXPERT_FILE = os.path.join(PROJECT_ROOT, "专家信息一览表_含机构全称.xls")
OUT_SQL = os.path.join(PROJECT_ROOT, "scripts", "init_prod_institutions_and_reviewers.sql")
OUT_SKIPPED = os.path.join(PROJECT_ROOT, "scripts", "init_prod_reviewers_skipped.csv")


def sql_quote(v):
    if v is None:
        return "NULL"
    s = str(v)
    s = s.replace("\\", "\\\\").replace("'", "''")
    return "'" + s + "'"


def normalize(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.lower() == "nan":
        return None
    return s


def normalize_phone(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, int):
        s = str(v)
    elif isinstance(v, float):
        if v.is_integer():
            s = str(int(v))
        else:
            s = ("%.15f" % v).rstrip("0").rstrip(".")
    else:
        s = normalize(v)
    if s is None:
        return None
    if s.endswith(".0"):
        s = s[:-2]
    digits = re.sub(r"\D", "", s)
    if len(digits) == 13 and digits.startswith("86"):
        digits = digits[2:]
    if len(digits) == 11:
        return digits
    return None


def main():
    df = pd.read_excel(EXPERT_FILE)

    required_columns = ["姓名", "手机号", "职称", "参评专业", "const_init机构全称"]
    for c in required_columns:
        if c not in df.columns:
            raise RuntimeError(f"缺少列: {c}")

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            expert_rows = []
            inst_names = set()
            skipped = []

            for idx, r in df.iterrows():
                name = normalize(r.get("姓名"))
                phone = normalize_phone(r.get("手机号"))
                title = normalize(r.get("职称"))
                background = normalize(r.get("参评专业"))
                inst_full_name = normalize(r.get("const_init机构全称"))

                if not name or not phone or not inst_full_name:
                    skipped.append(
                        {
                            "row_no": idx + 2,
                            "name": name or "",
                            "phone": phone or "",
                            "inst_full_name": inst_full_name or "",
                            "reason": "missing_required_or_invalid_field(name/phone/const_init机构全称)",
                        }
                    )
                    continue

                expert_rows.append(
                    {
                        "name": name,
                        "phone": phone,
                        "title": title,
                        "background": background,
                        "inst_full_name": inst_full_name,
                    }
                )
                inst_names.add(inst_full_name)

            inst_map = {}
            for n in sorted(inst_names):
                cur.execute(
                    """
                    SELECT id, code, uscc, name, region, city, level
                    FROM const_init_institutions
                    WHERE name = %s
                    """,
                    (n,),
                )
                rows = cur.fetchall()
                if len(rows) != 1:
                    reason = "not_found" if len(rows) == 0 else f"not_unique({len(rows)})"
                    skipped.append(
                        {
                            "row_no": "",
                            "name": "",
                            "phone": "",
                            "inst_full_name": n,
                            "reason": reason,
                        }
                    )
                    continue
                rid, code, uscc, name, region, city, level = rows[0]
                inst_map[n] = {
                    "code": code,
                    "uscc": uscc,
                    "name": name,
                    "region": region,
                    "city": city,
                    "level": level,
                }

            valid_experts = [x for x in expert_rows if x["inst_full_name"] in inst_map]

    finally:
        conn.close()

    inst_values = []
    for name in sorted({x["inst_full_name"] for x in valid_experts}):
        m = inst_map[name]
        inst_values.append(
            "("
            + ", ".join(
                [
                    sql_quote(m["name"]),
                    sql_quote(m["code"]),
                    sql_quote(m["uscc"]),
                    sql_quote(m["region"]),
                    sql_quote(m["city"]),
                    sql_quote(m["level"]),
                    "0",
                    "NOW()",
                ]
            )
            + ")"
        )

    user_values = []
    for x in valid_experts:
        m = inst_map[x["inst_full_name"]]
        user_values.append(
            "("
            + ", ".join(
                [
                    sql_quote(x["phone"]),
                    "NULL",
                    sql_quote(x["name"]),
                    sql_quote(x["title"]),
                    "'REVIEWER'",
                    "(SELECT id FROM institutions WHERE uscc = " + sql_quote(m["uscc"]) + " LIMIT 1)",
                    sql_quote(x["background"]),
                    "1",
                    "NOW()",
                ]
            )
            + ")"
        )

    lines = []
    lines.append("-- 从 专家信息一览表_含机构全称.xls 生成")
    lines.append("-- 仅初始化 institutions + user_accounts(REVIEWER)")
    lines.append("START TRANSACTION;")
    lines.append("")
    lines.append("-- 1) institutions（来自 const_init 的唯一匹配）")
    if inst_values:
        lines.append(
            "INSERT INTO institutions (name, code, uscc, region, city, level, is_ext, created_at) VALUES\n"
            + ",\n".join(inst_values)
            + "\nON DUPLICATE KEY UPDATE\n"
            + "name = VALUES(name),\n"
            + "region = VALUES(region),\n"
            + "city = VALUES(city),\n"
            + "level = VALUES(level);"
        )
    else:
        lines.append("-- 无可插入机构")
    lines.append("")
    lines.append("-- 2) user_accounts（评审专家）")
    if user_values:
        lines.append(
            "INSERT INTO user_accounts (phone, password, name, title, role, institution_id, expert_background, enabled, created_at) VALUES\n"
            + ",\n".join(user_values)
            + "\nON DUPLICATE KEY UPDATE\n"
            + "name = VALUES(name),\n"
            + "title = VALUES(title),\n"
            + "role = 'REVIEWER',\n"
            + "institution_id = VALUES(institution_id),\n"
            + "expert_background = VALUES(expert_background),\n"
            + "enabled = VALUES(enabled);"
        )
    else:
        lines.append("-- 无可插入评审专家")
    lines.append("")
    lines.append("COMMIT;")
    lines.append("")
    lines.append(
        f"-- summary: institutions={len(inst_values)}, reviewers={len(user_values)}, skipped={len(skipped)}"
    )

    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    with open(OUT_SKIPPED, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["row_no", "name", "phone", "inst_full_name", "reason"]
        )
        writer.writeheader()
        for r in skipped:
            writer.writerow(r)

    print(f"generated_sql={OUT_SQL}")
    print(f"generated_skipped={OUT_SKIPPED}")
    print(f"institutions={len(inst_values)} reviewers={len(user_values)} skipped={len(skipped)}")


if __name__ == "__main__":
    main()
