"""
1. 验证 20260632/20260893 主题类型的XML run序列
2. 检查20260563汇报书DOCX + 20260803汇报书DOCX
3. 检查20260803 PDF 第2页、20260889 PDF 全文
"""
import os, sys, re, zipfile, glob
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
import pdfplumber

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

def get_folder(reg_id):
    return os.path.join(BASE, [d for d in os.listdir(BASE) if d.startswith(reg_id)][0])

def inspect_subject_type_runs(reg_id, fname):
    folder = get_folder(reg_id)
    fp = os.path.join(folder, fname)
    with zipfile.ZipFile(fp) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='replace')
    idx = xml.find('主题类型')
    if idx < 0:
        print('  未找到主题类型')
        return
    chunk = xml[idx:idx+4000]
    runs = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', chunk)
    print(f'  全部run ({len(runs)}) 近主题类型:')
    for i, r in enumerate(runs[:80]):
        marker = '  <-- □' if r.strip() == '□' else ('  <-- ☑' if '☑' in r else '')
        print(f'    [{i:02d}] {repr(r)}{marker}')

print('='*60)
print('20260632 主题类型 XML runs')
inspect_subject_type_runs('20260632', '材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容.docx')

print()
print('='*60)
print('20260893 主题类型 XML runs')
inspect_subject_type_runs('20260893', '材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容模版.docx')

# 20260563 汇报书
print()
print('='*60)
print('20260563 汇报书 tables')
folder = get_folder('20260563')
files = os.listdir(folder)
docx_files = [f for f in files if f.endswith('.docx') and not f.startswith('~$')]
for fn in docx_files:
    fp = os.path.join(folder, fn)
    print(f'  -- {fn} --')
    try:
        doc = Document(fp)
        print(f'     表格数: {len(doc.tables)}, 段落数: {len(doc.paragraphs)}')
        for ti, t in enumerate(doc.tables):
            rows_text = '\n'.join(' | '.join(c.text.strip() for c in row.cells) for row in t.rows)
            if '主题类型' in rows_text or '运用手法' in rows_text:
                print(f'     *** 表格{ti+1}有活动说明! ***')
                print(rows_text[:1000])
    except Exception as e:
        print(f'     失败: {e}')

# 20260621 报告书 DOCX (精益A3，体积最大)
print()
print('='*60)
print('20260621 所有DOCX表格概况')
folder = get_folder('20260621')
files = os.listdir(folder)
docx_files = [f for f in files if f.endswith('.docx') and not f.startswith('~$')]
for fn in docx_files:
    fp = os.path.join(folder, fn)
    print(f'  -- {fn} --')
    try:
        doc = Document(fp)
        print(f'     表格数: {len(doc.tables)}, 段落数: {len(doc.paragraphs)}')
        for ti, t in enumerate(doc.tables[:5]):
            rows_text = '\n'.join(' | '.join(c.text.strip() for c in row.cells) for row in t.rows)
            if '主题类型' in rows_text or '运用手法' in rows_text:
                print(f'     *** 表格{ti+1}有活动说明! ***')
                print(rows_text[:1000])
    except Exception as e:
        print(f'     失败: {e}')

# 20260803 PDF 全部页面
print()
print('='*60)
print('20260803 PDF 全页文字检查')
folder = get_folder('20260803')
files = os.listdir(folder)
pdf_files = [f for f in files if f.endswith('.pdf')]
for fn in pdf_files:
    fp = os.path.join(folder, fn)
    print(f'  -- {fn} --')
    try:
        with pdfplumber.open(fp) as pdf:
            for i, page in enumerate(pdf.pages):
                t = (page.extract_text() or '').strip()
                if '主题类型' in t or '运用手法' in t:
                    print(f'     *** 第{i+1}页有活动说明! ***')
                    print(t[:1000])
                elif t:
                    print(f'     第{i+1}页: {t[:80]}...')
                else:
                    print(f'     第{i+1}页: (空)')
    except Exception as e:
        print(f'     失败: {e}')

# 20260889 报名表PDF (宁波明州)
print()
print('='*60)
print('20260889 报名表PDF检查')
folder = get_folder('20260889')
files = os.listdir(folder)
pdf_files = [f for f in files if f.endswith('.pdf') and '报名表' in f]
for fn in pdf_files:
    fp = os.path.join(folder, fn)
    print(f'  -- {fn} --')
    try:
        with pdfplumber.open(fp) as pdf:
            print(f'     页数: {len(pdf.pages)}')
            for i, page in enumerate(pdf.pages):
                t = (page.extract_text() or '').strip()
                print(f'     第{i+1}页字符数: {len(t)}')
                if t:
                    print(f'     内容预览: {t[:200]}')
    except Exception as e:
        print(f'     失败: {e}')
