"""深度检查 20260632 XML 里主题类型、运用手法的勾选情况"""
import os, sys, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

def inspect_docx_xml(reg_prefix, fname, keyword='主题类型', window=3000):
    folder = [d for d in os.listdir(BASE) if d.startswith(reg_prefix)][0]
    fp = os.path.join(BASE, folder, fname)
    with zipfile.ZipFile(fp) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='replace')
    idx = xml.find(keyword)
    if idx < 0:
        print(f'  未找到 {keyword}')
        return
    chunk = xml[idx:idx+window]
    # 提取所有run内容
    runs = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', chunk)
    print(f'runs near "{keyword}":')
    for i, r in enumerate(runs[:60]):
        special = [(hex(ord(c)), c) for c in r if ord(c) > 127]
        print(f'  [{i:02d}] {repr(r)}  special={special}')

print('=== 20260632 主题类型 ===')
inspect_docx_xml('20260632', '材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容.docx', '主题类型')

print('\n=== 20260587 主题类型 ===')
inspect_docx_xml('20260587', '2026年浙江省医院品管大赛报名表、活动说明、摘要内容模版.docx', '主题类型')

print('\n=== 20260893 主题类型 ===')
inspect_docx_xml('20260893', '材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容模版.docx', '主题类型')

# 对20260563用glob找文件
print('\n=== 20260563 文件列表 ===')
folder = [d for d in os.listdir(BASE) if d.startswith('20260563')][0]
fpath = os.path.join(BASE, folder)
for f in os.listdir(fpath):
    print(f'  {repr(f)}')
