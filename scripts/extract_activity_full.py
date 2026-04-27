"""
完整提取 activity_infos 所有字段：
  theme, keywords, avg_work_years, avg_age,
  subject_type_code/other, method_code/other,
  quality_topic_code/other, experience_improve_code/other,
  cross_department, related_to_digital_ai
"""
import os, sys, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
import pdfplumber

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

# ── 字典（与 init_prod_dictionary_items.sql 一致）────────────────────────────
SUBJECT_OPTIONS = [
    ('病人照护',       'patient_care'),
    ('病历质量',       'case_quality'),
    ('时间效率',       'time_efficiency'),
    ('成本效益',       'cost_efficiency'),
    ('安全环境',       'safety_env'),
    ('满意度',         'satisfaction'),
    ('教育训练',       'education'),
    ('医疗信息',       'subject_type_8'),
    ('医疗质量与安全', 'quality_safety'),
    ('流程改造',       'process'),
    ('其他',           'other'),
]
METHOD_OPTIONS = [
    ('品管圈.*课题达成',  'qc_topic'),
    ('品管圈.*问题解决',  'method_1'),
    ('品管圈',            'method_1'),
    ('专案改善',          'method_3'),
    ('平衡计分卡',        'balanced_scorecard'),
    ('根本原因分析',      'method_5'),
    ('失效模式',          'method_6'),
    ('标杆学习',          'method_7'),
    (r'\b5S\b',           '5s'),
    (r'\bQFD\b',          'method_9'),
    ('品质报告卡',        'method_10'),
    ('六西格玛',          'method_11'),
    ('循证医学',          'ebm'),
    ('FOCUS.PDCA',        'focus_pdca'),
    (r'(?<![A-Z])PDCA(?![A-Z\-])', 'method_13'),
    (r'\bTRM\b',          'trm'),
    ('流程改造',          'method_15'),
    ('其他',              'other'),
]
QUALITY_OPTIONS = [
    ('急性ST段',                     'stemi'),
    ('急性脑梗死',                   'stroke_reperfusion'),
    ('TNM',                          'tumor_tnm_staging'),
    ('围手术期死亡',                 'perioperative_mortality'),
    ('静脉血栓',                     'vte_prevention'),
    ('感染性休克',                   'sepsis_bundle'),
    ('不良事件报告',                 'adverse_event_report'),
    ('静脉输液',                     'iv_infusion_standard'),
    ('四级手术',                     'level4_surgery_mdt'),
    ('阴道分娩并发症',               'vaginal_delivery_complication'),
    ('非计划重返手术室',             'unplanned_reoperation'),
    ('关键诊疗.*记录|记录.*诊疗',    'key_diagnosis_record'),
    ('检查检验.*互认',               'test_result_mutual_recognition'),
    ('其他',                         'other'),
]
EXPERIENCE_OPTIONS = [
    ('预约诊疗',        'appointment'),
    ('门诊就诊流程',    'outpatient_process'),
    ('患者住院体验',    'inpatient_comfort'),
    ('院后医疗服务',    'post_discharge'),
    ('院前院内衔接',    'pre_inpatient_connection'),
    ('舒心就医环境',    'environment'),
    ('互联网诊疗',      'internet_med'),
    ('其他',            'other'),
]


def detect_selected(cell_text, options):
    # 优先：找带 ☑/✓/√ 前缀的选项
    for label, code in options:
        if re.search(r'[☑✓√]\s*' + label, cell_text):
            other = _extract_other(cell_text) if code == 'other' else ''
            return code, other
    # 次选：选项出现在文本中，但 □ 不是紧接在它前面
    no_box_matches = []
    for label, code in options:
        if not re.search(label, cell_text):
            continue
        if not re.search(r'□\s*' + label, cell_text):
            no_box_matches.append((label, code))
    # 若超过 3 个选项都"没有□前缀"，说明模板里 □ 全部丢失，无法判断 → 返回空
    if len(no_box_matches) > 3:
        return '', ''
    if no_box_matches:
        _, code = no_box_matches[0]
        other = _extract_other(cell_text) if code == 'other' else ''
        return code, other
    return '', ''

def _extract_other(text):
    m = re.search(r'其他[（(]请说明[：:]?\s*([^）)\n]{1,100})', text)
    if m:
        v = m.group(1).strip('＿_ ')
        if v and not re.match(r'^[_＿\s]+$', v) and v != '请说明':
            return v
    return ''

def detect_bool(text, yes_kw='是', no_kw='否'):
    if re.search(r'[☑✓√]\s*' + yes_kw, text): return True
    if re.search(r'[☑✓√]\s*' + no_kw,  text): return False
    stripped = re.sub(r'□[是否]', '', text).replace('☑','').replace('□','')
    if yes_kw in stripped and no_kw not in stripped: return True
    if no_kw in stripped and yes_kw not in stripped: return False
    return None

