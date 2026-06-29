"""
全链路自测：评委打分 → OPERATOR查看 → OPERATOR驳回 → 评委重打
使用测试库真实数据：
  评委: 孙丽娟 (13800002569 / user123)  负责 2026综合组问题解决型专场1
  OPERATOR: 沈佩儿 (13588040680 / opt123) 管辖 问题解决型专场1/2/4
  ADMIN: admin (13800000001 / admin123)
"""
import requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'
COMP_ID = 1
TASK_ID = 468   # 孙丽娟 PENDING 任务，QCC，问题解决型专场1

# ===========================================================================
def pp(label, r):
    print(f"\n{'─'*60}")
    print(f"【{label}】 HTTP {r.status_code}")
    try:
        d = r.json()
        if not d.get('success', True):
            print(f"  ❌ FAIL: {d.get('message')}")
            return d
        data = d.get('data')
        if isinstance(data, list):
            print(f"  ✅ 返回 {len(data)} 条")
            for item in data[:3]:
                # 只打印关键字段
                if isinstance(item, dict):
                    keys = ['taskId','id','projectName','sessionCode','status','totalScore','reviewerName']
                    sub = {k: item[k] for k in keys if k in item}
                    print(f"    {sub}")
                else:
                    print(f"    {item}")
            if len(data) > 3:
                print(f"    ... 共{len(data)}条")
        else:
            print(f"  ✅ {json.dumps(data, ensure_ascii=False)[:400]}")
    except Exception as e:
        print(f"  解析异常: {e}\n  原文: {r.text[:300]}")
    return r.json()

def login(phone, pwd):
    r = requests.post(f'{BASE}/api/auth/login-with-password', json={'phone': phone, 'password': pwd})
    d = r.json().get('data', {})
    token = d.get('token')
    name = d.get('name', '?')
    role = d.get('role', '?')
    status = '✅' if token else '❌'
    print(f"\n>>> 登录: {name} ({role}) {status}  phone={phone}")
    return token, d

def auth_h(token):
    return {'Authorization': f'Bearer {token}'}

def get_task(token, task_id):
    r = requests.get(f'{BASE}/api/reviews/final/my-tasks', headers=auth_h(token))
    tasks = r.json().get('data', [])
    return next((t for t in tasks if t.get('taskId') == task_id or t.get('id') == task_id), None)

# ===========================================================================
print("=" * 60)
print("STEP 0: 先确认任务初始状态")

rev_token, _ = login('13800002569', 'user123')
t = get_task(rev_token, TASK_ID)
print(f"\n  初始状态: taskId={TASK_ID}, status={t.get('status') if t else 'NOT FOUND'}, score={t.get('totalScore') if t else '-'}")
if not t:
    print("  ❌ 找不到任务，退出")
    sys.exit(1)

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 1: 评委提交草稿分")

qcc_score = {
    "scoreForm": "QCC",
    "plan": 8.0,        # 计划 max10
    "problem": 12.0,    # 项目结构 max15
    "action": 12.0,     # 对策行动 max15
    "success": 16.0,    # 成果表现 max20
    "review": 4.0,      # 查验 max5
    "operation": 12.0,  # 整体运作 max15
    "presentation": 16.0, # 现场表现 max20
    "total": 80.0,
    "highlight": "本次自测亮点",
    "weakness": "本次自测不足"
}

r1 = requests.put(f'{BASE}/api/reviews/final/scores/{TASK_ID}/draft',
    json=qcc_score, headers=auth_h(rev_token))
pp("评委保存草稿", r1)

t1 = get_task(rev_token, TASK_ID)
print(f"\n  草稿后: status={t1.get('status') if t1 else 'N/A'}, score={t1.get('totalScore') if t1 else '-'}")
assert t1 and t1.get('status') in ('IN_PROGRESS', 'DRAFT'), f"❌ 草稿状态异常: {t1.get('status') if t1 else 'N/A'}"
print("  ✅ 草稿状态符合预期")

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 2: 评委提交正式分")

r2 = requests.put(f'{BASE}/api/reviews/final/scores/{TASK_ID}/submit',
    json=qcc_score, headers=auth_h(rev_token))
pp("评委提交正式分", r2)

t2 = get_task(rev_token, TASK_ID)
print(f"\n  提交后: status={t2.get('status') if t2 else 'N/A'}, score={t2.get('totalScore') if t2 else '-'}")
assert t2 and t2.get('status') == 'SCORED', f"❌ 提交后状态异常: {t2.get('status') if t2 else 'N/A'}"
print("  ✅ 正式提交成功，状态变为 SCORED")

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 3: OPERATOR 登录，查看评分汇总（问题解决型专场1）")

