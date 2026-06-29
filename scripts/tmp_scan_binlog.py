"""扫描 binlog 全部事件，了解时间范围和涉及的表"""
import io, sys, datetime, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent
from pymysqlreplication.event import QueryEvent, RotateEvent

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'

stream = BinLogStreamReader(
    connection_settings={
        'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
        'port': 63606, 'user': 'root', 'passwd': 'Yiguo9527_',
        'db': 'd_hos_pinguan_traegj_20260205',
    },
    server_id=999,
    log_file=BINLOG,
    blocking=False,
    resume_stream=True,
)

first_ts = last_ts = None
table_counts = collections.Counter()
total_events = 0

try:
    for event in stream:
        total_events += 1
        if event.timestamp:
            ts = datetime.datetime.fromtimestamp(event.timestamp,
                 tz=datetime.timezone(datetime.timedelta(hours=8)))
            if first_ts is None: first_ts = ts
            last_ts = ts
        if isinstance(event, (WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent)):
            tbl = f'{event.schema}.{event.table}'
            table_counts[tbl] += 1
except Exception as e:
    print(f'解析中断: {e}')
finally:
    stream.close()

print(f'总事件数: {total_events}')
print(f'时间范围: {first_ts} ~ {last_ts}')
print(f'\n涉及的表 (写入/更新/删除):')
for tbl, cnt in table_counts.most_common():
    print(f'  {tbl:50s} {cnt} 次')
