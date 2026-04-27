"""
根据 2026浙江省医院品管大赛报名相关数据（4.7）(1).xlsx
生成初步分组方案，输出 Excel 供人工确认。

分组规则（来自"初步分组情况"Sheet）：
  进阶组 C：4组，按运用手法
  综合组 B：22组，先按十大安全目标分 B1-B3，再按手法分 B4-B22
  基层组 A：7组，先按十大安全目标分 A1，再按手法分 A2-A7

机构回避优化：
  同一机构的项目在同方法子分组内，尽量轮转分配到不同小组。
"""
import sys
import os
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205'
files = os.listdir(BASE)
src_file = [f for f in files if '4.7' in f][0]
src_path = os.path.join(BASE, src_file)

# ──────────────────────────────────────────────
# 1. 读取原始数据
# ──────────────────────────────────────────────
wb_src = openpyxl.load_workbook(src_path, read_only=True)
ws_src = wb_src['品管报名原始文档0407']

COL = {
    '序号': 1, '项目编号': 2, '竞赛组别': 3, '项目名称': 4,
    '申请人': 5, '联系方式': 6, '机构名称': 7, '机构等级': 8,
    '城市': 9, '活动主题': 10, '关键词': 11,
    '平均工作年限': 12, '平均年龄': 13, '跨部门': 14, '数字化AI': 15,
    '主题类型': 16, '运用手法': 17,
    '十大安全目标': 19, '改善就医感受': 21,
}

projects = []
for i, row in enumerate(ws_src.iter_rows(values_only=True)):
    if i == 0:
        continue  # 跳过表头
    seq = row[COL['序号'] - 1]
    if seq is None:
        continue
    p = {
        '序号':       row[COL['序号'] - 1],
        '项目编号':   row[COL['项目编号'] - 1],
        '竞赛组别':   str(row[COL['竞赛组别'] - 1] or '').strip(),
        '项目名称':   row[COL['项目名称'] - 1],
        '申请人':     row[COL['申请人'] - 1],
        '机构名称':   str(row[COL['机构名称'] - 1] or '').strip(),
        '机构等级':   row[COL['机构等级'] - 1],
        '城市':       row[COL['城市'] - 1],
        '主题类型':   str(row[COL['主题类型'] - 1] or '').strip(),
        '运用手法':   str(row[COL['运用手法'] - 1] or '').strip(),
        '十大安全目标': str(row[COL['十大安全目标'] - 1] or '').strip(),
        '分组代码':   '',
    }
    projects.append(p)

print(f'读取项目总数: {len(projects)}')
for gt in ['进阶组', '综合组', '基层组']:
    cnt = sum(1 for p in projects if p['竞赛组别'] == gt)
    print(f'  {gt}: {cnt}')

wb_src.close()


# ──────────────────────────────────────────────
# 2. 工具函数
# ──────────────────────────────────────────────
def is_shi_da(p):
    """判断是否十大安全目标项目（非"其他"且非空）"""
    v = p['十大安全目标']
    return v and v not in ('其他', '其他（非相关主题）', '')


def institution_spread(items, group_codes, target_sizes):
    """
    将 items 按机构轮转分配到各小组，减少同机构集中。
    group_codes: ['B4','B5',...,'B9']
    target_sizes: [27, 27, 27, 27, 27, 26]  每组目标大小
    返回 {项目序号: 分组代码}
    """
    n = len(group_codes)
    buckets = [[] for _ in range(n)]
    caps = list(target_sizes)

    # 按机构分组，机构内按序号排序
    by_inst = defaultdict(list)
    for item in items:
        by_inst[item['机构名称']].append(item)
    for v in by_inst.values():
        v.sort(key=lambda x: x['序号'])

    # 机构按项目数降序排，优先处理大机构
    sorted_insts = sorted(by_inst.keys(), key=lambda k: -len(by_inst[k]))

    result = {}
    # 为每个机构轮转分配，从项目最少的桶开始
    for inst in sorted_insts:
        inst_items = by_inst[inst]
        # 找当前最空的桶（按剩余容量降序）
        order = sorted(range(n), key=lambda i: -caps[i])
        for idx, item in enumerate(inst_items):
            # 找一个还有空余的桶，优先不同于上一次分配的
            placed = False
            for bi in order:
                if caps[bi] > 0:
                    buckets[bi].append(item)
                    caps[bi] -= 1
                    result[item['序号']] = group_codes[bi]
                    # 下次从下一个桶开始（轮转）
                    order = order[1:] + [order[0]]
                    placed = True
                    break
            if not placed:
                # 溢出处理：找任意有空的桶
                for bi in range(n):
                    if caps[bi] > 0:
                        buckets[bi].append(item)
                        caps[bi] -= 1
                        result[item['序号']] = group_codes[bi]
                        break

    return result


