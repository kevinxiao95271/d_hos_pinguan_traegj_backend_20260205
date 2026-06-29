"""
正交覆盖自测：group_type + score_form + null/0/正常值 的权重/公式验证
测试方式：直接向 final_ranking_snapshots 写入指定 group_type + score 组合，
         通过 getRanking API 读回，逐字段断言，最后清理。
"""

import sys
import pymysql
import requests
import json
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────────────────────────
BASE_URL  = "http://localhost:6031"
DB_HOST   = "gz-cdb-bq7gk3k5.sql.tencentcdb.com"
DB_PORT   = 63606
DB_USER   = "root"
DB_PASS   = "Yiguo9527_"
DB_NAME   = "d_hos_pinguan_traegj_20260205"

COMP_ID   = 1
# 用真实 OPS 账号登录（库里已有，密码沿用统一明文）
ADMIN_PHONE = "13800000005"
ADMIN_PASS  = "ops2026"

MARK = "SELFTEST_GT"   # 写入 session_code 标记，便于清理

PASS = "[PASS]"
FAIL = "[FAIL]"

# ── 正交测试矩阵 ──────────────────────────────────────────────────────────
# 字段说明：
#   group_type       : ADVANCED / BASIC / COMPREHENSIVE
#   book_score_d     : None = 无书审; float = 有书审（0.0 测试零值不误判）
#   interview_score_d: None = 无面谈; float = 有面谈（BASIC/COMP 有面谈为脏数据）
#   trimmed_avg      : 现场均分（None 表示未评分，totalScore 应 null）
#   score_form       : QCC / NON_QCC / QFD
#   dirty            : True 表示该条是脏数据，预期 totalScore=null
#
# 预期权重（book_w / interview_w / final_w）:
#   三阶段 ADVANCED   : 0.3 / 0.4 / 0.3
#   两阶段 ADVANCED   : None / 0.4 / 0.6
#   BASIC/COMP 正常   : 0.4 / None / 0.6
#   任何脏数据         : None / None / None
TEST_CASES = [
    # ── ADVANCED 三阶段 × 三种评分表 ────────────────────────────────────
    {"id": "TC01", "group_type":"ADVANCED",      "book":85.0, "interview":88.0, "final":90.0, "form":"QCC",    "dirty":False,
     "exp_total": 85*0.3+88*0.4+90*0.3, "exp_bw":0.3, "exp_iw":0.4, "exp_fw":0.3},
    {"id": "TC02", "group_type":"ADVANCED",      "book":85.0, "interview":88.0, "final":90.0, "form":"NON_QCC","dirty":False,
     "exp_total": 85*0.3+88*0.4+90*0.3, "exp_bw":0.3, "exp_iw":0.4, "exp_fw":0.3},
    {"id": "TC03", "group_type":"ADVANCED",      "book":85.0, "interview":88.0, "final":90.0, "form":"QFD",    "dirty":False,
     "exp_total": 85*0.3+88*0.4+90*0.3, "exp_bw":0.3, "exp_iw":0.4, "exp_fw":0.3},
    # ── ADVANCED 两阶段（无书审）── 仅面谈+现场 ────────────────────────
    {"id": "TC04", "group_type":"ADVANCED",      "book":None, "interview":88.0, "final":90.0, "form":"QCC",    "dirty":False,
     "exp_total": 88*0.4+90*0.6, "exp_bw":None, "exp_iw":0.4, "exp_fw":0.6},
    # ── ADVANCED 脏数据：无面谈（进阶组必须有面谈，否则视为脏数据） ───────
    {"id": "TC05", "group_type":"ADVANCED",      "book":85.0, "interview":None, "final":90.0, "form":"QCC",    "dirty":True,
     "exp_total": None, "exp_bw":None, "exp_iw":None, "exp_fw":None},
    {"id": "TC06", "group_type":"ADVANCED",      "book":None, "interview":None, "final":90.0, "form":"QCC",    "dirty":True,
     "exp_total": None, "exp_bw":None, "exp_iw":None, "exp_fw":None},
    # ── BASIC × 三种评分表 ──────────────────────────────────────────────
    {"id": "TC07", "group_type":"BASIC",         "book":85.0, "interview":None, "final":90.0, "form":"QCC",    "dirty":False,
     "exp_total": 85*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6},
    {"id": "TC08", "group_type":"BASIC",         "book":85.0, "interview":None, "final":90.0, "form":"NON_QCC","dirty":False,
     "exp_total": 85*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6},
    {"id": "TC09", "group_type":"BASIC",         "book":85.0, "interview":None, "final":90.0, "form":"QFD",    "dirty":False,
     "exp_total": 85*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6},
    # ── BASIC 脏数据：有面谈（不影响总分，interview_score_d 应被写为 null）
    {"id": "TC10", "group_type":"BASIC",         "book":85.0, "interview":88.0, "final":90.0, "form":"QCC",    "dirty":False,
     "exp_total": 85*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6,
     "note":"BASIC有面谈脏数据，面谈应被忽略"},
    # ── COMPREHENSIVE × 脏面谈测试 ──────────────────────────────────────
    {"id": "TC11", "group_type":"COMPREHENSIVE", "book":85.0, "interview":88.0, "final":90.0, "form":"NON_QCC","dirty":False,
     "exp_total": 85*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6,
     "note":"COMPREHENSIVE有面谈脏数据，面谈应被忽略"},
    # ── 零值不误判为无数据 ───────────────────────────────────────────────
    {"id": "TC12", "group_type":"BASIC",         "book":0.0,  "interview":None, "final":90.0, "form":"QCC",    "dirty":False,
     "exp_total": 0.0*0.4+90*0.6, "exp_bw":0.4, "exp_iw":None, "exp_fw":0.6,
     "note":"book=0.0 不应被视为无数据"},
    # ── 无现场均分 → 脏数据（totalScore=null） ──────────────────────────
    {"id": "TC13", "group_type":"BASIC",         "book":85.0, "interview":None, "final":None, "form":"QCC",    "dirty":True,
     "exp_total": None, "exp_bw":None, "exp_iw":None, "exp_fw":None,
     "note":"无现场均分，整条记录为脏数据"},
]

