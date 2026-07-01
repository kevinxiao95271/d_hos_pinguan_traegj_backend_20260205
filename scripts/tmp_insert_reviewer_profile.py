#!/usr/bin/env python3
import io, sys, pymysql, json, requests
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = 'http://81.71.44.180:6039'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
          password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
c = pymysql.connect(**DB); cur = c.cursor()
now = datetime.now()

# 郭佳奕 user_id=67 插入扩展信息
cur.execute('DELETE FROM reviewer_profiles WHERE user_id=67')
cur.execute(
    'INSERT INTO reviewer_profiles '
    '(user_id, gender, job_position, department, id_number, id_number_masked, '
    'bank_name, bank_card_no, bank_card_no_masked, '
    'backgrounds_json, tools_json, topics_json, experience_json, created_at, updated_at) '
    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
    (67, '女', '副主任护师', '护理部', '330101199001011234', '330101****01011234',
     '工商银行', '6222021234567890', '6222****7890',
     '["品管圈","PDCA"]', '["鱼骨图","柏拉图"]', '["护理质量","患者安全"]',
     '["主持过QCC项目"]', now, now)
)
c.commit()
print('郭佳奕扩展信息已插入')
cur.close(); c.close()

# ── API 测试 ─────────────────────────────────────────────────
def login(phone):
    r = requests.post(BASE+'/api/auth/login-with-password',
                      json={'phone': phone, 'password': 'user123'}, timeout=10)
    d = r.json()
    return d['data']['token'] if d.get('success') else None

print('\n' + '='*60)
print('案例 A — 有扩展信息（郭佳奕，phone=9002）')
print('='*60)
tok_a = login('9002')
if tok_a:
    r = requests.get(BASE+'/api/reviewers/me/profile',
                     headers={'Authorization': 'Bearer ' + tok_a}, timeout=10)
    print(f'GET /api/reviewers/me/profile  HTTP {r.status_code}')
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
else:
    print('登录失败')

print('\n' + '='*60)
print('案例 B — 无扩展信息（张春梅，phone=15957716111）')
print('='*60)
tok_b = login('15957716111')
if tok_b:
    r2 = requests.get(BASE+'/api/reviewers/me/profile',
                      headers={'Authorization': 'Bearer ' + tok_b}, timeout=10)
    print(f'GET /api/reviewers/me/profile  HTTP {r2.status_code}')
    print(json.dumps(r2.json(), ensure_ascii=False, indent=2))
else:
    print('登录失败')
