import pymysql, openpyxl, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

# ── Step1: 解析 Excel 21个场次结构 ──────────────────────────────────────────
wb = openpyxl.load_workbook(
    'd:/iCode/cursor/d_hos_pinguan_traegj_backend_20260205/现场竞赛项目分组及评分表类型 - 发工程师(1).xlsx',
    data_only=True)

sessions = []  # [(date, code, [(order, score_form), ...]), ...]
for i, name in enumerate(wb.sheetnames):
    if i == 0:
        continue
    m = re.match(r'^(\d+\.\d+)', name)
    date = m.group(1) if m else ''
    code = re.sub(r'^\d+\.\d+', '', name)
    code = re.sub(r'（[^）]*）', '', code).strip()
    code = re.sub(r'\([^)]*\)', '', code).strip()

    ws = wb[name]
    rows_data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        order = row[1]
        sf_raw = str(row[6]).strip() if row[6] else ''
        if not order:
            continue
        if sf_raw == 'QCC':
            sf = 'QCC'
        elif sf_raw == 'QFD':
            sf = 'QFD'
        elif '非' in sf_raw:
            sf = 'NON_QCC'
        else:
            continue
        rows_data.append((int(order), sf))
    if rows_data:
        sessions.append((date, code, rows_data))

print(f'解析到 {len(sessions)} 个专场，共 {sum(len(r) for _,_,r in sessions)} 个项目槽')

# ── Step2: 取所有可用 reg ID ─────────────────────────────────────────────────
cur.execute("SELECT id FROM registrations WHERE competition_id=1 AND status IN ('SUBMITTED','APPROVED') ORDER BY id")
all_ids = [r[0] for r in cur.fetchall()]
total_ids = len(all_ids)
print(f'可用 registration 数量: {total_ids}')

# ── Step3: 清空旧 final 数据 ─────────────────────────────────────────────────
cur.execute("DELETE rs FROM review_scores rs JOIN review_tasks rt ON rs.review_task_id=rt.id WHERE rt.stage='FINAL'")
cur.execute("DELETE FROM review_tasks WHERE stage='FINAL'")
cur.execute("DELETE FROM final_ranking_snapshots")
cur.execute("UPDATE registrations SET final_session_code=NULL, final_session_order=NULL, final_score_form=NULL, final_session_date=NULL")
conn.commit()
print('清空完成')

# ── Step4: 按场次权重比例分配 ID（每个 ID 只用一次）─────────────────────────
# 先算每个场次应分到多少个（按项目数占比 * total_ids）
total_slots = sum(len(r) for _, _, r in sessions)
session_alloc = []
remaining = total_ids
for i, (date, code, rows) in enumerate(sessions):
    if i == len(sessions) - 1:
        count = remaining
    else:
        count = max(1, round(len(rows) / total_slots * total_ids))
        remaining -= count
    session_alloc.append(count)

# 打散 ID，按场次顺序切分
id_cursor = 0
assigned_total = 0
for (date, code, rows), alloc in zip(sessions, session_alloc):
    batch = all_ids[id_cursor: id_cursor + alloc]
    id_cursor += alloc
    if not batch:
        break
    # 从该场次的 rows 里取前 alloc 个槽位
    for j, rid in enumerate(batch):
        if j >= len(rows):
            break
        order, sf = rows[j]
        cur.execute(
            'UPDATE registrations SET final_session_date=%s, final_session_code=%s, final_session_order=%s, final_score_form=%s WHERE id=%s',
            (date, code, order, sf, rid)
        )
        assigned_total += 1

conn.commit()
print(f'共写入 {assigned_total} 条')

# ── Step5: 验证 ──────────────────────────────────────────────────────────────
cur.execute("""
    SELECT final_session_date, final_session_code, COUNT(*) as cnt,
           SUM(CASE WHEN final_score_form='QCC' THEN 1 ELSE 0 END) as qcc,
           SUM(CASE WHEN final_score_form='QFD' THEN 1 ELSE 0 END) as qfd,
           SUM(CASE WHEN final_score_form='NON_QCC' THEN 1 ELSE 0 END) as non
    FROM registrations
    WHERE final_session_code IS NOT NULL
    GROUP BY final_session_date, final_session_code
    ORDER BY final_session_date, final_session_code
""")
print('\n日期 | 专场 | 项目数(QCC/QFD/非QCC)')
for r in cur.fetchall():
    print(f'  {r[0]} | {r[1]} | {r[2]}项 (QCC:{r[3]} QFD:{r[4]} 非QCC:{r[5]})')

conn.close()