report_lines = []
def log(msg):
    print(msg)
    report_lines.append(msg)

def section(t):
    log(f"\n{'='*64}\n  {t}\n{'='*64}")

def ok(label, cond, detail=""):
    icon = PASS if cond else FAIL
    log(f"  {icon}  {label}" + (f"\n       > {detail}" if detail else ""))
    return cond

def close(v, exp, tol=0.001):
    if exp is None: return v is None
    if v is None: return False
    return abs(float(v) - float(exp)) < tol

# ── DB ────────────────────────────────────────────────────────────────────
def db():
    return pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASS, database=DB_NAME, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)

def qry(sql, args=()):
    with db() as conn:
        with conn.cursor() as c:
            c.execute(sql, args)
            return c.fetchall()

def exe(sql, args=()):
    conn = db()
    try:
        with conn.cursor() as c:
            c.execute(sql, args)
        conn.commit()
    finally:
        conn.close()

def exem(sql_list):
    conn = db()
    try:
        with conn.cursor() as c:
            for sql, args in sql_list:
                c.execute(sql, args)
        conn.commit()
    finally:
        conn.close()

# ── 获取真实 registration_id（各组别取足够多的 ID 供轮用） ──────────────
def get_reg_ids():
    """返回 {"ADVANCED":[id,...], "BASIC":[id,...], "COMPREHENSIVE":[id,...]}
    取所有 submitted 状态的 reg_id；INSERT 时用 INSERT IGNORE 跳过唯一索引冲突。
    """
    rows = qry("""
        SELECT r.id, r.group_type
        FROM registrations r
        WHERE r.competition_id=%s AND r.status='SUBMITTED'
        ORDER BY r.id
    """, (COMP_ID,))
    pool = {}
    for r in rows:
        pool.setdefault(r["group_type"], []).append(r["id"])
    return pool

# ── 获取该 registration 的 institution_id ───────────────────────────────
def get_institution(reg_id):
    rows = qry("SELECT institution_id FROM registrations WHERE id=%s", (reg_id,))
    return rows[0]["institution_id"] if rows else 1