# ──────────────────────────────────────────────
# 3. 分组逻辑
# ──────────────────────────────────────────────
assignment = {}  # 序号 → 分组代码

# ── 进阶组 C（84项 → 4组）──
advanced = [p for p in projects if p['竞赛组别'] == '进阶组']
method_groups_C = {
    'C1': [p for p in advanced if '课题达成' in p['运用手法']],
    'C2_qfd': [p for p in advanced if 'QFD' in p['运用手法'] or 'qfd' in p['运用手法'].lower()],
    'C3_qs': [p for p in advanced if '问题解决' in p['运用手法']],
    'C3_fp': [p for p in advanced if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']],
    'C4': [p for p in advanced if p['运用手法'] not in ('',) and
           '课题达成' not in p['运用手法'] and
           'QFD' not in p['运用手法'] and
           '问题解决' not in p['运用手法'] and
           'FOCUS-PDCA' not in p['运用手法'] and
           'FOCUS_PDCA' not in p['运用手法']],
}

# C1: 课题达成前22个（按机构轮转取22）
c1_items = method_groups_C['C1']
c2_kc_items = []
if len(c1_items) > 22:
    # 先按机构轮转排序，确保C1/C2机构尽量分散
    by_inst_c1 = defaultdict(list)
    for p in c1_items:
        by_inst_c1[p['机构名称']].append(p)
    # 简单：先排序后前22给C1，余下给C2
    c1_sorted = sorted(c1_items, key=lambda x: x['序号'])
    c1_take = c1_sorted[:22]
    c2_kc_items = c1_sorted[22:]
else:
    c1_take = c1_items

for p in c1_take:
    assignment[p['序号']] = 'C1'
# C2 = 剩余课题达成 + QFD
c2_all = c2_kc_items + method_groups_C['C2_qfd']
for p in c2_all:
    assignment[p['序号']] = 'C2'
# C3 = 问题解决 + FOCUS-PDCA
for p in method_groups_C['C3_qs'] + method_groups_C['C3_fp']:
    assignment[p['序号']] = 'C3'
# C4 = 其余
for p in method_groups_C['C4']:
    assignment[p['序号']] = 'C4'
# 未分配的兜底 → C4
for p in advanced:
    if p['序号'] not in assignment:
        assignment[p['序号']] = 'C4'

# ── 综合组 B（555项 → 22组）──
comp = [p for p in projects if p['竞赛组别'] == '综合组']

# 十大安全目标 vs 非十大
shi_da_B = [p for p in comp if is_shi_da(p)]
non_sd_B = [p for p in comp if not is_shi_da(p)]

print(f'\n综合组 十大安全目标: {len(shi_da_B)}, 非十大: {len(non_sd_B)}')

# B1-B3: 十大安全目标，按手法再分3组
sd_qs = [p for p in shi_da_B if '问题解决' in p['运用手法']]
sd_pdca = [p for p in shi_da_B if 'PDCA' in p['运用手法']]  # PDCA + FOCUS-PDCA
sd_other = [p for p in shi_da_B if p not in sd_qs and p not in sd_pdca]

# B1: 问题解决，B3: PDCA/FOCUS-PDCA，B2: 其他
for p in sd_qs:
    assignment[p['序号']] = 'B1'
for p in sd_pdca:
    assignment[p['序号']] = 'B3'
for p in sd_other:
    assignment[p['序号']] = 'B2'

# 非十大，按手法分
b_qs = [p for p in non_sd_B if '问题解决' in p['运用手法']]   # 161项 → B4-B9
b_kc = [p for p in non_sd_B if '课题达成' in p['运用手法']]   # 104项 → B10-B13
b_qfd = [p for p in non_sd_B if 'QFD' in p['运用手法']]       # 26项 → B14
b_pdca = [p for p in non_sd_B if p['运用手法'] == 'PDCA']     # 72项 → B15-B17
b_fp = [p for p in non_sd_B if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']]  # 47项 → B18-B19
b_fmea = [p for p in non_sd_B if '失效模式' in p['运用手法']] # 29项 → B20
b_rca = [p for p in non_sd_B if '根本原因' in p['运用手法'] or p['运用手法'] == '其他']  # 18项 → B21
b_misc = [p for p in non_sd_B if p['序号'] not in
          {x['序号'] for lst in [b_qs, b_kc, b_qfd, b_pdca, b_fp, b_fmea, b_rca] for x in lst}]  # B22

print(f'  问题解决: {len(b_qs)}, 课题达成: {len(b_kc)}, QFD: {len(b_qfd)}')
print(f'  PDCA: {len(b_pdca)}, FOCUS-PDCA: {len(b_fp)}, 失效模式: {len(b_fmea)}')
print(f'  根本原因+其他: {len(b_rca)}, 综合工具: {len(b_misc)}')

# B4-B9 (6组, 问题解决161项): 机构轮转
n_qs = len(b_qs)
sizes_B4_9 = [n_qs // 6 + (1 if i < n_qs % 6 else 0) for i in range(6)]
r = institution_spread(b_qs, ['B4', 'B5', 'B6', 'B7', 'B8', 'B9'], sizes_B4_9)
assignment.update(r)

# B10-B13 (4组, 课题达成104项)
n_kc = len(b_kc)
sizes_B10_13 = [n_kc // 4 + (1 if i < n_kc % 4 else 0) for i in range(4)]
r = institution_spread(b_kc, ['B10', 'B11', 'B12', 'B13'], sizes_B10_13)
assignment.update(r)

# B14 QFD (全部一组)
for p in b_qfd:
    assignment[p['序号']] = 'B14'

# B15-B17 (3组, PDCA72项)
n_pd = len(b_pdca)
sizes_B15_17 = [n_pd // 3 + (1 if i < n_pd % 3 else 0) for i in range(3)]
r = institution_spread(b_pdca, ['B15', 'B16', 'B17'], sizes_B15_17)
assignment.update(r)

# B18-B19 (2组, FOCUS-PDCA47项)
n_fp = len(b_fp)
sizes_B18_19 = [n_fp // 2 + (1 if i < n_fp % 2 else 0) for i in range(2)]
r = institution_spread(b_fp, ['B18', 'B19'], sizes_B18_19)
assignment.update(r)

for p in b_fmea:
    assignment[p['序号']] = 'B20'
for p in b_rca:
    assignment[p['序号']] = 'B21'
for p in b_misc:
    assignment[p['序号']] = 'B22'

# 兜底
for p in comp:
    if p['序号'] not in assignment:
        assignment[p['序号']] = 'B22'

# ── 基层组 A（194项 → 7组）──
basic = [p for p in projects if p['竞赛组别'] == '基层组']

shi_da_A = [p for p in basic if is_shi_da(p)]
non_sd_A = [p for p in basic if not is_shi_da(p)]

print(f'\n基层组 十大安全目标: {len(shi_da_A)}, 非十大: {len(non_sd_A)}')

for p in shi_da_A:
    assignment[p['序号']] = 'A1'

a_qs = [p for p in non_sd_A if '问题解决' in p['运用手法']]   # → A2/A3
a_kc = [p for p in non_sd_A if '课题达成' in p['运用手法'] or 'QFD' in p['运用手法']]  # → A4
a_pdca = [p for p in non_sd_A if p['运用手法'] == 'PDCA']     # → A5
a_fp = [p for p in non_sd_A if 'FOCUS-PDCA' in p['运用手法'] or 'FOCUS_PDCA' in p['运用手法']]  # → A6
a_misc = [p for p in non_sd_A if p['序号'] not in
          {x['序号'] for lst in [a_qs, a_kc, a_pdca, a_fp] for x in lst}]  # → A7

print(f'  问题解决: {len(a_qs)}, 课题达成+QFD: {len(a_kc)}, PDCA: {len(a_pdca)}, FOCUS-PDCA: {len(a_fp)}, 其他: {len(a_misc)}')

# A2-A3 (2组)
n_aqs = len(a_qs)
sizes_A2_3 = [n_aqs // 2 + (1 if i < n_aqs % 2 else 0) for i in range(2)]
r = institution_spread(a_qs, ['A2', 'A3'], sizes_A2_3)
assignment.update(r)

for p in a_kc:
    assignment[p['序号']] = 'A4'
for p in a_pdca:
    assignment[p['序号']] = 'A5'
for p in a_fp:
    assignment[p['序号']] = 'A6'
for p in a_misc:
    assignment[p['序号']] = 'A7'

for p in basic:
    if p['序号'] not in assignment:
        assignment[p['序号']] = 'A7'

# 写回
for p in projects:
    p['分组代码'] = assignment.get(p['序号'], '?')


# ──────────────────────────────────────────────
# 4. 输出 Excel
# ──────────────────────────────────────────────
out_path = os.path.join(BASE, 'grouping_draft.xlsx')
wb_out = Workbook()

# ── Sheet1: 分组明细 ──
ws1 = wb_out.active
ws1.title = '分组明细'
headers = ['序号', '项目编号', '竞赛组别', '建议分组', '机构名称', '机构等级', '城市', '运用手法', '主题类型', '十大安全目标', '项目名称']
ws1.append(headers)
ws1.row_dimensions[1].height = 20

header_fill = PatternFill(fill_type='solid', fgColor='1F4E79')
header_font = Font(bold=True, color='FFFFFF')
for col_idx, _ in enumerate(headers, 1):
    cell = ws1.cell(row=1, column=col_idx)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

# 分组颜色
GROUP_COLOR = {
    'A': 'E2EFDA', 'B': 'DDEBF7', 'C': 'FCE4D6'
}

for p in sorted(projects, key=lambda x: (x['竞赛组别'], x['分组代码'], x['机构名称'])):
    row = [
        p['序号'], p['项目编号'], p['竞赛组别'], p['分组代码'],
        p['机构名称'], p['机构等级'], p['城市'],
        p['运用手法'], p['主题类型'], p['十大安全目标'], p['项目名称']
    ]
    ws1.append(row)
    prefix = p['分组代码'][0] if p['分组代码'] else ''
    color = GROUP_COLOR.get(prefix, 'FFFFFF')
    fill = PatternFill(fill_type='solid', fgColor=color)
    for col_idx in range(1, len(headers) + 1):
        ws1.cell(row=ws1.max_row, column=col_idx).fill = fill

# 列宽
col_widths = [6, 12, 8, 8, 28, 8, 8, 16, 14, 30, 50]
for i, w in enumerate(col_widths, 1):
    ws1.column_dimensions[ws1.cell(row=1, column=i).column_letter].width = w

# ── Sheet2: 各组机构分布（冲突风险）──
ws2 = wb_out.create_sheet('机构分布（回避检查）')
ws2.append(['分组代码', '机构名称', '项目数', '⚠️风险'])
ws2.row_dimensions[1].height = 20
for col_idx in range(1, 5):
    c = ws2.cell(row=1, column=col_idx)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal='center')

# 统计每个分组内各机构项目数
group_inst = defaultdict(lambda: defaultdict(int))
for p in projects:
    group_inst[p['分组代码']][p['机构名称']] += 1

for gcode in sorted(group_inst.keys()):
    inst_dict = group_inst[gcode]
    for inst, cnt in sorted(inst_dict.items(), key=lambda x: -x[1]):
        risk = '⚠️ 同机构≥3' if cnt >= 3 else ('注意 同机构≥2' if cnt >= 2 else '')
        ws2.append([gcode, inst, cnt, risk])
        if cnt >= 3:
            row_idx = ws2.max_row
            for col_idx in range(1, 5):
                ws2.cell(row=row_idx, column=col_idx).fill = PatternFill(fill_type='solid', fgColor='FFCCCC')

ws2.column_dimensions['A'].width = 10
ws2.column_dimensions['B'].width = 30
ws2.column_dimensions['C'].width = 8
ws2.column_dimensions['D'].width = 16

# ── Sheet3: 分组汇总 ──
ws3 = wb_out.create_sheet('分组汇总')
ws3.append(['分组代码', '项目数', '机构数', '最大同机构数'])
ws3.row_dimensions[1].height = 20
for col_idx in range(1, 5):
    c = ws3.cell(row=1, column=col_idx)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal='center')

for gcode in sorted(group_inst.keys()):
    inst_dict = group_inst[gcode]
    total = sum(inst_dict.values())
    num_inst = len(inst_dict)
    max_same = max(inst_dict.values())
    ws3.append([gcode, total, num_inst, max_same])
    if max_same >= 3:
        for col_idx in range(1, 5):
            ws3.cell(row=ws3.max_row, column=col_idx).fill = PatternFill(fill_type='solid', fgColor='FFCCCC')

ws3.column_dimensions['A'].width = 10
ws3.column_dimensions['B'].width = 8
ws3.column_dimensions['C'].width = 8
ws3.column_dimensions['D'].width = 14

wb_out.save(out_path)
print(f'\n✅ 输出文件: {out_path}')

# 打印分组统计
print('\n=== 分组结果统计 ===')
from collections import Counter
cnt_by_group = Counter(p['分组代码'] for p in projects)
for code in sorted(cnt_by_group.keys()):
    print(f'  {code}: {cnt_by_group[code]} 项')

# 冲突风险汇总
print('\n=== 机构回避风险（同组≥3个项目的机构）===')
risk_found = False
for gcode in sorted(group_inst.keys()):
    for inst, cnt in group_inst[gcode].items():
        if cnt >= 3:
            print(f'  ⚠️  {gcode} | {inst} | {cnt}项')
            risk_found = True
if not risk_found:
    print('  无高风险（无同机构≥3项）')

print('\n=== 注意（同组≥2个项目的机构）===')
warn_found = False
for gcode in sorted(group_inst.keys()):
    for inst, cnt in group_inst[gcode].items():
        if cnt == 2:
            print(f'  注意  {gcode} | {inst} | {cnt}项')
            warn_found = True
if not warn_found:
    print('  无')