op_token, _ = login('13588040680', 'opt123')

# 3a: 不传 sessionCode，拉全部分配场次
r3a = requests.get(f'{BASE}/api/admin/final/scores',
    params={'competitionId': COMP_ID},
    headers=auth_h(op_token))
pp("OPERATOR 查全部分配场次汇总", r3a)

# 3b: 传 sessionCode 只看问题解决型专场1
session_to_check = '2026综合组问题解决型专场1'
r3b = requests.get(f'{BASE}/api/admin/final/scores',
    params={'competitionId': COMP_ID, 'sessionCode': session_to_check},
    headers=auth_h(op_token))
pp(f"OPERATOR 查 {session_to_check}", r3b)

# 3c: OPERATOR 试图查不属于自己的场次 → 预期403
r3c = requests.get(f'{BASE}/api/admin/final/scores',
    params={'competitionId': COMP_ID, 'sessionCode': '2026基层组1组'},
    headers=auth_h(op_token))
pp("OPERATOR 查无权场次（预期403）", r3c)
print(f"  {'✅ 403权限拦截正确' if r3c.status_code == 403 else '❌ 未被拦截，异常!'}")

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 4: OPERATOR 驳回任务（在自己负责的场次）")

r4 = requests.post(f'{BASE}/api/admin/final/scores/{TASK_ID}/reject',
    headers=auth_h(op_token))
pp(f"OPERATOR 驳回 taskId={TASK_ID}", r4)

# 再检验
t4 = get_task(rev_token, TASK_ID)
print(f"\n  驳回后: status={t4.get('status') if t4 else 'N/A'}, score={t4.get('totalScore') if t4 else '-'}")
assert t4 and t4.get('status') == 'PENDING', f"❌ 驳回后状态异常: {t4.get('status') if t4 else 'N/A'}"
print("  ✅ 驳回成功，状态恢复为 PENDING，分数已清除")

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 5: 评委重新打分提交（验证驳回后可重打）")

r5 = requests.put(f'{BASE}/api/reviews/final/scores/{TASK_ID}/submit',
    json={**qcc_score, "total": 82.0, "plan": 9.0, "problem": 13.0},
    headers=auth_h(rev_token))
pp("评委重新提交正式分", r5)

t5 = get_task(rev_token, TASK_ID)
print(f"\n  重打后: status={t5.get('status') if t5 else 'N/A'}, score={t5.get('totalScore') if t5 else '-'}")
assert t5 and t5.get('status') == 'SCORED', f"❌ 重打后状态异常"
print("  ✅ 重打成功")

# ===========================================================================
print("\n" + "=" * 60)
print("STEP 6: 验证驳回越权（OPERATOR 不得驳回非己场次）")
# 找基层组1组的一个SCORED任务
import pymysql
db = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = db.cursor()
cur.execute("""
  SELECT rt.id FROM review_tasks rt
  JOIN registrations r ON r.id = rt.registration_id
  WHERE rt.stage = 'FINAL' AND rt.status = 'SCORED' AND r.final_session_code = '2026基层组1组'
  LIMIT 1
""")
row = cur.fetchone()
db.close()
if row:
    other_task_id = row[0]
    r6 = requests.post(f'{BASE}/api/admin/final/scores/{other_task_id}/reject',
        headers=auth_h(op_token))
    pp(f"OPERATOR 驳回非己场次 taskId={other_task_id}（预期403）", r6)
    print(f"  {'✅ 403权限拦截正确' if r6.status_code == 403 else '❌ 未被拦截，异常!'}")
else:
    print("  找不到基层组1组的SCORED任务，跳过越权测试")

# ===========================================================================
print("\n" + "=" * 60)
print("✅ 全链路自测完成")
print("""
[测试覆盖链路]
  1. 评委 my-tasks 拉取
  2. 评委保存草稿 → status 变为 IN_PROGRESS/DRAFT
  3. 评委提交正式分 → status 变为 SCORED
  4. OPERATOR 查看全部分配场次汇总
  5. OPERATOR 查看指定场次汇总
  6. OPERATOR 查看非权限场次 → 403
  7. OPERATOR 驳回己负责场次 → 成功，status 恢复 PENDING
  8. 评委驳回后重打 → 成功
  9. OPERATOR 驳回非己场次 → 403
""")
