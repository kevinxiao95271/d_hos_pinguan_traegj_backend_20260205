import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

# 登录
login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = login['data']['token']
print('登录成功')

# 查评委列表
data = get(BASE + '/api/admin/reviews/reviewers', token)
reviewers = data.get('data', [])
print(f'评委总数: {len(reviewers)}')

# 查书审得分列表，找有分的任务
book = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=BOOK', token)
book_items = book.get('data', [])
print(f'\n书审已评项目数: {len(book_items)}')

# 找有书审分的评委
book_reviewer_ids = set()
book_reg_ids = set()
for item in book_items:
    book_reg_ids.add(item['registrationId'])
    for rs in item.get('reviewerScores', []):
        if rs.get('reviewerId'):
            book_reviewer_ids.add(rs['reviewerId'])

print(f'书审有打分的评委ID数: {len(book_reviewer_ids)}')

# 查面谈得分列表
interview = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', token)
int_items = interview.get('data', [])
print(f'面谈已评项目数: {len(int_items)}')

interview_reviewer_ids = set()
interview_reg_ids = set()
for item in int_items:
    interview_reg_ids.add(item['registrationId'])
    for rs in item.get('reviewerScores', []):
        if rs.get('reviewerId'):
            interview_reviewer_ids.add(rs['reviewerId'])

print(f'面谈有打分的评委ID数: {len(interview_reviewer_ids)}')

# 找同时有书审和面谈任务的评委
both_ids = book_reviewer_ids & interview_reviewer_ids
print(f'\n同时有书审+面谈任务的评委ID: {both_ids}')

# 列出这些评委的账号信息
print('\n=== 同时有书审+面谈得分的评委 ===')
for rv in reviewers:
    if rv['id'] in both_ids:
        print(f"  id={rv['id']}  {rv.get('name','?')}  phone={rv.get('phone','?')}")

# 找书审有分面谈无分的项目
only_book = book_reg_ids - interview_reg_ids
print(f'\n书审有分、面谈无分 的项目 (reg_ids): {list(only_book)[:10]}')
for item in book_items:
    if item['registrationId'] in only_book:
        rv_names = [rs.get('reviewerName','?') for rs in item.get('reviewerScores', [])]
        print(f"  reg_id={item['registrationId']}  {item.get('groupType')}  评委={rv_names}  avg={item.get('avgTotal')}")
        if len([x for x in book_items if x['registrationId'] in only_book]) > 5:
            break

# 找面谈有分书审无分的项目
only_interview = interview_reg_ids - book_reg_ids
print(f'\n面谈有分、书审无分 的项目 (reg_ids): {list(only_interview)[:10]}')
for item in int_items:
    if item['registrationId'] in only_interview:
        rv_names = [rs.get('reviewerName','?') for rs in item.get('reviewerScores', [])]
        print(f"  reg_id={item['registrationId']}  {item.get('groupType')}  评委={rv_names}  avg={item.get('avgTotal')}")

print('\n=== 推荐测试账号 ===')
shown = set()
# 优先展示书审+面谈都有分的评委
for rv in reviewers:
    if rv['id'] in both_ids and rv['id'] not in shown:
        print(f"  phone={rv.get('phone','?')}  姓名={rv.get('name','?')}  【书审+面谈都有任务】")
        shown.add(rv['id'])
        if len(shown) >= 3:
            break
# 补充只有书审的
for rv in reviewers:
    if rv['id'] in book_reviewer_ids and rv['id'] not in shown:
        print(f"  phone={rv.get('phone','?')}  姓名={rv.get('name','?')}  【仅书审有任务】")
        shown.add(rv['id'])
        if len(shown) >= 5:
            break
