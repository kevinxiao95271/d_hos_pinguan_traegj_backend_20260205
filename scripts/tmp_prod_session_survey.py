"""
只读摸排：通过 registrations 接口获取生产专场码 × groupType 分布
ranking 接口因旧 JAR NPE 不可用，改用 admin/registrations/filter
"""
import requests
from collections import defaultdict

BASE  = "http://zkjb.zjmss.org.cn/api"
PHONE = "13800010001"
PWD   = "ops2026"
COMP_ID = 1

sess = requests.Session()
sess.headers["Content-Type"] = "application/json"

# 登录
r = sess.post(f"{BASE}/auth/login-with-password",
              json={"phone": PHONE, "password": PWD}, timeout=10)
token = (r.json().get("data") or {}).get("token")
if not token:
    print(f"[ERROR] 登录失败: {r.json()}")
    exit(1)
sess.headers["Authorization"] = f"Bearer {token}"
print("登录成功\n")

# ── 分页拉取所有已提交报名（拿 final_session_code + group_type） ───────────
all_regs = []
page = 1
while True:
    r2 = sess.get(f"{BASE}/admin/registrations/filter",
                  params={"competitionId": COMP_ID, "status": "SUBMITTED",
                          "page": page, "size": 100},
                  timeout=15)
    body = r2.json()
    if not body.get("success"):
        print(f"[ERROR] {body.get('message')}")
        break
    data = body.get("data", {})
    records = data.get("content") or data.get("records") or data if isinstance(data, list) else []
    if not records:
        break
    all_regs.extend(records)
    total_pages = data.get("totalPages") or 1
    print(f"  拉取第 {page}/{total_pages} 页，本页 {len(records)} 条")
    if page >= total_pages:
        break
    page += 1

print(f"\n共拉取 {len(all_regs)} 条报名记录\n")

# ── 统计 ──────────────────────────────────────────────────────────────────
session_groups  = defaultdict(lambda: defaultdict(int))
session_has_adv = {}

for reg in all_regs:
    sc = reg.get("finalSessionCode") or reg.get("final_session_code") or "(无专场)"
    gt = reg.get("groupType") or reg.get("group_type") or "null"
    session_groups[sc][gt] += 1
    if sc not in session_has_adv:
        session_has_adv[sc] = "进阶" in sc

print("=" * 68)
print("专场码 × groupType 分布")
print("=" * 68)
mixed = []
for sc in sorted(session_groups.keys()):
    gts = session_groups[sc]
    code_adv = session_has_adv[sc]
    types_in = set(gts.keys())
    is_mixed = "ADVANCED" in types_in and bool(types_in - {"ADVANCED", "null"})
    flag = "  <<<< 混合！" if is_mixed else ""
    print(f"\n  [{sc}]  码含'进阶'={code_adv}{flag}")
    for gt, cnt in sorted(gts.items()):
        print(f"         {gt:20s}: {cnt} 条")
    if is_mixed:
        mixed.append(sc)

# ── 一致性分析 ────────────────────────────────────────────────────────────
print("\n" + "=" * 68)
print("奖项逻辑一致性分析")
print("=" * 68)
inconsistent = []
for sc, gts in session_groups.items():
    code_adv = session_has_adv[sc]
    actual_types = set(gts.keys()) - {"null"}
    if not actual_types:
        continue
    actual_adv = "ADVANCED" in actual_types and len(actual_types) == 1
    if code_adv != actual_adv:
        inconsistent.append((sc, code_adv, actual_adv, dict(gts)))

if not inconsistent:
    print("\n  [OK] 专场码含'进阶' 与 groupType=ADVANCED 完全对应，无偏差")
else:
    print(f"\n  [!!] {len(inconsistent)} 个专场存在偏差：")
    for sc, ca, aa, gts in inconsistent:
        print(f"    {sc}: 码含进阶={ca}, 实际={gts}")

if not mixed:
    print("  [OK] 无混合专场，每个专场组别纯一")
else:
    print(f"  [!!] {len(mixed)} 个混合专场（进阶+非进阶同场）：")
    for sc in mixed:
        print(f"    {sc}")

print("\n完成（只读）")
