import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone":"13800000005","password":"ops2026"}).json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 取之前没有参与过 FINAL 任务的评委（取6个）
cur.execute("""
    SELECT id, name, phone FROM user_accounts
    WHERE role='REVIEWER' AND enabled=1
    AND id NOT IN (SELECT DISTINCT reviewer_id FROM review_tasks WHERE stage='FINAL')
    ORDER BY id
    LIMIT 6
""")
new_revs = cur.fetchall()
print(f"新评委 {len(new_revs)} 人:")
for rid, name, phone in new_revs:
    print(f"  {phone}  {name}")

# 重置密码为 user123
import bcrypt
pwd_hash = bcrypt.hashpw(b'user123', bcrypt.gensalt(rounds=10)).decode('utf-8').replace('$2b$','$2a$')
ids = [r[0] for r in new_revs]
cur.execute(f"UPDATE user_accounts SET password=%s WHERE id IN ({','.join(['%s']*len(ids))})", [pwd_hash]+ids)
conn.commit()
print("密码已重置为 user123")

# 取几个场次（取中间几个，避开已有大量数据的6.3）
r = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
sessions = r.json()["data"]
# 取 6.4 的前3个 + 6.5 的前3个
target_sessions = [s for s in sessions if s["sessionDate"] == "6.4"][:3] + \
                  [s for s in sessions if s["sessionDate"] == "6.5"][:3]
print(f"\n目标场次({len(target_sessions)}个): {[s['sessionCode'][:15] for s in target_sessions]}")

# 前3个评委：分配任务 + 保存草稿
# 后3个评委：只分配任务，不打分（PENDING）
draft_revs = new_revs[:3]
pending_revs = new_revs[3:]

# 分配所有新评委到目标场次
for sess in target_sessions:
    code = sess["sessionCode"]
    for rid, name, phone in new_revs:
        resp = requests.post(
            f"{BASE}/api/admin/final/sessions/{requests.utils.quote(code, safe='')}/assign-reviewer",
            params={"competitionId": 1, "reviewerId": rid},
            headers=headers)
        msg = resp.json().get('data','')[:25] if resp.status_code==200 else f"err"
        print(f"  {phone} → {code[:16]}: {msg}")

# 前3个评委打草稿
def rs(lo, hi, seed):
    random.seed(seed)
    return round((lo + (hi-lo)*random.random()) * 2) / 2

def make_draft(sf, seed):
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

draft_total = 0
for rid, name, phone in draft_revs:
    lr = requests.post(f"{BASE}/api/auth/login-with-password", json={"phone":phone,"password":"user123"})
    data = lr.json().get("data")
    if not data:
        print(f"  {phone} 登录失败"); continue
    rh = {"Authorization": f"Bearer {data['token']}"}
    tasks = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rh).json().get("data",[])
    pending = [t for t in tasks if t["status"] == "PENDING"]
    # 每人只保存前2个任务的草稿
    for task in pending[:2]:
        tid = task["taskId"]
        sf = task.get("scoreForm","QCC")
        sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/draft",
                          json=make_draft(sf, tid*7), headers=rh)
        if sr.status_code == 200:
            draft_total += 1
            print(f"  草稿 {phone} 任务{tid}({sf}) ✓")
        else:
            print(f"  草稿失败 {sr.text[:60]}")

print(f"\n草稿保存: {draft_total} 条")

# 验证状态
cur.execute("""
    SELECT ua.name, ua.phone, rt.status, COUNT(*) as cnt
    FROM review_tasks rt JOIN user_accounts ua ON ua.id=rt.reviewer_id
    WHERE rt.stage='FINAL' AND ua.id IN ({})
    GROUP BY ua.id, ua.name, ua.phone, rt.status
    ORDER BY ua.phone, rt.status
""".format(','.join(['%s']*len(ids))), ids)
print("\n新评委任务状态:")
for row in cur.fetchall():
    print(f"  {row[1]}({row[0]})  {row[2]}: {row[3]}条")

conn.close()
print("\n完成。后3个评委为纯PENDING状态（未打分）:")
for rid, name, phone in pending_revs:
    print(f"  {phone}  {name}")
