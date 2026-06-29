"""
离线解析 binlog.000005，提取今早 review_scores 的 INSERT/UPDATE 记录
"""
import io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'

# 今早 UTC+8 时间范围
TODAY = datetime.date(2026, 6, 3)

print(f'解析 {BINLOG} ...\n')

stream = BinLogStreamReader(
    connection_settings={
        'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
        'port': 63606,
        'user': 'root',
        'passwd': 'Yiguo9527_',
        'db': 'd_hos_pinguan_traegj_20260205',
    },
    server_id=999,
    log_file=BINLOG,
    blocking=False,
    resume_stream=True,
    only_tables=['review_scores'],
)

rows_found = []
try:
    for event in stream:
        if not isinstance(event, (WriteRowsEvent, UpdateRowsEvent)):
            continue
        ts = datetime.datetime.fromtimestamp(event.timestamp,
              tz=datetime.timezone(datetime.timedelta(hours=8)))
        if ts.date() != TODAY:
            continue
        etype = 'INSERT' if isinstance(event, WriteRowsEvent) else 'UPDATE'
        for row in event.rows:
            vals = row.get('values') or row.get('after_values') or {}
            rows_found.append((ts, etype, vals))
except Exception as e:
    print(f'解析中断: {e}')
finally:
    stream.close()

if not rows_found:
    print('今早无 review_scores 写入记录（binlog中未找到）')
else:
    print(f'共找到 {len(rows_found)} 条 review_scores 记录：\n')
    print(f'{"时间":10s}  {"类型":6s}  {"task_id":8s}  {"total":6s}  {"plan":5s}  {"problem":7s}  {"action":6s}  {"success":7s}  {"review":6s}  {"operation":9s}  {"presentation":12s}  {"item8":5s}')
    print('-' * 110)
    for ts, etype, v in rows_found:
        print(f'{ts.strftime("%H:%M:%S"):10s}  {etype:6s}  '
              f'{str(v.get("review_task_id","?")):8s}  '
              f'{str(v.get("total","?")):6s}  '
              f'{str(v.get("plan","?")):5s}  '
              f'{str(v.get("problem","?")):7s}  '
              f'{str(v.get("action","?")):6s}  '
              f'{str(v.get("success","?")):7s}  '
              f'{str(v.get("review","?")):6s}  '
              f'{str(v.get("operation","?")):9s}  '
              f'{str(v.get("presentation","?")):12s}  '
              f'{str(v.get("item8","?")):5s}')
