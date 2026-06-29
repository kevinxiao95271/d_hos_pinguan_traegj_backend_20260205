"""
原始二进制解析 binlog.000005
不依赖 TABLE_MAP，直接按 MySQL binlog 协议逐事件扫描
提取今早(2026-06-03)所有 WRITE_ROWS / UPDATE_ROWS 事件的原始数据
"""
import struct, datetime, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'

# MySQL binlog magic
MAGIC = b'\xfebin'

# Event types
EVENT_TYPES = {
    2: 'QUERY',
    4: 'ROTATE',
    15: 'FORMAT_DESC',
    19: 'TABLE_MAP',
    30: 'WRITE_ROWS_v2',
    31: 'UPDATE_ROWS_v2',
    32: 'DELETE_ROWS_v2',
    33: 'WRITE_ROWS_v3',
    34: 'UPDATE_ROWS_v3',
    35: 'DELETE_ROWS_v3',
}

# 今早 UTC 时间戳范围（UTC+8 00:00 ~ 23:59）
TS_START = int(datetime.datetime(2026, 6, 2, 16, 0, 0).timestamp())  # UTC+8 2026-06-03 00:00
TS_END   = int(datetime.datetime(2026, 6, 3, 16, 0, 0).timestamp())  # UTC+8 2026-06-04 00:00

with open(BINLOG, 'rb') as f:
    data = f.read()

print(f'文件大小: {len(data):,} bytes')

# 验证magic
if data[:4] != MAGIC:
    print('警告: 不是标准binlog magic头')
else:
    print('binlog magic OK')

# 跳过4字节magic
pos = 4
events = []

while pos < len(data) - 19:
    # binlog event header: 4+1+4+4+4+2 = 19 bytes
    ts_raw, etype, server_id, ev_len, next_pos, flags = struct.unpack_from('<IBIIIH', data, pos)
    
    if ev_len < 19 or ev_len > 10*1024*1024:  # 异常长度跳过
        pos += 1
        continue
    
    if pos + ev_len > len(data):
        break
    
    ev_data = data[pos+19 : pos+ev_len]
    ts_dt = datetime.datetime.fromtimestamp(ts_raw, tz=datetime.timezone(datetime.timedelta(hours=8)))
    
    events.append({
        'pos': pos,
        'ts': ts_dt,
        'ts_raw': ts_raw,
        'type': etype,
        'type_name': EVENT_TYPES.get(etype, f'UNKNOWN({etype})'),
        'len': ev_len,
        'data': ev_data,
    })
    
    pos += ev_len

print(f'解析事件数: {len(events)}')
if events:
    print(f'时间范围: {events[0]["ts"]} ~ {events[-1]["ts"]}')

# 统计今天的事件
today_events = [e for e in events if TS_START <= e['ts_raw'] <= TS_END]
print(f'\n今早(2026-06-03 UTC+8)事件数: {len(today_events)}')

from collections import Counter
type_cnt = Counter(e['type_name'] for e in today_events)
for k,v in type_cnt.most_common():
    print(f'  {k}: {v}')

# 提取 TABLE_MAP 事件（获取 table_id -> table_name 映射）
table_map = {}
for e in events:
    if e['type'] == 19:  # TABLE_MAP
        d = e['data']
        if len(d) < 8: continue
        table_id = struct.unpack_from('<Q', d[:6] + b'\x00\x00')[0] & 0xFFFFFFFFFF
        # schema_len(1) + schema + 0x00 + table_len(1) + table + 0x00
        idx = 6  # skip table_id(6) + reserved(2) = 8? 
        # actually: table_id(6) + reserved(2)
        idx = 8
        if idx >= len(d): continue
        schema_len = d[idx]; idx += 1
        schema = d[idx:idx+schema_len].decode('utf-8','ignore'); idx += schema_len + 1
        if idx >= len(d): continue
        table_len = d[idx]; idx += 1
        table = d[idx:idx+table_len].decode('utf-8','ignore')
        table_map[table_id] = f'{schema}.{table}'

print(f'\n表映射({len(table_map)}个):')
for tid, tname in sorted(table_map.items()):
    print(f'  table_id={tid}  {tname}')

# 找 review_scores 的 table_id
rs_ids = {tid for tid, tname in table_map.items() if 'review_score' in tname.lower()}
print(f'\nreview_scores table_id(s): {rs_ids}')

# 找今早的 WRITE/UPDATE 事件中属于 review_scores 的
write_events = [e for e in today_events if e['type'] in (30,31,33,34)]
print(f'今早 WRITE/UPDATE 事件: {len(write_events)} 个')

rs_events = []
for e in write_events:
    d = e['data']
    if len(d) < 6: continue
    tid = struct.unpack_from('<Q', d[:6] + b'\x00\x00')[0] & 0xFFFFFFFFFF
    tname = table_map.get(tid, f'unknown_{tid}')
    if 'review_score' in tname.lower() or not rs_ids:
        rs_events.append((e, tid, tname))

print(f'  其中 review_scores: {len(rs_events)} 个')

if not rs_events:
    # 显示所有今早WRITE事件的涉及表
    print('\n今早所有写入事件:')
    for e in write_events[:30]:
        d = e['data']
        if len(d) < 6: continue
        tid = struct.unpack_from('<Q', d[:6] + b'\x00\x00')[0] & 0xFFFFFFFFFF
        tname = table_map.get(tid, f'unknown_{tid}')
        print(f'  {e["ts"].strftime("%H:%M:%S")}  {e["type_name"]}  table_id={tid}  {tname}  len={e["len"]}')
    
    # 显示总体事件分布（不限今天）
    print('\n全部binlog事件统计:')
    all_type_cnt = Counter(e['type_name'] for e in events)
    for k,v in all_type_cnt.most_common():
        print(f'  {k}: {v}')
    all_tbl_cnt = Counter(
        table_map.get(struct.unpack_from('<Q', e['data'][:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF, 'unknown')
        for e in events if e['type'] in (30,31,32,33,34,35) and len(e['data'])>=6
    )
    print('\n全部写入表:')
    for k,v in all_tbl_cnt.most_common(20):
        print(f'  {k}: {v}')
