import openpyxl, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
fname = '弃赛项目汇总(1).xlsx'
path = os.path.join(base, fname)
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb['Sheet1']
rows = list(ws.iter_rows(values_only=True))

print(f"全部 {len(rows)} 行：")
for i, r in enumerate(rows):
    print(f"  {i}: {r}")
