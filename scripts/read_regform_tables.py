"""读取7个报名表DOCX，打印所有表格内容，找出activity_infos所需字段"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

BASE = r'D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\7error'

# 每个文件夹里找报名表 docx（优先选文件名含"报名表"的）
folders = sorted(os.listdir(BASE))
for folder in folders:
    fpath = os.path.join(BASE, folder)
    if not os.path.isdir(fpath):
        continue
    files = os.listdir(fpath)
    # 优先"报名表"，其次取最小的 docx（报名表通常比成果报告小）
    docx_files = [f for f in files if f.endswith('.docx') and not f.startswith('~$')]
    reg_forms  = [f for f in docx_files if '报名表' in f]
    target     = reg_forms[0] if reg_forms else (docx_files[0] if docx_files else None)
    if not target:
        print(f'\n=== {folder}  ← 无DOCX ===')
        continue

    print(f'\n{"="*70}')
    print(f'【{folder}】  ← {target}')
    print('='*70)

    try:
        doc = Document(os.path.join(fpath, target))
        for ti, table in enumerate(doc.tables):
            print(f'\n--- 表格 {ti+1} ---')
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                # 合并相邻重复单元格（merged cells）
                seen = []
                for c in cells:
                    if not seen or c != seen[-1]:
                        seen.append(c)
                line = ' | '.join(seen)
                if line.strip():
                    print(f'  {line}')
    except Exception as e:
        print(f'  读取失败: {e}')
