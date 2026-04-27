#!/usr/bin/env python3
"""
为「尚未同时具备书审+面谈待评」的评委，各补 1 条 BOOK PENDING + 1 条 INTERVIEW PENDING，
规则与 ReviewService.assignTask 一致：
  - 同一评委在同一报名上只能有一条任务（任意阶段）
  - 评委机构与报名机构均非空且相同时跳过（同机构回避）
  - 面谈任务仅挂在 group_type=ADVANCED 的报名上

然后对这些评委（及原先已满足条件的）可用 setup_reviewer_review2026.py 统一改密码 review2026。

依赖: pip install pymysql bcrypt

用法:
  python scripts/provision_10_reviewers_dual_pending.py --dry-run
  python scripts/provision_10_reviewers_dual_pending.py
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

import pymysql

try:
    import bcrypt
except ImportError:
    print("pip install bcrypt pymysql", file=sys.stderr)
    sys.exit(1)

DB = dict(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)

COMPETITION_ID = 1
TARGET_NEW = 10
NEW_PASSWORD = "review2026"


def bcrypt_jstyle(plain: str) -> str:
    """与 jbcrypt 0.4 一致：$2a$ + cost 8（勿用默认 $2b$）。"""
    salt = bcrypt.gensalt(rounds=8, prefix=b"2a")
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("ascii")


def load_registrations(cur, competition_id: int):
    cur.execute(
        """
        SELECT r.id, r.institution_id, r.group_type
        FROM registrations r
        WHERE r.competition_id = %s
        ORDER BY r.id
        """,
        (competition_id,),
    )
    return cur.fetchall()


def load_reviewer_task_pairs(cur):
    cur.execute(
        "SELECT reviewer_id, registration_id FROM review_tasks WHERE reviewer_id IS NOT NULL"
    )
    return set((r[0], r[1]) for r in cur.fetchall())


def load_reviewer_load(cur):
    cur.execute(
        """
        SELECT reviewer_id, COUNT(*) FROM review_tasks
        WHERE reviewer_id IS NOT NULL GROUP BY reviewer_id
        """
    )
    return {r[0]: r[1] for r in cur.fetchall()}


def get_max_load(cur):
    cur.execute(
        "SELECT setting_value FROM system_settings WHERE setting_key = 'reviewerMaxLoad'"
    )
    row = cur.fetchone()
    return int(row[0]) if row else 20


def already_dual_pending(cur, reviewer_id: int) -> bool:
    cur.execute(
        """
        SELECT
          SUM(CASE WHEN stage='BOOK' AND status='PENDING' THEN 1 ELSE 0 END) AS bp,
          SUM(CASE WHEN stage='INTERVIEW' AND status='PENDING' THEN 1 ELSE 0 END) AS ip
        FROM review_tasks WHERE reviewer_id = %s
        """,
        (reviewer_id,),
    )
    row = cur.fetchone()
    return row and (row[0] or 0) > 0 and (row[1] or 0) > 0


def pick_registration(regs, pairs, reviewer_id, r_inst_id, stage: str, occupied_reg: int | None):
    """选一条可分配的报名 id；occupied_reg 表示本评委本轮已占用的另一条报名，不能重复。"""
    for rid, inst_id, gtype in regs:
        if occupied_reg is not None and rid == occupied_reg:
            continue
        if (reviewer_id, rid) in pairs:
            continue
        if r_inst_id is not None and inst_id is not None and r_inst_id == inst_id:
            continue
        if stage == "INTERVIEW" and gtype != "ADVANCED":
            continue
        return rid
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    conn = pymysql.connect(**DB)
    cur = conn.cursor()

    regs = load_registrations(cur, COMPETITION_ID)
    pairs = load_reviewer_task_pairs(cur)
    loads = load_reviewer_load(cur)
    max_load = get_max_load(cur)

    cur.execute(
        """
        SELECT id, phone, name, institution_id
        FROM user_accounts
        WHERE role = 'REVIEWER' AND enabled = 1
        ORDER BY id
        """
    )
    all_reviewers = cur.fetchall()

    candidates = []
    for uid, phone, name, inst_id in all_reviewers:
        if already_dual_pending(cur, uid):
            continue
        load = loads.get(uid, 0)
        if load + 2 > max_load:
            continue
        candidates.append((uid, phone, name, inst_id))

    created = []
    now = datetime.now()

    for uid, phone, name, r_inst in candidates:
        if len(created) >= TARGET_NEW:
            break
        book_reg = pick_registration(regs, pairs, uid, r_inst, "BOOK", None)
        if not book_reg:
            continue
        int_reg = pick_registration(regs, pairs, uid, r_inst, "INTERVIEW", book_reg)
        if not int_reg:
            continue

        if args.dry_run:
            created.append((uid, phone, name, book_reg, int_reg))
            pairs.add((uid, book_reg))
            pairs.add((uid, int_reg))
            loads[uid] = loads.get(uid, 0) + 2
            continue

        cur.execute(
            """
            INSERT INTO review_tasks
            (registration_id, reviewer_id, stage, status, created_at, updated_at)
            VALUES (%s, %s, 'BOOK', 'PENDING', %s, %s)
            """,
            (book_reg, uid, now, now),
        )
        cur.execute(
            """
            INSERT INTO review_tasks
            (registration_id, reviewer_id, stage, status, created_at, updated_at)
            VALUES (%s, %s, 'INTERVIEW', 'PENDING', %s, %s)
            """,
            (int_reg, uid, now, now),
        )
        pairs.add((uid, book_reg))
        pairs.add((uid, int_reg))
        loads[uid] = loads.get(uid, 0) + 2
        hp = bcrypt_jstyle(NEW_PASSWORD)
        cur.execute("UPDATE user_accounts SET password = %s WHERE id = %s", (hp, uid))
        created.append((uid, phone, name, book_reg, int_reg))

    if not args.dry_run and created:
        conn.commit()

    print(f"竞赛 ID={COMPETITION_ID}，maxLoad={max_load}")
    print(f"本次{'[dry-run] ' if args.dry_run else ''}新增双待评评委数: {len(created)} / 目标 {TARGET_NEW}\n")

    for row in created:
        print(f"  id={row[0]}  {row[2]}  {row[1]}  BOOK→reg {row[3]}  INTERVIEW→reg {row[4]}")

    if len(created) < TARGET_NEW:
        print(
            f"\n⚠ 未满 {TARGET_NEW} 人：可能候选评委不足、或负荷已满、或无合适报名（回避/进阶组）。"
        )

    if not args.dry_run and created:
        print(f"\n以上账号密码已设为: {NEW_PASSWORD}")
        print("完整清单（含原本就双待评的）请执行: python scripts/setup_reviewer_review2026.py --dry-run")

    conn.close()


if __name__ == "__main__":
    main()
