import sys, re
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber

fp = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error\20260893_杭州市富阳区第三人民医院\材料1.基于PDCA循环提高严重精神障碍患者随访信息录入规范率报名表、活动说明、摘要内容.pdf'

with pdfplumber.open(fp) as pdf:
    print(f'总页数: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or '').strip()
        print(f'\n===== 第{i+1}页 ({len(text)}字) =====')
        if text:
            print(text)
        else:
            print('(无可提取文字，可能为扫描件)')
