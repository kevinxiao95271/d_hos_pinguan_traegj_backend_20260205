"""
从7error文件夹中的DOCX/PDF提取activity_infos所需字段，生成SQL INSERT。

需要的字段：
  subject_type_code / subject_type_other
  method_code / method_other
  quality_topic_code / quality_topic_other
  experience_improve_code / experience_improve_other
  cross_department (bool)
  related_to_digital_ai (bool)
"""
import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

# ---- 已知的字典映射（从API返回值推断）----
# 主题类型
SUBJECT_MAP = {
    '病人照护':    'patient_care',
    '病历质量':    'medical_record',
    '时间效率':    'time_efficiency',
    '成本效益':    'cost_benefit',
    '安全环境':    'safety_environment',
    '满意度':      'satisfaction',
    '教育训练':    'education_training',
    '医疗信息':    'medical_information',
    '医疗质量与安全': 'medical_quality_safety',
    '流程改造':    'process_improvement',
    '其他':        'other',
}
# 运用手法
METHOD_MAP = {
    '品管圈.*问题解决': 'qcc_problem_solving',
    '品管圈.*课题达成': 'qcc_topic_achievement',
    '专案改善':          'project_improvement',
    '平衡计分卡':        'balanced_scorecard',
    '根本原因分析':      'root_cause_analysis',
    '失效模式与效应分析': 'fmea',
    '标杆学习':          'benchmarking',
    r'\b5S\b':           'five_s',
    r'\bQFD\b':          'qfd',
    '品质报告卡':        'quality_report_card',
    '六西格玛':          'six_sigma',
    '循证医学':          'evidence_based',
    r'(?<![A-Z\-])PDCA(?![\-A-Z])': 'pdca',
    'FOCUS-PDCA':        'focus_pdca',
    r'\bTRM\b':          'trm',
    '流程改造':          'process_reengineering',
    '其他':              'other',
}
# 医疗质量安全主题（国家十大目标）
QUALITY_MAP = {
    '急性ST段':          'stemi',
    '急性脑梗死':        'stroke_thrombolysis',
    '肿瘤.*TNM':         'tumor_tnm',
    '围手术期死亡':      'periop_mortality',
    '静脉血栓':          'vte_prevention',
    '感染性休克':        'septic_shock',
    '不良事件报告':      'adverse_event_report',
    '静脉输液':          'iv_fluids',
    '四级手术.*多学科':  'grade4_surgery_mdt',
    '阴道分娩并发症':    'vaginal_delivery_complication',
    '非计划重返手术室':  'unplanned_return_to_or',
    '诊疗行为.*记录':    'clinical_record_completeness',
    '检查检验.*互认':    'result_mutual_recognition',
    '其他':              'other',
}
# 改善就医感受
EXPERIENCE_MAP = {
    '预约诊疗':          'appointment_service',
    '门诊就诊流程':      'outpatient_process',
    '患者住院体验':      'inpatient_experience',
    '院后医疗服务':      'post_discharge_service',
    '院前院内衔接':      'pre_hospital_coordination',
    '舒心就医环境':      'comfortable_environment',
    '互联网诊疗':        'internet_medical',
    '其他':              'other',
}


def find_checked(text, option_map):
    """在文本里找到被选中（☑或无□前缀）的选项，返回(code, other_text)"""
    # 方法1：找☑
    checked_labels = re.findall(r'☑\s*([^\s□☑\n]+(?:\s*[^\s□☑\n]+)*?)(?=\s*(?:□|☑|$|\n))', text)
    # 方法2：在连续"□选项"序列中找没有□前缀的选项（但需剔除标题）
    # 用方法1优先
    if checked_labels:
        label_str = ' '.join(checked_labels)
        for pattern, code in option_map.items():
            if re.search(pattern, label_str):
                return code, label_str
    # fallback：找到没有□前缀的词
    # 把所有"□xxx"替换掉，剩下的就是选中项
    cleaned = re.sub(r'□[^\s□☑（）\n]*', '', text)
    cleaned = re.sub(r'☑', '', cleaned)
    # 再用已知模式匹配
    for pattern, code in option_map.items():
        if re.search(pattern, cleaned):
            return code, ''
    return None, ''


def extract_other(text, keyword):
    """提取"其他（请说明___）"里的内容"""
    m = re.search(keyword + r'[（(]([^）)）\n]{1,80})', text)
    if m:
        content = m.group(1).strip('＿_')
        if content and not re.match(r'^[_＿\s]+$', content):
            return content
    return ''


