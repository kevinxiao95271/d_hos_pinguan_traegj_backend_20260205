import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

fp = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error\20260893_杭州市富阳区第三人民医院\材料1.2026年浙江省医院品管大赛报名表、活动说明、摘要内容模版.docx'
doc = Document(fp)

for ti, table in enumerate(doc.tables):
    rows_text = '\n'.join(' | '.join(c.text.strip() for c in row.cells) for row in table.rows)
    if '主题类型' in rows_text or '运用手法' in rows_text:
        print(f'===== 表格 {ti+1} (活动说明) =====\n')
        for row in table.rows:
            # 去重合并单元格
            cells = [c.text.strip() for c in row.cells]
            seen = []
            for c in cells:
                if not seen or c != seen[-1]:
                    seen.append(c)
            line = ' | '.join(seen)
            if line.strip():
                print(line)
        print()
