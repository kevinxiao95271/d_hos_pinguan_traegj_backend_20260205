import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\update_final_sessions_0527.sql'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 每条UPDATE单独处理
entries = []
for block in re.findall(r'UPDATE registrations SET .+? WHERE id=\d+;', content, re.DOTALL):
    id_m = re.search(r'WHERE id=(\d+)', block)
    sess_m = re.search(r"final_session_code='([^']+)'", block)
    order_m = re.search(r'final_session_order=(\d+)', block)
    if id_m and sess_m:
        entries.append((int(id_m.group(1)), sess_m.group(1), int(order_m.group(1)) if order_m else 0))

s1 = [(rid, sess, order) for rid, sess, order in entries if '十大安全目标专场1' in sess]
s1.sort(key=lambda x: x[2])
print(f'十大安全目标专场1 共 {len(s1)} 条:')
for rid, sess, order in s1:
    print(f'  order={order}  id={rid}')

# 查 20260321
match = [(rid, sess, order) for rid, sess, order in entries if rid == 20260321]
print(f'\nid=20260321: {match}')
