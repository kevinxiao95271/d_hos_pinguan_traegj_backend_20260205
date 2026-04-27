"""
综合提取7条缺失activity_infos的报名表数据（DOCX XML + PDF）
输出：汇总结果 + SQL INSERT 语句
"""
import os, sys, re, zipfile, glob
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
import pdfplumber

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

# ── 字典映射 ─────────────────────────────────────────────────────────────────
SUBJECT_OPTIONS = [
    ('病人照护',          'patient_care'),
    ('病历质量',          'medical_record'),
    ('时间效率',          'time_efficiency'),
    ('成本效益',          'cost_benefit'),
    ('安全环境',          'safety_environment'),
    ('满意度',            'satisfaction'),
    ('教育训练',          'education_training'),
    ('医疗信息',          'medical_information'),
    ('医疗质量与安全',    'medical_quality_safety'),
    ('流程改造',          'process_improvement'),
    ('其他',              'other'),
]
METHOD_OPTIONS = [
    ('品管圈.*课题达成',  'qcc_topic_achievement'),
    ('品管圈.*问题解决',  'qcc_problem_solving'),
    ('品管圈',            'qcc_problem_solving'),   # fallback
    ('专案改善',          'project_improvement'),
    ('平衡计分卡',        'balanced_scorecard'),
    ('根本原因分析',      'root_cause_analysis'),
    ('失效模式',          'fmea'),
    ('标杆学习',          'benchmarking'),
    (r'\b5S\b',           'five_s'),
    (r'\bQFD\b',          'qfd'),
    ('品质报告卡',        'quality_report_card'),
    ('六西格玛',          'six_sigma'),
    ('循证医学',          'evidence_based'),
    ('FOCUS.PDCA',        'focus_pdca'),
    (r'(?<![A-Z])PDCA(?![A-Z\-])', 'pdca'),
    (r'\bTRM\b',          'trm'),
    ('精益A3|精益管理',   'lean_a3'),
    ('流程改造',          'process_reengineering'),
    ('其他',              'other'),
]
QUALITY_OPTIONS = [
    ('急性ST段',          'stemi'),
    ('急性脑梗死',        'stroke_thrombolysis'),
    ('肿瘤.*TNM|TNM.*肿瘤', 'tumor_tnm'),
    ('围手术期死亡',      'periop_mortality'),
    ('静脉血栓',          'vte_prevention'),
    ('感染性休克',        'septic_shock'),
    ('不良事件报告',      'adverse_event_report'),
    ('静脉输液',          'iv_fluids'),
    ('四级手术',          'grade4_surgery_mdt'),
    ('阴道分娩并发症',    'vaginal_delivery_complication'),
    ('非计划重返手术室',  'unplanned_return_to_or'),
    ('诊疗行为.*记录|记录.*诊疗', 'clinical_record_completeness'),
    ('检查检验.*互认',    'result_mutual_recognition'),
    ('其他',              'other'),
]
EXPERIENCE_OPTIONS = [
    ('预约诊疗',          'appointment_service'),
    ('门诊就诊流程',      'outpatient_process'),
    ('患者住院体验',      'inpatient_experience'),
    ('院后医疗服务',      'post_discharge_service'),
    ('院前院内衔接',      'pre_hospital_coordination'),
    ('舒心就医环境',      'comfortable_environment'),
    ('互联网诊疗',        'internet_medical'),
    ('其他',              'other'),
]


# ── 核心：从单元格文本中检测选中项 ──────────────────────────────────────────
def detect_selected(cell_text, options):
    """
    规则：
      1. ☑xxx  → 选中
      2. □xxx  → 未选
      3. xxx 前既无☑也无□ → 视为选中（部分填写人直接删了□）
    返回 (code, other_content)
    """
    # 先找☑
    for label, code in options:
        if re.search(r'☑\s*' + label, cell_text):
            other = _extract_other(cell_text) if code == 'other' else ''
            return code, other

    # 再找"无□前缀"的项目（把□xxx替换掉后还剩下的）
    stripped = re.sub(r'□[^\s□☑（()）\n]{1,15}', '', cell_text)
    stripped = stripped.replace('☑', '').replace('□', '')
    for label, code in options:
        if re.search(label, stripped):
            other = _extract_other(cell_text) if code == 'other' else ''
            return code, other
    return '', ''