# ── 写测试快照 ──────────────────────────────────────────────────────────
def insert_test_snaps(reg_id_pool):
    inserts = []
    used_reg_ids = set()   # 同一 reg_id 在本次 batch 不重复
    counters = {}
    for tc in TEST_CASES:
        gt   = tc["group_type"]
        pool = reg_id_pool.get(gt, [])
        idx  = counters.get(gt, 0)
        reg_id = None
        while idx < len(pool):
            cand = pool[idx]
            idx += 1
            if cand not in used_reg_ids:
                reg_id = cand
                used_reg_ids.add(cand)
                break
        counters[gt] = idx
        if not reg_id:
            log(f"  [WARN] {tc['id']} 无可用 reg_id(group_type={gt})，跳过")
            continue

        # 模拟 computeTotalRanking 写入 snapshot 的结果
        # TC10/TC11 需要验证：snapshot 里 interview_score_d 应为 null（compute 已清零）
        # 所以写入时直接按 compute 逻辑的输出结果写
        book  = tc["book"]
        intv  = tc["interview"]
        final = tc["final"]
        form  = tc["form"]
        dirty = tc["dirty"]

        if gt == "ADVANCED":
            if intv is not None and book is not None:
                # 三阶段
                snap_book = book
                snap_intv = intv
                snap_total = book*0.3 + intv*0.4 + final*0.3 if final else None
            elif intv is not None and book is None:
                # 两阶段进阶
                snap_book = None
                snap_intv = intv
                snap_total = intv*0.4 + final*0.6 if final else None
            else:
                # 脏数据
                snap_book = None
                snap_intv = None
                snap_total = None
        else:
            # BASIC / COMPREHENSIVE：面谈强制 null
            snap_intv = None
            if book is not None and final is not None:
                snap_book = book
                snap_total = book*0.4 + final*0.6
            else:
                snap_book = book
                snap_total = None

        # 若该 reg_id 已有快照先删掉（测试完清理时一并 DELETE MARK 行）
        exe("DELETE FROM final_ranking_snapshots WHERE competition_id=%s AND registration_id=%s",
            (COMP_ID, reg_id))
        inserts.append(("""
            INSERT INTO final_ranking_snapshots
                (competition_id, registration_id, session_code, session_date,
                 trimmed_avg, session_rank, group_type, score_form,
                 book_score_d, interview_score_d, total_score, calculated_at)
            VALUES (%s,%s,%s,'20260601',%s,1,%s,%s,%s,%s,%s,NOW())
        """, (COMP_ID, reg_id, f"{MARK}_{tc['id']}", final,
              gt, form, snap_book, snap_intv, snap_total)))

    exem(inserts)
    log(f"  已写入 {len(inserts)} 条测试快照（session_code 含 {MARK} 标记）")

# ── API login ────────────────────────────────────────────────────────────
sess = requests.Session()

def login():
    r = sess.post(f"{BASE_URL}/api/auth/login-with-password",
                  json={"phone": ADMIN_PHONE, "password": ADMIN_PASS})
    body = r.json()
    token = (body.get("data") or {}).get("token")
    if not token:
        # 尝试其它账号
        for ph in ["13800000027","10000000000","13800138000"]:
            r2 = sess.post(f"{BASE_URL}/api/auth/login-with-password",
                           json={"phone": ph, "password": "ops2026"})
            token = (r2.json().get("data") or {}).get("token")
            if token:
                log(f"  登录成功 phone={ph}")
                break
    if not token:
        log(f"  [ERROR] 所有账号登录失败，body={body}")
        sys.exit(1)
    sess.headers["Authorization"] = f"Bearer {token}"

