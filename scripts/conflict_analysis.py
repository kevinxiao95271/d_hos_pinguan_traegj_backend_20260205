"""
书审分组冲突分析 v2
- 专家机构来源：生产库 专家数据含机构ID0410.csv（用姓名+手机匹配）
- 专家分组来源：书审专家单位(1)-0410.xlsx（忽略其中单位列）
- 项目分组来源：分组方案草稿.xlsx + 项目数据（含机构ID）
"""
import sys, os, csv, re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205'

# ────────────────────────────────────────────
# 1. 读生产库专家数据 → 建立 phone/name → institution_id 索引
# ────────────────────────────────────────────
phone2expert = {}   # 手机 → {institution_id, institution_name, name}
name2expert  = {}   # 姓名 → 同上（手机不可用时兜底）

with open(os.path.join(BASE, '专家数据含机构ID0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        phone = re.sub(r'\D', '', str(row['phone'] or ''))
        name  = str(row['name'] or '').strip()
        iid   = int(row['institution_id']) if row['institution_id'] else None
        iname = str(row['institution_name'] or '').strip()
        info  = {'institution_id': iid, 'institution_name': iname, 'name': name, 'phone': phone}
        if phone:
            phone2expert[phone] = info
        if name:
            name2expert[name] = info

print(f'生产库专家: {len(phone2expert)} 条(按手机), {len(name2expert)} 条(按姓名)')


def lookup_expert(name_raw, phone_raw):
    """用手机优先、姓名兜底从生产库查专家机构信息"""
    phone = re.sub(r'\D', '', str(phone_raw or ''))
    name  = str(name_raw or '').strip()
    if phone and phone in phone2expert:
        return phone2expert[phone]
    if name and name in name2expert:
        return name2expert[name]
    return None


# ────────────────────────────────────────────
# 2. 专家文件组号 → 项目分组代码映射
# ────────────────────────────────────────────
EXPERT_GROUP_MAP = {
    'A1': 'C1', 'A2': 'C2', 'A3': 'C3', 'A4': 'C4',
    **{f'B{i}': f'B{i}' for i in range(1, 23)},
    'C1': 'A1', 'C2': 'A2', 'C3': 'A3', 'C4': 'A4',
    'C5': 'A5', 'C6': 'A6', 'C7': 'A7',
}

# ────────────────────────────────────────────
# 3. 读专家分组文件，匹配生产库机构
# ────────────────────────────────────────────
wb_exp = openpyxl.load_workbook(
    os.path.join(BASE, '书审专家单位(1)-0410.xlsx'), read_only=True)
ws_exp = wb_exp['书审']

# proj_group → [expert info dict]
expert_groups = defaultdict(list)
unmatched = []

cur_expert_group = None
for i, row in enumerate(ws_exp.iter_rows(values_only=True)):
    if i < 2:
        continue
    group_raw  = row[0]
    name_raw   = row[3]
    phone_raw  = row[7]

    if group_raw:
        cur_expert_group = str(group_raw).strip()
    if not name_raw or not cur_expert_group:
        continue

    proj_group = EXPERT_GROUP_MAP.get(cur_expert_group)
    if proj_group is None:
        continue

    db_info = lookup_expert(name_raw, phone_raw)
    if db_info:
        expert_groups[proj_group].append({
            'expert_name':    db_info['name'],
            'phone':          db_info['phone'],
            'institution_id': db_info['institution_id'],
            'institution_name': db_info['institution_name'],
            'expert_group':   cur_expert_group,
        })
    else:
        # 未在生产库找到
        unmatched.append((cur_expert_group, str(name_raw).strip(),
                          str(phone_raw) if phone_raw else ''))
        expert_groups[proj_group].append({
            'expert_name':    str(name_raw).strip(),
            'phone':          str(phone_raw) if phone_raw else '',
            'institution_id': None,
            'institution_name': '【未匹配到生产库】',
            'expert_group':   cur_expert_group,
        })

wb_exp.close()

if unmatched:
    print(f'\n⚠️  以下专家未在生产库匹配（无法检查冲突）：')
    for eg, en, ep in unmatched:
        print(f'   {eg} | {en} | {ep}')

# ────────────────────────────────────────────
# 4. 读项目分组方案（institution_id 来自项目数据CSV）
# ────────────────────────────────────────────
reg2inst  = {}
reg2iname = {}
reg2pname = {}
with open(os.path.join(BASE, '项目数据（含机构ID+手法+主题0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        rid   = int(row['registration_id'])
        iid   = int(row['institution_id']) if row['institution_id'] else None
        iname = str(row['institution_name'] or '').strip()
        pname = str(row['project_name'] or '').strip()
        reg2inst[rid]  = iid
        reg2iname[rid] = iname
        reg2pname[rid] = pname

wb_grp = openpyxl.load_workbook(
    os.path.join(BASE, 'grouping_draft.xlsx'), read_only=True)
ws_grp = wb_grp['分组明细']

proj_groups = defaultdict(list)
col_names = None
for i, row in enumerate(ws_grp.iter_rows(values_only=True)):
    if i == 0:
        col_names = row
        continue
    if not row[0]:
        continue
    p = dict(zip(col_names, row))
    reg_id = int(p['项目编号']) if p['项目编号'] else None
    gcode  = p['建议分组']
    if not reg_id or not gcode:
        continue
    iid = reg2inst.get(reg_id)
    proj_groups[gcode].append({
        'registration_id': reg_id,
        'project_name':    reg2pname.get(reg_id, p.get('项目名称', '')),
        'institution_id':  iid,
        'institution_name': reg2iname.get(reg_id, p.get('机构名称', '')),
    })

wb_grp.close()

# ────────────────────────────────────────────
# 5. 冲突分析
# ────────────────────────────────────────────
all_groups = sorted(set(list(expert_groups.keys()) + list(proj_groups.keys())))
conflicts_all = []
summary = []

print('\n' + '='*70)
print('书审分组冲突分析报告（专家机构来自生产库）')
print('='*70)

for gcode in all_groups:
    experts = expert_groups.get(gcode, [])
    projs   = proj_groups.get(gcode, [])

    proj_inst_set = {p['institution_id'] for p in projs if p['institution_id']}

    group_conflicts = []
    for e in experts:
        eid = e['institution_id']
        if eid is None:
            continue
        if eid in proj_inst_set:
            clash = [p for p in projs if p['institution_id'] == eid]
            group_conflicts.append({**e, 'conflict_projects': clash})
            conflicts_all.append((gcode, e, clash))

    n_proj = len(projs)
    n_exp  = len(experts)
    n_conf = len(group_conflicts)
    summary.append((gcode, n_proj, n_exp, n_conf, group_conflicts))

    if group_conflicts:
        print(f'\n❌ {gcode} | 项目{n_proj}个 | 专家{n_exp}人 | 冲突{n_conf}处')
        for c in group_conflicts:
            print(f'   专家: {c["expert_name"]} ({c["institution_name"]}，id={c["institution_id"]})')
            for pp in c['conflict_projects']:
                print(f'      → {pp["registration_id"]} {pp["project_name"][:40]}')

total_conf = sum(r[3] for r in summary)
affected   = len([r for r in summary if r[3] > 0])
print(f'\n{"="*70}')
print(f'总计冲突：{total_conf} 处，涉及 {affected} 个小组')
print(f'未匹配专家：{len(unmatched)} 人（这些人的冲突未被检测）')
print('='*70)

# ────────────────────────────────────────────
# 6. 输出 Excel
# ────────────────────────────────────────────
out_path = os.path.join(BASE, 'conflict_report.xlsx')
wb_out = Workbook()
RED   = PatternFill(fill_type='solid', fgColor='FFCCCC')
GRN   = PatternFill(fill_type='solid', fgColor='E2EFDA')
YLW   = PatternFill(fill_type='solid', fgColor='FFEB9C')
HDR   = PatternFill(fill_type='solid', fgColor='1F4E79')
HDR_F = Font(bold=True, color='FFFFFF')
CTR   = Alignment(horizontal='center', vertical='center')

def set_header(ws, headers):
    ws.append(headers)
    for ci in range(1, len(headers)+1):
        c = ws.cell(1, ci)
        c.fill = HDR; c.font = HDR_F; c.alignment = CTR

# Sheet1: 冲突明细
ws1 = wb_out.active
ws1.title = '冲突明细'
set_header(ws1, ['小组','专家名','手机','专家机构(生产库)','institution_id','冲突项目编号','冲突项目名称','冲突机构'])
for gcode, e, cprojs in conflicts_all:
    for pp in cprojs:
        ws1.append([gcode, e['expert_name'], e['phone'],
                    e['institution_name'], e['institution_id'],
                    pp['registration_id'], pp['project_name'][:60],
                    pp['institution_name']])
        for ci in range(1, 9):
            ws1.cell(ws1.max_row, ci).fill = RED
for ci, w in enumerate([8,10,13,28,14,12,55,28],1):
    ws1.column_dimensions[ws1.cell(1,ci).column_letter].width = w

# Sheet2: 分组汇总
ws2 = wb_out.create_sheet('分组汇总')
set_header(ws2, ['小组','项目数','专家数','冲突数','状态'])
for gcode, n_proj, n_exp, n_conf, _ in summary:
    status = '❌ 有冲突' if n_conf > 0 else ('✅ 无冲突' if n_exp > 0 else '⚠️ 无专家')
    ws2.append([gcode, n_proj, n_exp, n_conf, status])
    fill = RED if n_conf > 0 else (GRN if n_exp > 0 else YLW)
    for ci in range(1, 6):
        ws2.cell(ws2.max_row, ci).fill = fill
for ci, w in enumerate([8,8,8,8,12],1):
    ws2.column_dimensions[ws2.cell(1,ci).column_letter].width = w

# Sheet3: 未匹配专家
ws3 = wb_out.create_sheet('未匹配专家')
set_header(ws3, ['专家组','项目组','专家名','手机（原始）','说明'])
for eg, en, ep in unmatched:
    pg = EXPERT_GROUP_MAP.get(eg, '?')
    ws3.append([eg, pg, en, ep, '未在生产库专家表找到对应记录'])
    for ci in range(1, 6):
        ws3.cell(ws3.max_row, ci).fill = YLW
for ci, w in enumerate([8,8,12,15,30],1):
    ws3.column_dimensions[ws3.cell(1,ci).column_letter].width = w

# Sheet4: 各组专家完整清单
ws4 = wb_out.create_sheet('专家分组清单')
set_header(ws4, ['专家组','项目组','专家名','手机','机构(生产库)','institution_id','匹配状态'])
for eg_code, experts in sorted(expert_groups.items(),
                                key=lambda x: EXPERT_GROUP_MAP.get(x[0], x[0])):
    for e in experts:
        status = '✅' if e['institution_id'] else '⚠️ 未匹配'
        ws4.append([e['expert_group'], eg_code,
                    e['expert_name'], e['phone'],
                    e['institution_name'], e['institution_id'], status])
        if not e['institution_id']:
            for ci in range(1, 8):
                ws4.cell(ws4.max_row, ci).fill = YLW
for ci, w in enumerate([8,8,12,13,30,14,10],1):
    ws4.column_dimensions[ws4.cell(1,ci).column_letter].width = w

wb_out.save(out_path)
print(f'\n✅ 报告已输出: {out_path}')
