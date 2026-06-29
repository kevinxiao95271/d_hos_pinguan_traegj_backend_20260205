"""
解码 binlog.000005 今早 review_scores 的 WRITE/UPDATE 行数据
"""
import struct, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'

TS_START = int(datetime.datetime(2026, 6, 2, 16, 0, 0).timestamp())
TS_END   = int(datetime.datetime(2026, 6, 3, 16, 0, 0).timestamp())

with open(BINLOG, 'rb') as f:
    data = f.read()

pos = 4
events = []
while pos < len(data) - 19:
    ts_raw, etype, server_id, ev_len, next_pos, flags = struct.unpack_from('<IBIIIH', data, pos)
    if ev_len < 19 or ev_len > 10*1024*1024:
        pos += 1; continue
    if pos + ev_len > len(data): break
    events.append({'pos': pos, 'ts_raw': ts_raw, 'type': etype,
                   'len': ev_len, 'data': data[pos+19:pos+ev_len]})
    pos += ev_len

# 建 table_map
table_map = {}
for e in events:
    if e['type'] == 19:
        d = e['data']
        if len(d) < 8: continue
        tid = struct.unpack_from('<Q', d[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
        idx = 8
        if idx >= len(d): continue
        sl = d[idx]; idx += 1
        schema = d[idx:idx+sl].decode('utf-8','ignore'); idx += sl+1
        if idx >= len(d): continue
        tl = d[idx]; idx += 1
        table = d[idx:idx+tl].decode('utf-8','ignore')
        table_map[tid] = (schema, table)

rs_ids = {tid for tid,(s,t) in table_map.items() if 'review_score' in t}

# review_scores 列定义（与实体对齐）
# id(bigint) created_at(datetime) updated_at(datetime) action(double) highlight(text)
# item8(double) operation(double) plan(double) presentation(double) problem(double)
# review(double) score_form(varchar) submitted_at(datetime) success(double) total(double)
# weakness(text) review_task_id(bigint)
# 实际列顺序以 SHOW COLUMNS 为准，这里尝试直接读数值
import pymysql
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM review_scores")
columns = [row[0] for row in cur.fetchall()]
cur.close(); conn.close()
print('列顺序:', columns)

def read_lenenc_int(buf, pos):
    b = buf[pos]
    if b < 0xFB: return b, pos+1
    if b == 0xFC: return struct.unpack_from('<H', buf, pos+1)[0], pos+3
    if b == 0xFD: v = struct.unpack_from('<I', buf[pos+1:pos+4]+b'\x00')[0]; return v, pos+4
    if b == 0xFE: return struct.unpack_from('<Q', buf, pos+1)[0], pos+9
    return 0, pos+1

def parse_row(buf, col_count):
    """粗略解析行：跳过null bitmap，按列类型读值"""
    # null bitmap: ceil(col_count/8) bytes
    null_bytes = (col_count + 7) // 8
    null_bitmap = buf[:null_bytes]
    idx = null_bytes
    vals = []
    for i in range(col_count):
        is_null = (null_bitmap[i//8] >> (i%8)) & 1
        if is_null:
            vals.append(None)
        else:
            # 保守：读8字节double尝试
            if idx + 8 <= len(buf):
                v = struct.unpack_from('<d', buf, idx)[0]
                vals.append(v)
                idx += 8
            else:
                vals.append('?')
    return vals

# 今早 review_scores WRITE/UPDATE 事件
results = []
for e in events:
    if e['ts_raw'] < TS_START or e['ts_raw'] > TS_END: continue
    if e['type'] not in (30, 31): continue  # WRITE_ROWS_v2, UPDATE_ROWS_v2
    d = e['data']
    if len(d) < 6: continue
    tid = struct.unpack_from('<Q', d[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    if tid not in rs_ids: continue
    ts = datetime.datetime.fromtimestamp(e['ts_raw'],
         tz=datetime.timezone(datetime.timedelta(hours=8)))
    results.append((ts, e['type'], tid, d))

print(f'\n今早 review_scores 事件数: {len(results)}')

# 用 pymysqlreplication 精确解码
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent

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
    only_schemas=['pgds'],
)

rows_found = []
try:
    for event in stream:
        if not isinstance(event, (WriteRowsEvent, UpdateRowsEvent)): continue
        if 'review_score' not in event.table.lower(): continue
        if not (TS_START <= event.timestamp <= TS_END): continue
        ts = datetime.datetime.fromtimestamp(event.timestamp,
             tz=datetime.timezone(datetime.timedelta(hours=8)))
        etype = 'INSERT' if isinstance(event, WriteRowsEvent) else 'UPDATE'
        for row in event.rows:
            vals = row.get('values') or row.get('after_values') or {}
            rows_found.append((ts, etype, vals))
except Exception as ex:
    print(f'stream解析: {ex}')
finally:
    stream.close()

if rows_found:
    print(f'\n精确解码 {len(rows_found)} 条 review_scores 记录:\n')
    print(f'{"时间":8s}  {"类型":6s}  {"task_id":8s}  {"total":6s}  {"plan":5s}  {"problem":7s}  {"action":6s}  {"success":7s}  {"review":5s}  {"oper":5s}  {"pres":5s}  {"item8":5s}  {"form":8s}')
    print('-'*100)
    for ts, etype, v in rows_found:
        print(f'{ts.strftime("%H:%M:%S"):8s}  {etype:6s}  '
              f'{str(v.get("review_task_id","?")):8s}  '
              f'{str(round(v.get("total",0) or 0,1)):6s}  '
              f'{str(round(v.get("plan",0) or 0,1)):5s}  '
              f'{str(round(v.get("problem",0) or 0,1)):7s}  '
              f'{str(round(v.get("action",0) or 0,1)):6s}  '
              f'{str(round(v.get("success",0) or 0,1)):7s}  '
              f'{str(round(v.get("review",0) or 0,1)):5s}  '
              f'{str(round(v.get("operation",0) or 0,1)):5s}  '
              f'{str(round(v.get("presentation",0) or 0,1)):5s}  '
              f'{str(round(v.get("item8",0) or 0,1)):5s}  '
              f'{v.get("score_form","?"):8s}')
else:
    print('\n未能精确解码，输出今早 review_scores 事件时间点:')
    for ts, etype, tid, d in results[:20]:
        print(f'  {ts.strftime("%H:%M:%S")}  {"WRITE" if etype==30 else "UPDATE"}  table_id={tid}  data_len={len(d)}')
