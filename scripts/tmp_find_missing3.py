import openpyxl, io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
fname = next(f for f in os.listdir(base) if '评委分派' in f and f.endswith('.xlsx'))

wb = openpyxl.load_workbook(os.path.join(base, fname), data_only=True)
ws = wb['Sheet2']
rows = list(ws.iter_rows(values_only=True))

# 打印前40行 (含会场信息)
for i, row in enumerate(rows[:40]):
    if any(v is not None for v in row):
        print(f"  {i+1:>3}: {row}")
