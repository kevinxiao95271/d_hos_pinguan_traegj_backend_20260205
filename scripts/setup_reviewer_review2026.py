#!/usr/bin/env python3
"""
查询：同时存在「书审 PENDING」与「面谈 PENDING」任务的 REVIEWER，
将密码重置为 review2026（BCrypt cost=8，与 PasswordService 一致）。

依赖: pip install pymysql bcrypt

用法:
  python scripts/setup_reviewer_review2026.py           # 查库并更新
  python scripts/setup_reviewer_review2026.py --dry-run # 只查不更新
"""
from __future__ import annotations

import argparse
import sys

try:
    import bcrypt
except ImportError:
    print("请先执行: pip install bcrypt", file=sys.stderr)
    sys.exit(1)

import pymysql

# 与仓库内其它脚本一致；生产请改环境变量或参数
DB = dict(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)

NEW_PASSWORD = "review2026"


def bcrypt_jstyle(plain: str) -> str:
    """
    必须与后端 PasswordService（org.mindrot.jbcrypt 0.4）一致。
    Python bcrypt 默认生成 $2b$，jbcrypt 常用 $2a$，混用会导致 checkpw 失败；
    故显式 prefix=2a、rounds=8。
    """
    salt = bcrypt.gensalt(rounds=8, prefix=b"2a")
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("ascii")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只查询与打印清单，不写库")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    conn = pymysql.connect(**DB)
    cur = conn.cursor()

    # 同时有书审待评 + 面谈待评的评委
    cur.execute(
        """
        SELECT ua.id, ua.phone, ua.name,
               ua.reviewer_group_code,
               ua.interview_group_code,
               SUM(CASE WHEN rt.stage = 'BOOK' AND rt.status = 'PENDING' THEN 1 ELSE 0 END) AS book_pending,
               SUM(CASE WHEN rt.stage = 'INTERVIEW' AND rt.status = 'PENDING' THEN 1 ELSE 0 END) AS int_pending,
               SUM(CASE WHEN rt.stage = 'BOOK' THEN 1 ELSE 0 END) AS book_total,
               SUM(CASE WHEN rt.stage = 'INTERVIEW' THEN 1 ELSE 0 END) AS int_total
        FROM review_tasks rt
        INNER JOIN user_accounts ua ON rt.reviewer_id = ua.id
        WHERE ua.role = 'REVIEWER'
        GROUP BY ua.id, ua.phone, ua.name, ua.reviewer_group_code, ua.interview_group_code
        HAVING book_pending > 0 AND int_pending > 0
        ORDER BY ua.id
        """
    )
    rows = cur.fetchall()

    if not rows:
        print("=== 未找到「同时有书审 PENDING + 面谈 PENDING」的评委 ===\n")
        cur.execute(
            """
            SELECT ua.id, ua.phone, ua.name,
                   SUM(CASE WHEN rt.stage = 'BOOK' AND rt.status = 'PENDING' THEN 1 ELSE 0 END) AS bp,
                   SUM(CASE WHEN rt.stage = 'INTERVIEW' AND rt.status = 'PENDING' THEN 1 ELSE 0 END) AS ip
            FROM review_tasks rt
            INNER JOIN user_accounts ua ON rt.reviewer_id = ua.id
            WHERE ua.role = 'REVIEWER'
            GROUP BY ua.id, ua.phone, ua.name
            HAVING bp > 0 OR ip > 0
            ORDER BY ua.id
            LIMIT 30
            """
        )
        alt = cur.fetchall()
        print("下列评委仅有单侧待评（供参考，未自动重置）：")
        for r in alt:
            print(f"  id={r[0]} phone={r[1]} name={r[2]} 书审待评={r[3]} 面谈待评={r[4]}")
        conn.close()
        return

    print("=== 将重置密码的评审专家（书审+面谈均有待评）===\n")

    checklist = []
    for r in rows:
        uid, phone, name, rg, ig, bp, ip, bt, it = r
        checklist.append((name, phone, NEW_PASSWORD, int(bp), int(ip), int(bt), int(it), rg or "", ig or ""))
        print(
            f"id={uid}  {name}  {phone}  "
            f"书审待评={bp}/{bt}  面谈待评={ip}/{it}  "
            f"reviewerGroup={rg} interviewGroup={ig}"
        )
        if not args.dry_run:
            cur.execute(
                "UPDATE user_accounts SET password = %s WHERE id = %s",
                (bcrypt_jstyle(NEW_PASSWORD), uid),
            )

    if not args.dry_run:
        conn.commit()
        print(f"\n已写入密码 BCrypt（明文统一为: {NEW_PASSWORD}）\n")
    else:
        print(f"\n[--dry-run] 未更新数据库。明文将设为: {NEW_PASSWORD}\n")

    print("--- 测试验证清单（复制到文档） ---\n")
    print("| 姓名 | 手机号 | 密码 | 书审待评 | 面谈待评 | 书审组码 | 面谈组码 |")
    print("|------|--------|------|----------|----------|----------|----------|")
    for name, phone, pwd, bp, ip, bt, it, rg, ig in checklist:
        print(f"| {name} | {phone} | {pwd} | {bp} | {ip} | {rg} | {ig} |")

    print(
        """
验证步骤建议：
1. POST /api/auth/login-with-password  body: {"phone":"手机号","password":"review2026"}
2. GET  /api/reviews/tasks  Authorization: Bearer <token>
   - 核对存在 stage=BOOK 且 status=PENDING 的任务
   - 核对存在 stage=INTERVIEW 且 status=PENDING 的任务
3. 分别对一条书审、一条面谈任务走提交打分接口完成闭环测试
"""
    )

    conn.close()


if __name__ == "__main__":
    main()
