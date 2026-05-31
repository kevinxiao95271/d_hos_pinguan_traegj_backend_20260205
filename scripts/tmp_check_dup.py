import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\update_final_sessions_0527.sql'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 提取所有 WHERE id=XXXXXX
ids = re.findall(r'WHERE id=(\d+)', content)
from collections import Counter
cnt = Counter(ids)
dups = {k: v for k, v in cnt.items() if v > 1}
if dups:
    print(f"重复出现的 id（共{len(dups)}个）：")
    for rid, times in sorted(dups.items()):
        # 找出对应的场次
        lines = [l.strip() for l in content.splitlines() if f'WHERE id={rid}' in l]
        sessions = [re.search(r"final_session_code='([^']+)'", l) for l in lines]
        sess_names = [s.group(1) if s else '?' for s in sessions]
        print(f"  id={rid}  出现{times}次:")
        for sn in sess_names:
            print(f"    → {sn}")
else:
    print("无重复 id")
print(f"\n总计 {len(ids)} 条，唯一 {len(set(ids))} 个")
