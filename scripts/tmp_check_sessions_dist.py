"""
摸排：专场码 × 组别实际分布
目标：
1. 看 final_ranking_snapshots 中 session_code 是否含"进阶"
2. 看每个专场内 group_type 的分布（是否存在同一专场混进阶与非进阶）
3. 看 registrations 的 final_session_code × group_type 分布
"""
import pymysql

DB_HOST = "gz-cdb-bq7gk3k5.sql.tencentcdb.com"
DB_PORT = 63606
DB_USER = "root"
DB_PASS = "Yiguo9527_"
DB_NAME = "d_hos_pinguan_traegj_20260205"

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
    password=DB_PASS, database=DB_NAME, charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)

def q(sql, args=()):
    with conn.cursor() as c:
        c.execute(sql, args)
        return c.fetchall()

print("=" * 70)
print("1. final_ranking_snapshots 专场码 × group_type 分布")
print("=" * 70)
rows = q("""
    SELECT session_code,
           group_type,
           COUNT(*) AS cnt,
           session_code LIKE '%%进阶%%' AS code_has_adv
    FROM final_ranking_snapshots
    WHERE competition_id = 1
    GROUP BY session_code, group_type
    ORDER BY session_code, group_type
""")
last_sc = None
mixed_sessions = []
session_groups = {}
for r in rows:
    sc = r["session_code"] or "(null)"
    gt = r["group_type"] or "null"
    cnt = r["cnt"]
    has_adv = bool(r["code_has_adv"])
    if sc != last_sc:
        print(f"\n  专场: [{sc}]  (码含'进阶': {has_adv})")
        last_sc = sc
    print(f"    group_type={gt:15s}  {cnt} 条")
    session_groups.setdefault(sc, set()).add(gt)

print("\n")
print("=" * 70)
print("2. 是否存在同一专场混进阶与非进阶的情况")
print("=" * 70)
for sc, gts in session_groups.items():
    has_adv = "ADVANCED" in gts
    has_non = bool(gts - {"ADVANCED", "null"})
    if has_adv and has_non:
        print(f"  ⚠ 混合专场: [{sc}] → {gts}")
    elif has_adv:
        print(f"  纯进阶专场: [{sc}] → {gts}")
    elif "null" in gts and len(gts) == 1:
        print(f"  全null专场: [{sc}] → {gts}")
    else:
        print(f"  非进阶专场: [{sc}] → {gts}")

print("\n")
print("=" * 70)
print("3. registrations final_session_code × group_type（已入场的项目）")
print("=" * 70)
rows2 = q("""
    SELECT final_session_code,
           group_type,
           COUNT(*) AS cnt,
           final_session_code LIKE '%%进阶%%' AS code_has_adv
    FROM registrations
    WHERE competition_id = 1
      AND final_session_code IS NOT NULL
      AND status = 'SUBMITTED'
    GROUP BY final_session_code, group_type
    ORDER BY final_session_code, group_type
""")
last_sc2 = None
for r in rows2:
    sc = r["final_session_code"] or "(null)"
    gt = r["group_type"] or "null"
    has_adv = bool(r["code_has_adv"])
    if sc != last_sc2:
        print(f"\n  专场: [{sc}]  (码含'进阶': {has_adv})")
        last_sc2 = sc
    print(f"    group_type={gt:15s}  {r['cnt']} 条")

conn.close()
print("\n摸排完成")