def _extract_other(text):
    """提取 其他（请说明...）里的内容"""
    m = re.search(r'其他[（(]请说明[：:]?\s*([^）)\n]{1,80})', text)
    if m:
        v = m.group(1).strip('＿_＿ ')
        if v and not re.match(r'^[_＿\s]+$', v):
            return v
    # 有时写法是 其他（非相关主题）
    m2 = re.search(r'其他（([^）\n]{1,50})）', text)
    if m2:
        v = m2.group(1).strip()
        if v and v not in ('请说明', '非相关主题'):
            return v
    return ''


def detect_bool(cell_text, yes_kw='是', no_kw='否'):
    """检测是/否勾选"""
    if re.search(r'[☑✓√]\s*' + yes_kw, cell_text):
        return True
    if re.search(r'[☑✓√]\s*' + no_kw, cell_text):
        return False
    # 无☑前缀 fallback
    stripped = re.sub(r'□[是否]', '', cell_text)
    stripped = stripped.replace('☑', '').replace('□', '')
    if yes_kw in stripped and no_kw not in stripped:
        return True
    if no_kw in stripped and yes_kw not in stripped:
        return False
    return None


# ── 解析活动说明表格 ─────────────────────────────────────────────────────────
def parse_activity_from_text(full_text):
    """把整张活动说明的文本传入，返回字段字典"""
    r = {}

    def get_section(start_kw, end_kw=None):
        pat = start_kw + r'.*?\n(.*?)'
        if end_kw:
            pat += r'(?=' + end_kw + r')'
        else:
            pat += r'$'
        m = re.search(pat, full_text, re.S)
        return m.group(1) if m else ''

    # 主题类型
    chunk = get_section(r'主题类型', r'运用手法')
    r['subject_type_code'], r['subject_type_other'] = detect_selected(chunk, SUBJECT_OPTIONS)

    # 运用手法
    chunk = get_section(r'运用手法', r'数字化')
    r['method_code'], r['method_other'] = detect_selected(chunk, METHOD_OPTIONS)

    # 数字化/AI
    chunk = get_section(r'数字化.{0,20}', r'改善就医')
    r['related_to_digital_ai'] = detect_bool(chunk, '是', '否')
    if r['related_to_digital_ai'] is None:
        r['related_to_digital_ai'] = False  # 默认否

    # 改善就医感受
    chunk = get_section(r'改善就医感受', r'医疗质量安全')
    r['experience_improve_code'], r['experience_improve_other'] = detect_selected(chunk, EXPERIENCE_OPTIONS)

    # 医疗质量安全
    chunk = get_section(r'医疗质量安全\s*相关主题', r'本期活')
    r['quality_topic_code'], r['quality_topic_other'] = detect_selected(chunk, QUALITY_OPTIONS)

    # 跨部门
    m = re.search(r'跨部门\s*[|｜]?\s*(.*)', full_text)
    if m:
        r['cross_department'] = detect_bool(m.group(1), '是', '否')
    if r.get('cross_department') is None:
        r['cross_department'] = False

    return r


# ── DOCX 提取（结合 XML 分析） ───────────────────────────────────────────────
def extract_from_docx(filepath):
    """遍历所有表格，找到含活动说明的那张，返回解析结果"""
    doc = Document(filepath)
    for table in doc.tables:
        rows_text = []
        for row in table.rows:
            cells = []
            for cell in row.cells:
                cells.append(cell.text.strip())
            rows_text.append(' | '.join(cells))
        full = '\n'.join(rows_text)
        if '主题类型' in full and '运用手法' in full:
            return parse_activity_from_text(full)
    return None


# ── PDF 提取 ─────────────────────────────────────────────────────────────────
def extract_from_pdf(filepath):
    """用 pdfplumber 提取 PDF 文字，返回解析结果"""
    all_text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ''
            all_text.append(t)
    full = '\n'.join(all_text)
    if '主题类型' in full and '运用手法' in full:
        return parse_activity_from_text(full), full
    return None, full