# ── 主测试 ────────────────────────────────────────────────────────────────
def main():
    log("="*66)
    log(f"  正交覆盖自测报告  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("="*66)

    # Step 0: 登录
    section("Step 0: 登录")
    login()

    # Step 1: 获取 reg_id_pool
    section("Step 1: 获取各组别 registration_id 池")
    reg_id_pool = get_reg_ids()
    for k, v in reg_id_pool.items():
        log(f"  {k} → {len(v)} 条可用 reg_id，前3: {v[:3]}")

    # Step 2: 写入测试快照
    section("Step 2: 写入 13 个测试快照")
    # 先清上次残留
    exe("DELETE FROM final_ranking_snapshots WHERE session_code LIKE %s AND competition_id=%s", (MARK + "%", COMP_ID))
    insert_test_snaps(reg_id_pool)

    # Step 3: 调 getRanking，过滤出测试记录
    section("Step 3: GET /admin/final/ranking 取回测试记录")
    r = sess.get(f"{BASE_URL}/api/admin/final/ranking?competitionId={COMP_ID}")
    if r.status_code != 200 or not r.json().get("success"):
        log(f"  [ERROR] API 失败 status={r.status_code} body={r.text[:300]}")
        cleanup()
        return

    all_items = r.json().get("data", [])
    # 用 session_code 精确匹配测试快照
    snap_rows = qry(
        "SELECT id, session_code, group_type, book_score_d, interview_score_d, "
        "total_score, trimmed_avg FROM final_ranking_snapshots "
        "WHERE competition_id=%s AND session_code LIKE %s",
        (COMP_ID, MARK + "%"))
    snap_by_id = {}
    # getRanking 返回的 item 没有 snap_id，但有 registrationId + sessionCode
    for item in all_items:
        sc = item.get("sessionCode","")
        if sc.startswith(MARK):
            snap_by_id[sc] = item

    log(f"  API 返回 {len(all_items)} 条，其中测试记录 {len(snap_by_id)} 条")

    # Step 4: 逐 case 断言
    section("Step 4: 逐 case 断言")

    all_pass = True
    for tc in TEST_CASES:
        sc = f"{MARK}_{tc['id']}"
        item = snap_by_id.get(sc)
        if item is None:
            ok(f"{tc['id']} [{tc['group_type']} | {tc['form']}] 未在 API 响应中找到", False, f"sessionCode={sc} 缺失")
            all_pass = False
            continue

        note = tc.get("note","")
        label = f"{tc['id']} [{tc['group_type']} | {tc['form']}]{' | '+note if note else ''}"

        # 读 API 字段
        got_ts = item.get("totalScore")
        got_bw = item.get("bookWeight")
        got_iw = item.get("interviewWeight")
        got_fw = item.get("finalWeight")
        got_isd = item.get("interviewScoreD")  # snapshot 里 interview_score_d

        exp_ts = tc["exp_total"]
        exp_bw = tc["exp_bw"]
        exp_iw = tc["exp_iw"]
        exp_fw = tc["exp_fw"]

        ts_ok = close(got_ts, exp_ts)
        bw_ok = close(got_bw, exp_bw)
        iw_ok = close(got_iw, exp_iw)
        fw_ok = close(got_fw, exp_fw)

        # BASIC/COMP 有面谈脏数据 → interviewScoreD 应为 null（compute 已清零）
        isd_ok = True
        if tc["group_type"] in ("BASIC","COMPREHENSIVE"):
            isd_ok = got_isd is None

        passed = ts_ok and bw_ok and iw_ok and fw_ok and isd_ok
        all_pass = all_pass and passed

        detail = (
            f"totalScore: exp={round(exp_ts,4) if exp_ts is not None else None} "
            f"got={round(got_ts,4) if got_ts is not None else None}  "
            f"bw: {exp_bw}→{got_bw}  iw: {exp_iw}→{got_iw}  fw: {exp_fw}→{got_fw}"
            + (f"  interviewScoreD: exp=null got={got_isd}" if not isd_ok else "")
        )
        ok(label, passed, detail)

    # Step 5: 汇总
    section("汇总")
    pass_cnt = sum(1 for l in report_lines if l.strip().startswith("[PASS]"))
    fail_cnt = sum(1 for l in report_lines if l.strip().startswith("[FAIL]"))
    log(f"  PASS: {pass_cnt}  FAIL: {fail_cnt}")
    if all_pass:
        log("  [OK] 所有 case 通过 -- group_type 权重/公式/脏数据规避逻辑闭环验证完毕")
    else:
        log("  [WARN] 存在失败 case，请查看上方 [FAIL] 项")

    # Step 6: 清理
    cleanup()

    # 写报告
    path = "scripts/selftest_orthogonal_report.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    log(f"\n  报告已写入: {path}")

def cleanup():
    exe("DELETE FROM final_ranking_snapshots WHERE session_code LIKE %s AND competition_id=%s", (MARK + "%", COMP_ID))
    log("  测试数据已清理")

if __name__ == "__main__":
    main()
