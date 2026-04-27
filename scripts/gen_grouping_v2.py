"""
分组算法 v2：专家机构约束版
- 专家分组固定，每个小组的专家机构是禁止出现的 institution_id
- 项目在同一手法池内重新分配，优先放到没有该机构专家的小组
- 如果某项目在所有同类小组都有专家冲突（无解），单独标记出来
"""
import sys, os, csv, re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205'

# ────────────────────────────────────────────
# 1. 读生产库专家数据
# ────────────────────────────────────────────
phone2expert = {}
name2expert  = {}
with open(os.path.join(BASE, '专家数据含机构ID0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        phone = re.sub(r'\D', '', str(row['phone'] or ''))
        name  = str(row['name'] or '').strip()
        iid   = int(row['institution_id']) if row['institution_id'] else None
        info  = {'institution_id': iid, 'institution_name': str(row['institution_name'] or '').strip()}
        if phone: phone2expert[phone] = info
        if name:  name2expert[name]  = info

def lookup_inst(name_raw, phone_raw):
    phone = re.sub(r'\D', '', str(phone_raw or ''))
    name  = str(name_raw or '').strip()
    if phone and phone in phone2expert: return phone2expert[phone]
    if name  and name  in name2expert:  return name2expert[name]
    return None

# ────────────────────────────────────────────
# 2. 读专家分组文件，建立 project_group → forbidden_institution_ids
# ────────────────────────────────────────────
EXPERT_GROUP_MAP = {
    'A1': 'C1', 'A2': 'C2', 'A3': 'C3', 'A4': 'C4',
    **{f'B{i}': f'B{i}' for i in range(1, 23)},
    'C1': 'A1', 'C2': 'A2', 'C3': 'A3', 'C4': 'A4',
    'C5': 'A5', 'C6': 'A6', 'C7': 'A7',
}

# proj_group → set of forbidden institution_ids
forbidden = defaultdict(set)
expert_detail = defaultdict(list)  # proj_group → [(name, inst_id, inst_name)]

wb_exp = openpyxl.load_workbook(os.path.join(BASE, '书审专家单位(1)-0410.xlsx'), read_only=True)
ws_exp = wb_exp['书审']
cur_eg = None
for i, row in enumerate(ws_exp.iter_rows(values_only=True)):
    if i < 2: continue
    if row[0]: cur_eg = str(row[0]).strip()
    if not row[3] or not cur_eg: continue
    pg = EXPERT_GROUP_MAP.get(cur_eg)
    if not pg: continue
    info = lookup_inst(row[3], row[7])
    iid  = info['institution_id'] if info else None
    iname = info['institution_name'] if info else '【未匹配】'
    if iid: forbidden[pg].add(iid)
    expert_detail[pg].append({'name': str(row[3]).strip(), 'institution_id': iid, 'institution_name': iname})
wb_exp.close()

print(f'专家约束已加载，涉及 {len(forbidden)} 个小组')

# ────────────────────────────────────────────
# 3. 读项目数据（含 institution_id）
# ────────────────────────────────────────────
reg2info = {}  # registration_id → {institution_id, institution_name, project_name, ...}
with open(os.path.join(BASE, '项目数据（含机构ID+手法+主题0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        rid = int(row['registration_id'])
        reg2info[rid] = {
            'registration_id':   rid,
            'project_name':      row['project_name'].strip(),
            'group_type':        row['group_type'].strip(),
            'institution_id':    int(row['institution_id']) if row['institution_id'] else None,
            'institution_name':  row['institution_name'].strip(),
            'institution_level': row['institution_level'].strip(),
            'institution_city':  row['institution_city'].strip(),
            'method_code':       row['method_code'].strip(),
            'method_label':      row['method_label'].strip(),
            'quality_topic_code': row['quality_topic_code'].strip(),
            'quality_topic_label': row['quality_topic_label'].strip(),
        }

# ────────────────────────────────────────────
# 4. 读原始Excel（项目编号+竞赛组别+手法+十大安全目标）
# ────────────────────────────────────────────
files = os.listdir(BASE)
src_file = [f for f in files if '4.7' in f][0]
wb_src = openpyxl.load_workbook(os.path.join(BASE, src_file), read_only=True)
ws_src = wb_src['品管报名原始文档0407']

projects = []
for i, row in enumerate(ws_src.iter_rows(values_only=True)):
    if i == 0: continue
    seq = row[0]
    if seq is None: continue
    rid = row[1]
    if rid is None: continue
    rid = int(rid)
    db = reg2info.get(rid, {})
    p = {
        '序号':        seq,
        '项目编号':    rid,
        '竞赛组别':    str(row[2] or '').strip(),
        '项目名称':    row[3],
        '机构名称':    db.get('institution_name', str(row[6] or '').strip()),
        '机构等级':    db.get('institution_level', str(row[7] or '').strip()),
        '城市':        db.get('institution_city', str(row[8] or '').strip()),
        '主题类型':    str(row[15] or '').strip(),
        '运用手法':    str(row[16] or '').strip(),
        '十大安全目标': str(row[18] or '').strip(),
        'institution_id': db.get('institution_id'),
        '分组代码':    '',
        '冲突标记':    '',
    }
    projects.append(p)

wb_src.close()
print(f'读取项目: {len(projects)} 条')

# ────────────────────────────────────────────
# 5. 带约束的分配函数
# ────────────────────────────────────────────
def is_shi_da(p):
    v = p['十大安全目标']
    return v and v not in ('其他', '其他（非相关主题）', '')

def constrained_distribute(items, group_codes, target_sizes, forbidden_map):
    """
    将 items 分配到 group_codes 各组，满足：
    - 各组容量不超过 target_sizes（软约束，溢出时放宽）
    - project.institution_id 不能出现在 forbidden_map[group_code] 中
    返回 {序号: 分组代码}，以及无法满足约束的项目列表
    """
    n = len(group_codes)
    caps      = list(target_sizes)
    buckets   = [[] for _ in range(n)]
    result    = {}
    hard_conflicts = []  # 所有组都有冲突，无法规避

    # 按机构分组，机构内按序号排序
    by_inst = defaultdict(list)
    for item in items:
        by_inst[item['机构名称']].append(item)
    for v in by_inst.values():
        v.sort(key=lambda x: x['序号'])

    # 大机构优先处理
    sorted_insts = sorted(by_inst.keys(), key=lambda k: -len(by_inst[k]))

    for inst in sorted_insts:
        inst_items = by_inst[inst]
        iid = inst_items[0]['institution_id']

        for item in inst_items:
            # 可用组：没有专家冲突 AND 还有容量（优先）
            valid_with_cap = [i for i in range(n)
                              if iid not in forbidden_map.get(group_codes[i], set())
                              and caps[i] > 0]
            # 有容量但有冲突
            cap_only = [i for i in range(n) if caps[i] > 0]
            # 无约束兜底
            any_slot = list(range(n))

            # 按优先级尝试
            placed = False
            for candidates in [valid_with_cap, cap_only, any_slot]:
                if not candidates:
                    continue
                # 从当前最空的候选中选
                bi = max(candidates, key=lambda i: caps[i])
                buckets[bi].append(item)
                caps[bi] -= 1
                result[item['序号']] = group_codes[bi]
                if iid and iid in forbidden_map.get(group_codes[bi], set()):
                    hard_conflicts.append(item)
                placed = True
                break

            if not placed:
                hard_conflicts.append(item)

    return result, hard_conflicts

# ────────────────────────────────────────────
# 6. 分组执行
# ────────────────────────────────────────────
assignment = {}
all_hard_conflicts = []

# ── 进阶组 C ──
advanced = [p for p in projects if p['竞赛组别'] == '进阶组']
c_kc  = [p for p in advanced if '课题达成' in p['运用手法']]
c_qfd = [p for p in advanced if 'QFD' in p['运用手法']]
c_qs  = [p for p in advanced if '问题解决' in p['运用手法']]
c_fp  = [p for p in advanced if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']]
c_rest = [p for p in advanced if p['序号'] not in
          {x['序号'] for lst in [c_kc, c_qfd, c_qs, c_fp] for x in lst}]

# C1/C2 课题达成+QFD 带约束分配
c12_pool = c_kc + c_qfd
n = len(c12_pool)
sizes = [22, n - 22]  # C1≈22, C2=余下
r, hc = constrained_distribute(c12_pool, ['C1', 'C2'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# C3: 问题解决+FOCUS-PDCA（带约束，单组无法规避则标记）
c3_pool = c_qs + c_fp
r, hc = constrained_distribute(c3_pool, ['C3'], [len(c3_pool)], forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# C4: 其余（带约束，单组）
r, hc = constrained_distribute(c_rest, ['C4'], [len(c_rest)], forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

for p in advanced:
    if p['序号'] not in assignment: assignment[p['序号']] = 'C4'

# ── 综合组 B ──
comp = [p for p in projects if p['竞赛组别'] == '综合组']
shi_da_B = [p for p in comp if is_shi_da(p)]
non_sd_B = [p for p in comp if not is_shi_da(p)]

# B1-B3: 十大安全目标
sd_qs   = [p for p in shi_da_B if '问题解决' in p['运用手法']]
sd_pdca = [p for p in shi_da_B if 'PDCA' in p['运用手法']]
sd_other= [p for p in shi_da_B if p not in sd_qs and p not in sd_pdca]
for p in sd_qs:    assignment[p['序号']] = 'B1'
for p in sd_pdca:  assignment[p['序号']] = 'B3'
for p in sd_other: assignment[p['序号']] = 'B2'

# B4-B9: 问题解决（带约束）
b_qs = [p for p in non_sd_B if '问题解决' in p['运用手法']]
n = len(b_qs)
sizes = [n//6 + (1 if i < n%6 else 0) for i in range(6)]
r, hc = constrained_distribute(b_qs, ['B4','B5','B6','B7','B8','B9'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# B10-B13: 课题达成（带约束）
b_kc = [p for p in non_sd_B if '课题达成' in p['运用手法']]
n = len(b_kc)
sizes = [n//4 + (1 if i < n%4 else 0) for i in range(4)]
r, hc = constrained_distribute(b_kc, ['B10','B11','B12','B13'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# B14: QFD（单组，无法规避内部冲突，只能标记）
b_qfd = [p for p in non_sd_B if 'QFD' in p['运用手法']]
r, hc = constrained_distribute(b_qfd, ['B14'], [len(b_qfd)], forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# B15-B17: PDCA（带约束）
b_pdca = [p for p in non_sd_B if p['运用手法'] == 'PDCA']
n = len(b_pdca)
sizes = [n//3 + (1 if i < n%3 else 0) for i in range(3)]
r, hc = constrained_distribute(b_pdca, ['B15','B16','B17'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# B18-B19: FOCUS-PDCA（带约束）
b_fp = [p for p in non_sd_B if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']]
n = len(b_fp)
sizes = [n//2 + (1 if i < n%2 else 0) for i in range(2)]
r, hc = constrained_distribute(b_fp, ['B18','B19'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# B20/B21/B22
b_fmea = [p for p in non_sd_B if '失效模式' in p['运用手法']]
b_rca  = [p for p in non_sd_B if '根本原因' in p['运用手法'] or p['运用手法'] == '其他']
b_misc = [p for p in non_sd_B if p['序号'] not in
          {x['序号'] for lst in [b_qs,b_kc,b_qfd,b_pdca,b_fp,b_fmea,b_rca] for x in lst}]
for p in b_fmea: assignment[p['序号']] = 'B20'
for p in b_rca:  assignment[p['序号']] = 'B21'
for p in b_misc: assignment[p['序号']] = 'B22'
for p in comp:
    if p['序号'] not in assignment: assignment[p['序号']] = 'B22'

# ── 基层组 A ──
basic = [p for p in projects if p['竞赛组别'] == '基层组']
shi_da_A = [p for p in basic if is_shi_da(p)]
non_sd_A = [p for p in basic if not is_shi_da(p)]

# A1: 十大安全目标（带约束，但只有1组）
r, hc = constrained_distribute(shi_da_A, ['A1'], [len(shi_da_A)], forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

# A2/A3: 问题解决（带约束）
a_qs = [p for p in non_sd_A if '问题解决' in p['运用手法']]
n = len(a_qs)
sizes = [n//2 + (1 if i < n%2 else 0) for i in range(2)]
r, hc = constrained_distribute(a_qs, ['A2','A3'], sizes, forbidden)
assignment.update(r); all_hard_conflicts.extend(hc)

a_kc = [p for p in non_sd_A if '课题达成' in p['运用手法'] or 'QFD' in p['运用手法']]
a_pdca = [p for p in non_sd_A if p['运用手法'] == 'PDCA']
a_fp   = [p for p in non_sd_A if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']]
a_misc = [p for p in non_sd_A if p['序号'] not in
          {x['序号'] for lst in [a_qs,a_kc,a_pdca,a_fp] for x in lst}]
for p in a_kc:  assignment[p['序号']] = 'A4'
for p in a_pdca: assignment[p['序号']] = 'A5'
for p in a_fp:  assignment[p['序号']] = 'A6'
for p in a_misc: assignment[p['序号']] = 'A7'
for p in basic:
    if p['序号'] not in assignment: assignment[p['序号']] = 'A7'

# 写回
for p in projects:
    p['分组代码'] = assignment.get(p['序号'], '?')

# ────────────────────────────────────────────
# 7. 验证：重新检查冲突
# ────────────────────────────────────────────
remaining_conflicts = []
for p in projects:
    gcode = p['分组代码']
    iid   = p['institution_id']
    if iid and gcode and iid in forbidden.get(gcode, set()):
        remaining_conflicts.append(p)

print(f'\n{"="*60}')
print(f'优化后剩余冲突: {len(remaining_conflicts)} 个项目')
if remaining_conflicts:
    print('（这些是所有同类小组都有该机构专家，无法通过重分配解决的）')
    for p in remaining_conflicts:
        experts_in_group = [e for e in expert_detail.get(p['分组代码'], [])
                            if e['institution_id'] == p['institution_id']]
        exp_names = ', '.join(e['name'] for e in experts_in_group)
        print(f'  {p["分组代码"]} | {p["项目编号"]} | {p["机构名称"]} | 专家: {exp_names}')
else:
    print('✅ 所有冲突已通过重新分配消除！')
print('='*60)

# ────────────────────────────────────────────
# 8. 输出 Excel
# ────────────────────────────────────────────
out_path = os.path.join(BASE, 'grouping_v2.xlsx')
wb_out = Workbook()
RED  = PatternFill(fill_type='solid', fgColor='FFCCCC')
GRN  = PatternFill(fill_type='solid', fgColor='E2EFDA')
BLU  = PatternFill(fill_type='solid', fgColor='DDEBF7')
ORG  = PatternFill(fill_type='solid', fgColor='FCE4D6')
HDR  = PatternFill(fill_type='solid', fgColor='1F4E79')
HDR_F= Font(bold=True, color='FFFFFF')
CTR  = Alignment(horizontal='center', vertical='center')

# Sheet1: 分组明细
ws1 = wb_out.active; ws1.title = '分组明细'
headers = ['序号','项目编号','竞赛组别','建议分组','机构名称','机构等级','城市','运用手法','主题类型','十大安全目标','⚠️冲突','项目名称']
ws1.append(headers)
for ci in range(1, len(headers)+1):
    c = ws1.cell(1, ci); c.fill = HDR; c.font = HDR_F; c.alignment = CTR

conflict_ids = {p['序号'] for p in remaining_conflicts}
GROUP_FILL = {'A': GRN, 'B': BLU, 'C': ORG}

for p in sorted(projects, key=lambda x: (x['竞赛组别'], x['分组代码'], x['机构名称'])):
    flag = '⚠️冲突' if p['序号'] in conflict_ids else ''
    row = [p['序号'], p['项目编号'], p['竞赛组别'], p['分组代码'],
           p['机构名称'], p['机构等级'], p['城市'],
           p['运用手法'], p['主题类型'], p['十大安全目标'], flag, p['项目名称']]
    ws1.append(row)
    fill = RED if flag else GROUP_FILL.get(p['分组代码'][0] if p['分组代码'] else '', PatternFill())
    for ci in range(1, len(headers)+1):
        ws1.cell(ws1.max_row, ci).fill = fill

for ci, w in enumerate([6,12,8,8,28,8,8,16,14,28,8,50], 1):
    ws1.column_dimensions[ws1.cell(1,ci).column_letter].width = w

# Sheet2: 分组汇总（带冲突标记）
ws2 = wb_out.create_sheet('分组汇总')
ws2.append(['小组','项目数','专家数','禁忌机构数','剩余冲突','状态'])
for ci in range(1, 7):
    c = ws2.cell(1, ci); c.fill = HDR; c.font = HDR_F; c.alignment = CTR

all_gcodes = sorted(set(p['分组代码'] for p in projects))
for gcode in all_gcodes:
    n_proj = sum(1 for p in projects if p['分组代码'] == gcode)
    n_exp  = len(expert_detail.get(gcode, []))
    n_forb = len(forbidden.get(gcode, set()))
    n_conf = sum(1 for p in remaining_conflicts if p['分组代码'] == gcode)
    status = '❌ 仍有冲突' if n_conf > 0 else ('✅ 无冲突' if n_exp > 0 else '⚠️ 无专家')
    ws2.append([gcode, n_proj, n_exp, n_forb, n_conf, status])
    fill = RED if n_conf > 0 else (GRN if n_exp > 0 else PatternFill(fill_type='solid', fgColor='FFEB9C'))
    for ci in range(1, 7): ws2.cell(ws2.max_row, ci).fill = fill
for ci, w in enumerate([8,8,8,10,8,14], 1):
    ws2.column_dimensions[ws2.cell(1,ci).column_letter].width = w

wb_out.save(out_path)
print(f'\n✅ 输出: {out_path}')
