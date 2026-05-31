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
headers = {"Authorization": f"Bearer {admin_token}"}

# 获取机构ID池（随机取）
cur.execute("SELECT id FROM institutions LIMIT 100")
inst_ids = [r[0] for r in cur.fetchall()]

# 获取所有场次
r = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
sessions = r.json()["data"]

# 每场次最少目标数
def target_count(code):
    if '进阶' in code: return 15
    return 13

# 当前每场已有多少项目
cur.execute("""
    SELECT final_session_code, COUNT(*) FROM registrations
    WHERE competition_id=1 AND final_session_code IS NOT NULL
    GROUP BY final_session_code
""")
current = {r[0]: r[1] for r in cur.fetchall()}

# 取 applicant_id 样本
cur.execute("SELECT id FROM user_accounts WHERE role='APPLICANT' LIMIT 1")
row = cur.fetchone()
applicant_id = row[0] if row else None

now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.000000')

tool_topics = [
    '品管圈-问题解决','品管圈-课题达成','PDCA','QFD','六西格玛','精益管理','5S管理',
    '根因分析','标杆学习','流程再造','循证医学','专案改善'
]
areas = [
    '护理质量','医疗安全','院感控制','药事管理','后勤保障','信息化建设',
    '患者满意度','手术室管理','急诊流程','门诊优化','慢病管理','康复服务'
]
hospital_names = [
    '市第一人民医院','市中心医院','市人民医院','省立医院','附属医院',
    '妇幼保健院','中医医院','肿瘤医院','儿童医院','口腔医院'
]

total_created = 0

for sess in sessions:
    code = sess["sessionCode"]
    date = sess["sessionDate"]
    sf = None
    if sess["qccCount"] > 0 and sess["qfdCount"] == 0 and sess["nonQccCount"] == 0:
        sf = "QCC"
    elif sess["qfdCount"] > 0 and sess["nonQccCount"] == 0:
        sf = "QFD"
    elif sess["nonQccCount"] > 0 and sess["qccCount"] == 0:
        sf = "NON_QCC"
    else:
        sf = "QCC"  # 混合场次默认

    have = current.get(code, 0)
    need = max(0, target_count(code) - have)
    if need == 0:
        print(f"  {code[:20]}: 已有{have}项，无需补充")
        continue

    # group_type
    if '进阶' in code: gt = 'ADVANCED'
    elif '基层' in code: gt = 'GRASSROOTS'
    else: gt = 'COMPREHENSIVE'

    # group_code 取一个合理值
    gc = 'A1' if gt == 'ADVANCED' else ('B1' if gt == 'GRASSROOTS' else 'C1')

    created = 0
    start_order = have + 1
    for i in range(need):
        random.seed(hash(code) + i + 9999)
        topic = random.choice(tool_topics)
        area = random.choice(areas)
        hosp = random.choice(hospital_names)
        pname = f"{area}-{topic}-{hosp}-TEST{total_created+i+1:03d}"
        inst_id = random.choice(inst_ids) if inst_ids else None

        cur.execute("""
            INSERT INTO registrations
            (created_at, group_code, group_type, project_name, status, submitted_at,
             applicant_id, competition_id, institution_id,
             final_session_date, final_session_code, final_session_order, final_score_form)
            VALUES (%s,%s,%s,%s,'SUBMITTED',%s,%s,1,%s,%s,%s,%s,%s)
        """, (now_str, gc, gt, pname, now_str,
              applicant_id, inst_id,
              date, code, start_order + i, sf))
        created += 1

    conn.commit()
    total_created += created
    print(f"  {code[:22]}: 原{have}项 → 补{created}项，共{have+created}项")

print(f"\n合计新增: {total_created} 条测试项目")

# 验证
r2 = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
print("\n更新后各场次项目数:")
for s in r2.json()["data"]:
    flag = "✓" if s["totalCount"] >= target_count(s["sessionCode"]) else "✗"
    print(f"  {flag} {s['sessionDate']} {s['sessionCode'][:22]:22s} {s['totalCount']}项")

conn.close()
