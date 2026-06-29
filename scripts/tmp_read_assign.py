import openpyxl, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
fname = next(f for f in os.listdir(base) if '评委分派' in f and f.endswith('.xlsx'))

wb = openpyxl.load_workbook(os.path.join(base, fname), data_only=True)
ws = wb['Sheet2']
rows = list(ws.iter_rows(values_only=True))
print(f"全部 {len(rows)} 行:\n")
for i, r in enumerate(rows):
    # 过滤全空行
    if any(v is not None for v in r):
        print(f"  {i:>2}: {r}")
