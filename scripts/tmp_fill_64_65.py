import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone": "13800000005", "password": "ops2026"}).json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 取 6.4 / 6.5 的场次
r = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
sessions_64_65 = [s for s in r.json()["data"] if s["sessionDate"] in ("6.4", "6.5")]
print(f"6.4+6.5 场次数: {len(sessions_64_65)}")

# 取前3个评委
cur.execute("SELECT id, phone FROM user_accounts WHERE role='REVIEWER' AND enabled=1 LIMIT 3")
reviewers = cur.fetchall()
print(f"评委: {[r[1] for r in reviewers]}")

# 分配评委到 6.4/6.5 所有场次
for sess in sessions_64_65:
    code = sess["sessionCode"]
    for rev_id, rev_phone in reviewers:
        resp = requests.post(
            f"{BASE}/api/admin/final/sessions/{requests.utils.quote(code, safe='')}/assign-reviewer",
            params={"competitionId": 1, "reviewerId": rev_id},
            headers=headers)
        msg = resp.json().get('data', '')[:30] if resp.status_code == 200 else f"err{resp.status_code}"
        print(f"  {rev_phone} → {code[:18]}: {msg}")

# 每位评委登录提交打分
def rs(lo, hi, seed):
    random.seed(seed)
    v = lo + (hi - lo) * random.random()
    return round(v * 2) / 2

def make_payload(sf, seed):
    if sf == "QCC":
        return {"scoreForm":"QCC",
                "plan": rs(7.5,10,seed), "problem": rs(11.5,15,seed+1),
                "action": rs(11.5,15,seed+2), "success": rs(15.5,20,seed+3),
                "review": rs(3.5,5,seed+4), "operation": rs(11.5,15,seed+5),
                "presentation": rs(15.5,20,seed+6)}
    elif sf == "QFD":
        return {"scoreForm":"QFD",
                "plan": rs(11.5,15,seed), "problem": rs(19.5,25,seed+1),
                "action": rs(19.5,25,seed+2), "success": rs(19.5,25,seed+3),
                "review": rs(7.5,10,seed+4)}
    else:
        return {"scoreForm":"NON_QCC",
                "plan": rs(11.5,15,seed), "problem": rs(7.5,10,seed+1),
                "action": rs(7.5,10,seed+2), "success": rs(15.5,20,seed+3),
                "review": rs(7.5,10,seed+4), "operation": rs(7.5,10,seed+5),
                "presentation": rs(11.5,15,seed+6), "item8": rs(7.5,10,seed+7)}

total_ok = 0
for rev_id, rev_phone in reviewers:
    lr = requests.post(f"{BASE}/api/auth/login-with-password",
                       json={"phone": rev_phone, "password": "user123"})
    data = lr.json().get("data")
    if not data:
        print(f"  {rev_phone} 登录失败"); continue
    rev_headers = {"Authorization": f"Bearer {data['token']}"}
    tasks = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rev_headers).json().get("data", [])
    # 只提交 PENDING 状态的（6.4/6.5新分配的）
    pending = [t for t in tasks if t["status"] == "PENDING"]
    print(f"\n{rev_phone}: {len(pending)} 个待评分任务")
    for task in pending:
        tid = task["taskId"]
        sf = task.get("scoreForm", "QCC")
        payload = make_payload(sf, tid * 13 + rev_id)
        sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/submit",
                          json=payload, headers=rev_headers)
        if sr.status_code == 200:
            total_ok += 1
        else:
            print(f"  任务{tid} 失败: {sr.text[:60]}")

print(f"\n提交完成: {total_ok} 条")

# 重算排名
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=headers)
print(f"排名计算: {cr.json().get('data','')}")

# 验证三天都有数据
rr = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=headers)
items = rr.json().get("data", [])
from collections import Counter
date_cnt = Counter(i["sessionDate"] for i in items)
print(f"\n各天排名条数: {dict(date_cnt)}")
sess_cnt = Counter(i["sessionCode"] for i in items)
print(f"场次数: {len(sess_cnt)}")

conn.close()