def parse_activity_table(table_text):
    """解析活动说明表格文本，返回字段字典"""
    result = {}
    # 主题类型
    m = re.search(r'主题类型.*?单选.*?\n(.*?)(?=运用手法|$)', table_text, re.S)
    if m:
        chunk = m.group(1)
        code, _ = find_checked(chunk, SUBJECT_MAP)
        result['subject_type_code'] = code or ''
        if code == 'other':
            result['subject_type_other'] = extract_other(chunk, '其他')
        else:
            result['subject_type_other'] = ''
    # 运用手法
    m = re.search(r'运用手法.*?单选.*?\n(.*?)(?=数字化|$)', table_text, re.S)
    if m:
        chunk = m.group(1)
        code, _ = find_checked(chunk, METHOD_MAP)
        result['method_code'] = code or ''
        if code == 'other':
            result['method_other'] = extract_other(chunk, '其他')
        else:
            result['method_other'] = ''
    # 数字化/AI
    m = re.search(r'数字化.{0,20}(.*?)(?=改善就医|$)', table_text, re.S)
    if m:
        chunk = m.group(1)
        result['related_to_digital_ai'] = '☑是' in chunk or ('是' in chunk and '□是' not in chunk and '否' not in chunk.replace('☑否',''))
        if '☑是' in chunk:
            result['related_to_digital_ai'] = True
        elif '☑否' in chunk or '否' in chunk.replace('□否','').replace('☑否',''):
            result['related_to_digital_ai'] = False
        else:
            result['related_to_digital_ai'] = None
        # 精确判断
        result['related_to_digital_ai'] = '☑是' in chunk
    # 改善就医感受
    m = re.search(r'改善就医感受.*?单选.*?\n(.*?)(?=医疗质量安全|$)', table_text, re.S)
    if m:
        chunk = m.group(1)
        code, _ = find_checked(chunk, EXPERIENCE_MAP)
        result['experience_improve_code'] = code or ''
        if code == 'other':
            result['experience_improve_other'] = extract_other(chunk, '其他')
        else:
            result['experience_improve_other'] = ''
    # 医疗质量安全相关主题
    m = re.search(r'医疗质量安全\s*相关主题.*?单选.*?\n(.*?)(?=本期活动|$)', table_text, re.S)
    if m:
        chunk = m.group(1)
        code, _ = find_checked(chunk, QUALITY_MAP)
        result['quality_topic_code'] = code or ''
        if code == 'other':
            result['quality_topic_other'] = extract_other(chunk, '其他')
        else:
            result['quality_topic_other'] = ''
    # 跨部门
    m = re.search(r'跨部门.*?(☑是|☑否|是\s*□否|□是\s*☑否|□是.*?☑否|☑是.*?□否)', table_text, re.S)
    if m:
        val = m.group(1)
        result['cross_department'] = '☑是' in val or (re.match(r'^是', val.strip()))
    else:
        m2 = re.search(r'跨部门[^\n]*\n\s*(是|否)', table_text)
        if m2:
            result['cross_department'] = m2.group(1) == '是'
    return result


# ---- 按注册ID遍历 ----
REG_IDS = {
    '20260563': '宁波明州医院',
    '20260587': '杭州市临平区第一人民医院',
    '20260621': '浙江省台州医院',
    '20260632': '永康市妇幼保健院',
    '20260803': '宁波大学附属阳明医院',
    '20260889': '宁波明州医院',
    '20260893': '杭州市富阳区第三人民医院',
}

all_results = {}
for folder in sorted(os.listdir(BASE)):
    fpath = os.path.join(BASE, folder)
    if not os.path.isdir(fpath):
        continue
    reg_id = folder.split('_')[0]
    files = os.listdir(fpath)
    docx_files = [f for f in files if f.endswith('.docx') and not f.startswith('~$')]
    reg_forms  = [f for f in docx_files if '报名表' in f]
    # 所有docx都试一遍，找到有活动说明的那个
    activity_data = {}
    for fn in (reg_forms + [f for f in docx_files if f not in reg_forms]):
        try:
            doc = Document(os.path.join(fpath, fn))
            for ti, table in enumerate(doc.tables):
                # 把整张表的文本拼在一起
                table_text = '\n'.join(
                    ' | '.join(c.text.strip() for c in row.cells)
                    for row in table.rows
                )
                if '主题类型' in table_text and '运用手法' in table_text:
                    print(f'\n>>> {folder}  {fn}  表格{ti+1}  <找到活动说明>')
                    parsed = parse_activity_table(table_text)
                    for k, v in parsed.items():
                        print(f'    {k}: {repr(v)}')
                    activity_data = parsed
                    break
            if activity_data:
                break
        except Exception as e:
            print(f'  {fn} 读取失败: {e}')
    all_results[reg_id] = activity_data

# ---- 输出汇总 ----
print('\n\n' + '='*70)
print('汇总结果')
print('='*70)
for reg_id, data in all_results.items():
    print(f'\n-- {reg_id} --')
    if data:
        for k, v in data.items():
            print(f'  {k}: {repr(v)}')
    else:
        print('  【未能提取到活动说明数据】')
