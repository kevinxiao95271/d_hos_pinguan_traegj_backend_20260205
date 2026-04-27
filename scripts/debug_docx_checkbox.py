"""检查DOCX XML里的checkbox字符，以及缺失活动信息的文档的全文内容"""
import os, sys, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

# 检查 20260632 的主题类型checkbox原始XML
print('=== 检查 20260632 主题类型 checkboxes ===')
f = os.path.join(BASE, r'20260632_永康市妇幼保健院\材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容.docx')
try:
    with zipfile.ZipFile(f) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='replace')
    # 找主题类型附近的XML（前后各200字符）
    idx = xml.find('主题类型')
    if idx >= 0:
        chunk = xml[idx:idx+2000]
        # 找所有特殊字符（码点>127）
        chars = {}
        for c in chunk:
            if ord(c) > 127 and not c.isalpha():
                chars[c] = chars.get(c, 0) + 1
        print('特殊字符统计:', {hex(ord(k)): (k, v) for k, v in chars.items()})
        # 提取run文本
        runs = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', chunk)
        print('runs:', runs[:40])
except Exception as e:
    print(f'失败: {e}')

print()
# 对缺失活动说明的文档，打印段落全文（排除空行）
MISSING = {
    '20260563': '宁波明州医院报名表-"信息化赋能"提高术前去除毛发正确率.docx',
    '20260621': '报名表.docx',
    '20260803': '2026年浙江省医院品管大赛报名表.docx',
    '20260889': '宁波明州医院报名表-多团队协作降低阴道分娩产后尿潴留发生率.docx',
}
for reg_id, fname in MISSING.items():
    folder = [d for d in os.listdir(BASE) if d.startswith(reg_id)][0]
    fp = os.path.join(BASE, folder, fname)
    print(f'\n{"="*60}')
    print(f'【{reg_id}】{fname}')
    print('='*60)
    try:
        doc = Document(fp)
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                print(f'  P: {t}')
        print(f'  (共 {len(doc.tables)} 个表格, {len(doc.paragraphs)} 个段落)')
    except Exception as e:
        print(f'  失败: {e}')
