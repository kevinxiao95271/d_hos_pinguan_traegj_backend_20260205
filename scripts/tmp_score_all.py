import pymysql, requests, random, io, sys
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor()

admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone":"13800000005","password":"ops2026"}).json()["data"]["token"]
ah = {"Authorization": f"Bearer {admin_token}"}

# 取所有场次
sessions = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=ah).json()["data"]

# 取 30 个评委（已重置密码）
cur.execute("""
    SELECT id, name, phone FROM user_accounts
    WHERE role='REVIEWER' AND enabled=1
    ORDER BY id LIMIT 30
""")
all_revs = cur.fetchall()
print(f"评委总数: {len(all_revs)}")

# 每个场次分配 5 个评委（从30个里按场次索引轮转）
print("\n=== 分配评委到所有场次 ===")
sess_rev_map = {}  # session_code -> [(rev_id, rev_phone), ...]
for i, sess in enumerate(sessions):
    code = sess["sessionCode"]
    # 每场取5个评委（轮转）
    revs = [all_revs[(i*5 + j) % len(all_revs)] for j in range(5)]
    sess_rev_map[code] = revs
    for rev_id, rev_name, rev_phone in revs:
        resp = requests.post(
            f"{BASE}/api/admin/final/sessions/{requests.utils.quote(code, safe='')}/assign-reviewer",
            params={"competitionId": 1, "reviewerId": rev_id},
            headers=ah)
        if resp.status_code != 200:
            print(f"  分配失败 {rev_phone}→{code[:15]}: {resp.text[:40]}")

print("分配完成")

# 评分工具函数
def rs(lo, hi, seed):
    random.seed(seed)
    return round((lo + (hi - lo) * random.random()) * 2) / 2

def make_payload(sf, seed):
    if sf == "QCC":
        return {"scoreForm":"QCC","plan":rs(7.5,10,seed),"problem":rs(11.5,15,seed+1),
                "action":rs(11.5,15,seed+2),"success":rs(15.5,20,seed+3),
                "review":rs(3.5,5,seed+4),"operation":rs(11.5,15,seed+5),"presentation":rs(15.5,20,seed+6)}
    elif sf == "QFD":
        return {"scoreForm":"QFD","plan":rs(11.5,15,seed),"problem":rs(19.5,25,seed+1),
                "action":rs(19.5,25,seed+2),"success":rs(19.5,25,seed+3),"review":rs(7.5,10,seed+4)}
    else:
        return {"scoreForm":"NON_QCC","plan":rs(11.5,15,seed),"problem":rs(7.5,10,seed+1),
                "action":rs(7.5,10,seed+2),"success":rs(15.5,20,seed+3),"review":rs(7.5,10,seed+4),
                "operation":rs(7.5,10,seed+5),"presentation":rs(11.5,15,seed+6),"item8":rs(7.5,10,seed+7)}

# 每位评委：提交大部分，保留 1 个草稿 + 1 个不打分（PENDING）
print("\n=== 评委打分 ===")
total_submit = 0
total_draft = 0

for rev_id, rev_name, rev_phone in all_revs:
    lr = requests.post(f"{BASE}/api/auth/login-with-password",
                       json={"phone": rev_phone, "password": "user123"})
    data = lr.json().get("data")
    if not data:
        print(f"  {rev_phone} 登录失败"); continue
    rh = {"Authorization": f"Bearer {data['token']}"}

    tasks = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rh).json().get("data", [])
    pending_tasks = [t for t in tasks if t["status"] == "PENDING"]

    if not pending_tasks:
        continue

    # 最后2个任务留着：倒数第1个保持PENDING，倒数第2个保存草稿
    submit_tasks = pending_tasks[:-2] if len(pending_tasks) > 2 else pending_tasks[:-1] if len(pending_tasks) > 1 else []
    draft_task = pending_tasks[-2] if len(pending_tasks) >= 2 else None
    # 最后1个保持PENDING，不动

    for task in submit_tasks:
        tid = task["taskId"]
        sf = task.get("scoreForm", "QCC")
        sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/submit",
                          json=make_payload(sf, tid * 17 + rev_id), headers=rh)
        if sr.status_code == 200:
            total_submit += 1
        else:
            print(f"  提交失败 tid={tid}: {sr.text[:60]}")

    if draft_task:
        tid = draft_task["taskId"]
        sf = draft_task.get("scoreForm", "QCC")
        sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/draft",
                          json=make_payload(sf, tid * 17 + rev_id), headers=rh)
        if sr.status_code == 200:
            total_draft += 1

print(f"提交: {total_submit} 条，草稿: {total_draft} 条")

# 同步更新旧打分记录的 total（确保100分制）
print("\n=== 修正旧打分记录total为100分制 ===")
cur.execute("""
    SELECT rs.id, rs.score_form FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    WHERE rt.stage = 'FINAL' AND (rs.total IS NULL OR rs.total < 50)
""")
bad = cur.fetchall()
print(f"需修正: {len(bad)} 条")
for score_id, sf in bad:
    random.seed(score_id * 31)
    def r2(lo, hi): return round((lo + (hi-lo)*random.random()) * 2) / 2
    if sf == 'QCC':
        plan=r2(7.5,10); problem=r2(11.5,15); action=r2(11.5,15); success=r2(15.5,20)
        review_=r2(3.5,5); operation=r2(11.5,15); presentation=r2(15.5,20)
        total = plan+problem+action+success+review_+operation+presentation
        cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=%s,presentation=%s,item8=NULL,total=%s WHERE id=%s",
                    (plan,problem,action,success,review_,operation,presentation,round(total,1),score_id))
    elif sf == 'QFD':
        plan=r2(11.5,15); problem=r2(19.5,25); action=r2(19.5,25); success=r2(19.5,25); review_=r2(7.5,10)
        total = plan+problem+action+success+review_
        cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=NULL,presentation=NULL,item8=NULL,total=%s WHERE id=%s",
                    (plan,problem,action,success,review_,round(total,1),score_id))
    else:
        plan=r2(11.5,15); problem=r2(7.5,10); action=r2(7.5,10); success=r2(15.5,20)
        review_=r2(7.5,10); operation=r2(7.5,10); presentation=r2(11.5,15); item8=r2(7.5,10)
        total = plan+problem+action+success+review_+operation+presentation+item8
        cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=%s,presentation=%s,item8=%s,total=%s WHERE id=%s",
                    (plan,problem,action,success,review_,operation,presentation,item8,round(total,1),score_id))
conn.commit()
print("修正完成")

# 重算排名
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=ah)
print(f"\n排名计算: {cr.json().get('data','')}")

# 验证三天分布
rr = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=ah)
items = rr.json().get("data", [])
from collections import Counter
date_cnt = Counter(i["sessionDate"] for i in items)
sess_cnt = Counter(i["sessionCode"] for i in items)
print(f"排名: {dict(sorted(date_cnt.items()))} 共{len(sess_cnt)}个场次")

# 验证状态
cur.execute("SELECT status, COUNT(*) FROM review_tasks WHERE stage='FINAL' GROUP BY status")
print("\nFINAL任务状态:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}条")

conn.close()
