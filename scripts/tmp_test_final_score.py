import requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = 'http://81.71.44.180:6039'

# 登录
r = requests.post(base + '/api/auth/login-with-password',
                  json={'phone': '13754322649', 'password': '589856'}, timeout=10)
token = r.json().get('data', {}).get('token')
headers = {'Authorization': 'Bearer ' + token}
print('登录:', '成功' if token else '失败')

# 找一个PENDING任务测试
tasks = requests.get(base + '/api/reviews/final/my-tasks', headers=headers, timeout=10).json().get('data', [])
pending = [t for t in tasks if t.get('status') == 'PENDING']
print(f'PENDING任务数: {len(pending)}')

if pending:
    t = pending[0]
    tid = t['taskId']
    print(f'\n=== 测试 taskId={tid} order={t["sessionOrder"]} ===')

    # 保存草稿，只传total
    r2 = requests.put(base + f'/api/reviews/final/scores/{tid}/draft',
                      headers=headers,
                      json={'scoreForm': 'QCC', 'total': 86}, timeout=10)
    print('草稿保存:', r2.status_code, r2.json().get('success'))

    # 重新拉取验证
    tasks2 = requests.get(base + '/api/reviews/final/my-tasks', headers=headers, timeout=10).json().get('data', [])
    t2 = next((x for x in tasks2 if x['taskId'] == tid), None)
    if t2:
        draft = t2.get('draftScore') or {}
        items = t2.get('scoreItems') or []
        print(f'status: {t2["status"]}')
        print(f'draftScore.total: {draft.get("total")}')
        print(f'分项: plan={draft.get("plan")} problem={draft.get("problem")} action={draft.get("action")}')
        print(f'      success={draft.get("success")} review={draft.get("review")} operation={draft.get("operation")} presentation={draft.get("presentation")}')
        for item in items:
            print(f'  {item["label"]:10s} 满分={item["maxScore"]:3d}  得分={item["score"]}')
