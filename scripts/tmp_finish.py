import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205',
          charset='utf8mb4', connect_timeout=30)

# 1. 修正旧打分 total 为 100 分制（分批，每批 50 条重连）
print("=== 修正旧打分记录 total ===")
def get_conn():
    return pymysql.connect(**DB)

conn = get_conn()
cur = conn.cursor()
cur.execute("""
    SELECT rs.id, rs.score_form FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    WHERE rt.stage = 'FINAL' AND (rs.total IS NULL OR rs.total < 50)
""")
bad = cur.fetchall()
conn.close()
print(f"需修正: {len(bad)} 条")

def r2(lo, hi, seed_val):
    random.seed(seed_val)
    return round((lo + (hi - lo) * random.random()) * 2) / 2

BATCH = 50
for i in range(0, len(bad), BATCH):
    chunk = bad[i:i+BATCH]
    conn = get_conn(); cur = conn.cursor()
    for score_id, sf in chunk:
        s = score_id * 31
        if sf == 'QCC':
            plan=r2(7.5,10,s); prob=r2(11.5,15,s+1); act=r2(11.5,15,s+2)
            succ=r2(15.5,20,s+3); rev=r2(3.5,5,s+4); op=r2(11.5,15,s+5); pres=r2(15.5,20,s+6)
            total=round(plan+prob+act+succ+rev+op+pres,1)
            cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=%s,presentation=%s,item8=NULL,total=%s WHERE id=%s",
                        (plan,prob,act,succ,rev,op,pres,total,score_id))
        elif sf == 'QFD':
            plan=r2(11.5,15,s); prob=r2(19.5,25,s+1); act=r2(19.5,25,s+2)
            succ=r2(19.5,25,s+3); rev=r2(7.5,10,s+4)
            total=round(plan+prob+act+succ+rev,1)
            cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=NULL,presentation=NULL,item8=NULL,total=%s WHERE id=%s",
                        (plan,prob,act,succ,rev,total,score_id))
        else:
            plan=r2(11.5,15,s); prob=r2(7.5,10,s+1); act=r2(7.5,10,s+2)
            succ=r2(15.5,20,s+3); rev=r2(7.5,10,s+4); op=r2(7.5,10,s+5)
            pres=r2(11.5,15,s+6); item8=r2(7.5,10,s+7)
            total=round(plan+prob+act+succ+rev+op+pres+item8,1)
            cur.execute("UPDATE review_scores SET plan=%s,problem=%s,action=%s,success=%s,review=%s,operation=%s,presentation=%s,item8=%s,total=%s WHERE id=%s",
                        (plan,prob,act,succ,rev,op,pres,item8,total,score_id))
    conn.commit(); conn.close()
    print(f"  修正 {i+len(chunk)}/{len(bad)}")

# 2. 重算排名
print("\n=== 重算排名 ===")
token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone":"13800000005","password":"ops2026"}).json()["data"]["token"]
ah = {"Authorization": f"Bearer {token}"}
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=ah)
print("排名计算结果:", cr.json().get("data",""))

# 3. 验证排名分布
items = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=ah).json().get("data",[])
from collections import Counter
print(f"排名总条目: {len(items)}")
dc = Counter(i["sessionDate"] for i in items)
for d,c in sorted(dc.items()):
    print(f"  {d}: {c} 个项目")

# 4. 任务状态统计
conn = get_conn(); cur = conn.cursor()
cur.execute("SELECT status, COUNT(*) FROM review_tasks WHERE stage='FINAL' GROUP BY status")
print("\nFINAL 任务状态:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} 条")
conn.close()
