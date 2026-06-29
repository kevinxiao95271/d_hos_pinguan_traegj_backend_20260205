import openpyxl, io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
fname = next(f for f in os.listdir(base) if '评委分派' in f and f.endswith('.xlsx'))
print(f"文件: {fname}")

wb = openpyxl.load_workbook(os.path.join(base, fname), data_only=True)

# 搜索 王泓权 和 潘翠萍
targets = {'王泓权', '潘翠萍'}

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    for i, row in enumerate(rows):
        for cell in row:
            if cell and any(t in str(cell) for t in targets):
                # Print context row and nearby rows
                print(f"\n[Sheet={sheet_name}, 行{i+1}]: {row}")