# ── 每个注册ID处理逻辑 ───────────────────────────────────────────────────────
REG_LIST = [
    ('20260563', '宁波明州医院'),
    ('20260587', '杭州市临平区第一人民医院'),
    ('20260621', '浙江省台州医院'),
    ('20260632', '永康市妇幼保健院'),
    ('20260803', '宁波大学附属阳明医院'),
    ('20260889', '宁波明州医院'),
    ('20260893', '杭州市富阳区第三人民医院'),
]

results = {}
for reg_id, inst in REG_LIST:
    folder_list = [d for d in os.listdir(BASE) if d.startswith(reg_id)]
    if not folder_list:
        print(f'[{reg_id}] 文件夹不存在')
        continue
    folder = os.path.join(BASE, folder_list[0])
    files = os.listdir(folder)

    docx_files = [f for f in files if f.lower().endswith('.docx') and not f.startswith('~$')]
    pdf_files  = [f for f in files if f.lower().endswith('.pdf')]
    # 优先带"报名表"的 docx
    reg_docx = [f for f in docx_files if '报名表' in f]

    data = None
    source = ''

    # 1. 尝试报名表 DOCX
    for fn in (reg_docx + [f for f in docx_files if f not in reg_docx]):
        fp = os.path.join(folder, fn)
        try:
            data = extract_from_docx(fp)
            if data:
                source = f'DOCX:{fn}'
                break
        except Exception as e:
            pass

    # 2. 若 DOCX 未找到，尝试 PDF（优先带"报名表"的）
    if not data:
        reg_pdf = sorted(pdf_files, key=lambda f: (0 if '报名表' in f else 1, len(f)))
        for fn in reg_pdf:
            fp = os.path.join(folder, fn)
            try:
                data, raw = extract_from_pdf(fp)
                if data:
                    source = f'PDF:{fn}'
                    break
                # 打印PDF文字供参考
                print(f'\n[{reg_id}] PDF({fn}) 原始文字 (前2000字):\n{raw[:2000]}')
            except Exception as e:
                print(f'[{reg_id}] PDF读取失败 {fn}: {e}')

    results[reg_id] = (data, source)
    status = '✓' if data else '✗'
    print(f'[{status}] {reg_id} {inst}  来源: {source or "未找到"}')
    if data:
        for k, v in data.items():
            print(f'      {k}: {repr(v)}')

# ── 输出 SQL ─────────────────────────────────────────────────────────────────
print('\n\n' + '='*70)
print('-- INSERT SQL for activity_infos')
print('-- 注：registration_id 和 group_type 请根据实际情况确认')
print('='*70)

for reg_id, (data, source) in results.items():
    if not data:
        print(f'\n-- ⚠️  {reg_id} 无法提取，需手动补全')
        continue

    def q(v):
        if v is None:
            return 'NULL'
        if isinstance(v, bool):
            return '1' if v else '0'
        v = str(v).replace("'", "''")
        return f"'{v}'"

    subject_code  = data.get('subject_type_code', '') or ''
    subject_other = data.get('subject_type_other', '') or ''
    method_code   = data.get('method_code', '') or ''
    method_other  = data.get('method_other', '') or ''
    qt_code       = data.get('quality_topic_code', '') or ''
    qt_other      = data.get('quality_topic_other', '') or ''
    ei_code       = data.get('experience_improve_code', '') or ''
    ei_other      = data.get('experience_improve_other', '') or ''
    cross         = data.get('cross_department', False)
    digital       = data.get('related_to_digital_ai', False)

    print(f"""
-- {reg_id}  (来源: {source})
INSERT INTO activity_infos
  (registration_id, subject_type_code, subject_type_other,
   method_code, method_other,
   quality_topic_code, quality_topic_other,
   experience_improve_code, experience_improve_other,
   cross_department, related_to_digital_ai,
   created_at, updated_at)
VALUES
  ({reg_id}, {q(subject_code)}, {q(subject_other)},
   {q(method_code)}, {q(method_other)},
   {q(qt_code)}, {q(qt_other)},
   {q(ei_code)}, {q(ei_other)},
   {1 if cross else 0}, {1 if digital else 0},
   NOW(), NOW());""")
