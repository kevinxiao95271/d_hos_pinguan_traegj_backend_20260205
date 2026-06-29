import os, docx, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
files = os.listdir(root)

# 找原版评分细则（不含529的）
originals = [f for f in files if f.endswith('.docx') and '529' not in f and '5.29' not in f]
print("原版评分细则文件:")
for f in originals:
    print(f"  {f}")

for fname in originals:
    path = os.path.join(root, fname)
    print(f"\n{'='*60}")
    print(f"文件: {fname}")
    print('='*60)
    try:
        doc = docx.Document(path)
        for para in doc.paragraphs:
            if para.text.strip():
                print(para.text)
        for table in doc.tables:
            print(f"\n[表格]")
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    print(' | '.join(cells))
    except Exception as e:
        print(f"  读取失败: {e}")
