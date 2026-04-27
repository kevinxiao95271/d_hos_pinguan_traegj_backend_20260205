import collections
from pathlib import Path
import pymysql


DB = dict(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)


def main():
    miss_path = Path("D:/AiCode/cursor/d_hos_pinguan_traegj_backend_20260205/institution_miss.txt")
    names = [x.strip() for x in miss_path.read_text(encoding="utf-8").splitlines() if x.strip()]

    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            exact_found = 0
            exact_not_found = []
            level_counter = collections.Counter()
            not_level_3 = []

            for name in names:
                cur.execute(
                    """
                    SELECT name, level, region, city
                    FROM const_init_institutions
                    WHERE name = %s
                    """,
                    (name,),
                )
                rows = cur.fetchall()
                if not rows:
                    exact_not_found.append(name)
                    continue
                exact_found += 1
                levels = {((r[1] or "").strip() if r[1] is not None else "") for r in rows}
                for lv in levels:
                    level_counter[lv if lv else "<NULL/EMPTY>"] += 1
                if all((("三级" not in (r[1] or "")) for r in rows)):
                    not_level_3.append((name, sorted(levels)))

            # 模拟“API关键词 + level=三级”的语义（level 精确等于 '三级'）
            api_like_level3_miss = []
            for name in names:
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM const_init_institutions
                    WHERE name LIKE CONCAT('%%', %s, '%%')
                      AND level = '三级'
                    """,
                    (name,),
                )
                cnt = cur.fetchone()[0]
                if cnt == 0:
                    api_like_level3_miss.append(name)

            print("total_miss_names:", len(names))
            print("exact_found_in_const_init:", exact_found)
            print("exact_not_found_count:", len(exact_not_found))
            print("exact_not_found_top30:", exact_not_found[:30])
            print("level_distribution_on_exact_found:", dict(level_counter))
            print("exact_found_but_not_contains_三级_count:", len(not_level_3))
            print("exact_found_but_not_contains_三级_top40:", not_level_3[:40])
            print("api_like(keyword LIKE + level='三级')_miss_count:", len(api_like_level3_miss))
            print("api_like_level3_miss_top40:", api_like_level3_miss[:40])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