def parse_int(text):
    m = re.search(r'(\d+)', text)
    return int(m.group(1)) if m else None


def parse_activity_table(table_text):
    """从活动说明表格文本里提取全部字段"""
    r = {}

    def section(start_kw, end_kw=None):
        pat = start_kw + r'[^\n]*\n(.*?)'
        pat += (r'(?=' + end_kw + r')') if end_kw else r'$'
        m = re.search(pat, table_text, re.S)
        return m.group(1) if m else ''

    def row_value(label_kw):
        """找 label_kw 所在行的值（表格用 | 分隔）"""
        m = re.search(label_kw + r'[^\|]*\|\s*([^\|\n]+)', table_text)
        return m.group(1).strip() if m else ''

    # 主题 & 关键词
    r['theme']    = row_value('活动主题')
    r['keywords'] = row_value('关键词')

    # 主题类型
    chunk = section(r'主题类型', r'运用手法')
    r['subject_type_code'], r['subject_type_other'] = detect_selected(chunk, SUBJECT_OPTIONS)

    # 运用手法
    chunk = section(r'运用手法', r'数字化')
    r['method_code'], r['method_other'] = detect_selected(chunk, METHOD_OPTIONS)

    # 数字化/AI
    chunk = section(r'数字化.{0,20}', r'改善就医')
    r['related_to_digital_ai'] = bool(re.search(r'[☑✓√]\s*是', chunk))

    # 改善就医感受
    chunk = section(r'改善就医感受', r'医疗质量安全')
    r['experience_improve_code'], r['experience_improve_other'] = detect_selected(chunk, EXPERIENCE_OPTIONS)

    # 医疗质量安全
    chunk = section(r'医疗质量安全\s*相关主题', r'本期活')
    r['quality_topic_code'], r['quality_topic_other'] = detect_selected(chunk, QUALITY_OPTIONS)

    # 平均工作年资 / 平均年龄（格式: "__ 10 ___年" 或 "10年"，有下划线）
    m = re.search(r'平均工作年资[^\|]*\|\s*[_＿\s]*(\d+)', table_text)
    r['avg_work_years'] = int(m.group(1)) if m else None
    m = re.search(r'平均年龄[^\|]*\|\s*[_＿\s]*(\d+)', table_text)
    r['avg_age'] = int(m.group(1)) if m else None

    # 跨部门（同行，格式: "跨部门 | □是  ☑否" 或 "跨部门 | ☑是  □否"）
    m = re.search(r'跨部门([^\n]+)', table_text)
    r['cross_department'] = detect_bool(m.group(1) if m else '', '是', '否')

    return r


def extract_from_docx(filepath):
    doc = Document(filepath)
    for table in doc.tables:
        rows = [' | '.join(c.text.strip() for c in row.cells) for row in table.rows]
        full = '\n'.join(rows)
        if '主题类型' in full and '运用手法' in full:
            return parse_activity_table(full)
    return None

def extract_from_pdf(filepath):
    with pdfplumber.open(filepath) as pdf:
        full = '\n'.join(p.extract_text() or '' for p in pdf.pages)
    if '主题类型' in full and '运用手法' in full:
        return parse_activity_table(full)
    return None


# ─────────────────────────────────────────────────────────────
REG_LIST = [
    '20260563', '20260587', '20260621',
    '20260632', '20260803', '20260889', '20260893',
]

all_data = {}
for reg_id in REG_LIST:
    folder_list = [d for d in os.listdir(BASE) if d.startswith(reg_id)]
    if not folder_list:
        all_data[reg_id] = None
        continue
    folder = os.path.join(BASE, folder_list[0])
    files  = os.listdir(folder)
    docx_files = sorted([f for f in files if f.endswith('.docx') and not f.startswith('~$')],
                        key=lambda x: (0 if '报名表' in x else 1, len(x)))
    pdf_files  = sorted([f for f in files if f.endswith('.pdf')],
                        key=lambda x: (0 if '报名表' in x else 1, len(x)))

    data = None
    for fn in docx_files:
        try:
            data = extract_from_docx(os.path.join(folder, fn))
            if data: break
        except: pass
    if not data:
        for fn in pdf_files:
            try:
                data = extract_from_pdf(os.path.join(folder, fn))
                if data: break
            except: pass

    all_data[reg_id] = data
    print(f'[{reg_id}] {"✓" if data else "✗"}')
    if data:
        for k, v in data.items():
            print(f'  {k}: {repr(v)}')
