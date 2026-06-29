"""
手动解码今早 binlog review_scores WRITE/UPDATE 事件
列顺序: id, action, highlight, operation, plan, presentation, problem,
        review, submitted_at, success, total, weakness, review_task_id, item8, score_form
"""
import struct, datetime, io, sys, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'
TS_START = int(datetime.datetime(2026, 6, 2, 16, 0, 0).timestamp())
TS_END   = int(datetime.datetime(2026, 6, 3, 16, 0, 0).timestamp())

with open(BINLOG, 'rb') as f:
    raw = f.read()

# ── 解析所有事件 ──────────────────────────────────────────────────────────────
pos = 4; events = []
while pos < len(raw) - 19:
    ts_raw, etype, svid, ev_len, next_pos, flags = struct.unpack_from('<IBIIIH', raw, pos)
    if ev_len < 19 or ev_len > 10_000_000: pos += 1; continue
    if pos + ev_len > len(raw): break
    events.append({'pos':pos,'ts':ts_raw,'type':etype,'len':ev_len,'body':raw[pos+19:pos+ev_len]})
    pos += ev_len

# ── TABLE_MAP ─────────────────────────────────────────────────────────────────
table_map = {}
for e in events:
    if e['type'] != 19: continue
    d = e['body']
    if len(d) < 10: continue
    tid = struct.unpack_from('<Q', d[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    idx = 8
    sl = d[idx]; idx += 1
    schema = d[idx:idx+sl].decode('utf-8','ignore'); idx += sl+1
    tl = d[idx]; idx += 1
    table = d[idx:idx+tl].decode('utf-8','ignore')
    table_map[tid] = (schema, table)

rs_ids = {tid for tid,(s,t) in table_map.items() if 'review_score' in t.lower()}
print(f'review_scores table_id: {rs_ids}')

# ── 从测试库获取列类型 ──────────────────────────────────────────────────────────
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM review_scores")
col_defs = cur.fetchall()  # (Field, Type, Null, Key, Default, Extra)
cur.close(); conn.close()

COLS = [(row[0], row[1]) for row in col_defs]
print('列:', [(c,t[:12]) for c,t in COLS])
N = len(COLS)

# MySQL binlog 类型常量 (from COLUMN_TYPE in TABLE_MAP)
# 我们从 TABLE_MAP 的 column_type 字段读取

# 先从 TABLE_MAP 拿列类型字节
col_types_by_tid = {}
for e in events:
    if e['type'] != 19: continue
    d = e['body']
    if len(d) < 10: continue
    tid = struct.unpack_from('<Q', d[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    if tid not in rs_ids: continue
    idx = 8
    sl = d[idx]; idx += 1; idx += sl+1
    tl = d[idx]; idx += 1; idx += tl+1
    # column_count (lenenc)
    b = d[idx]
    if b < 0xFB: col_cnt = b; idx += 1
    elif b == 0xFC: col_cnt = struct.unpack_from('<H',d,idx+1)[0]; idx += 3
    else: col_cnt = 0; idx += 1
    # column_type array
    col_types = list(d[idx:idx+col_cnt])
    col_types_by_tid[tid] = col_types
    break

for tid, ctypes in col_types_by_tid.items():
    print(f'\ntable_id={tid} 列类型({len(ctypes)}): {ctypes}')
    for i,(ctype,coldef) in enumerate(zip(ctypes, COLS)):
        print(f'  [{i:2d}] {coldef[0]:20s} mysql_type={ctype:3d}  schema_type={coldef[1][:20]}')

# ── 解码行 ─────────────────────────────────────────────────────────────────────
def lenenc(buf, idx):
    b = buf[idx]
    if b < 0xFB: return b, idx+1
    if b == 0xFC: return struct.unpack_from('<H',buf,idx+1)[0], idx+3
    if b == 0xFD: return struct.unpack_from('<I',buf[idx+1:idx+4]+b'\x00')[0], idx+4
    return struct.unpack_from('<Q',buf,idx+1)[0], idx+9

MYSQL_TYPE_LONGLONG = 8
MYSQL_TYPE_DOUBLE   = 5
MYSQL_TYPE_FLOAT    = 4
MYSQL_TYPE_DATETIME2 = 18
MYSQL_TYPE_TIMESTAMP2 = 17
MYSQL_TYPE_BLOB      = 252
MYSQL_TYPE_VARCHAR   = 15
MYSQL_TYPE_VAR_STRING = 253
MYSQL_TYPE_STRING    = 254
MYSQL_TYPE_LONG      = 3
MYSQL_TYPE_INT24     = 9

def decode_value(buf, idx, mysql_type):
    if mysql_type == MYSQL_TYPE_LONGLONG:
        if idx+8 > len(buf): return None, idx
        return struct.unpack_from('<q', buf, idx)[0], idx+8
    if mysql_type == MYSQL_TYPE_DOUBLE:
        if idx+8 > len(buf): return None, idx
        return struct.unpack_from('<d', buf, idx)[0], idx+8
    if mysql_type == MYSQL_TYPE_FLOAT:
        if idx+4 > len(buf): return None, idx
        return struct.unpack_from('<f', buf, idx)[0], idx+4
    if mysql_type == MYSQL_TYPE_DATETIME2:
        if idx+5 > len(buf): return None, idx
        # MySQL DATETIME2 = 5 bytes packed
        v = int.from_bytes(buf[idx:idx+5], 'big')
        # year_month = (v >> 22) & 0x1FFFF; etc.
        ymd = (v >> 17) & 0x1FFFF; hms = (v >> 5) & 0xFFF; sub = v & 0x1F
        year = ymd >> 5; ym = ymd & 0x1F; day = ym  # rough
        return f'datetime({v:010x})', idx+5
    if mysql_type in (MYSQL_TYPE_BLOB, MYSQL_TYPE_VARCHAR, MYSQL_TYPE_VAR_STRING, MYSQL_TYPE_STRING):
        if idx >= len(buf): return None, idx
        slen, idx2 = lenenc(buf, idx)
        s = buf[idx2:idx2+slen].decode('utf-8','ignore')
        return s, idx2+slen
    if mysql_type == MYSQL_TYPE_LONG:
        if idx+4 > len(buf): return None, idx
        return struct.unpack_from('<i', buf, idx)[0], idx+4
    # unknown
    return f'unk_type{mysql_type}', idx

# 取第一个 rs_ids 的 col_types
if not col_types_by_tid:
    print('未找到TABLE_MAP中review_scores的列类型')
    sys.exit()

first_tid = list(col_types_by_tid.keys())[0]
col_types = col_types_by_tid[first_tid]

# 解码今早所有 review_scores WRITE/UPDATE
print(f'\n{"时间":8s}  {"类型":6s}  {"task_id":8s}  {"total":6s}  {"plan":5s}  {"problem":7s}  {"action":6s}  {"success":7s}  {"review":5s}  {"oper":5s}  {"pres":5s}  {"item8":5s}  {"form":8s}  {"submitted":5s}')
print('-'*120)

decoded_rows = []
for e in events:
    if e['ts'] < TS_START or e['ts'] > TS_END: continue
    if e['type'] not in (30, 31): continue
    body = e['body']
    if len(body) < 8: continue
    tid = struct.unpack_from('<Q', body[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    if tid not in rs_ids: continue

    ts = datetime.datetime.fromtimestamp(e['ts'], tz=datetime.timezone(datetime.timedelta(hours=8)))
    etype = 'WRITE' if e['type'] == 30 else 'UPDATE'

    # parse rows
    idx = 6  # skip table_id
    idx += 2  # flags
    extra_len = struct.unpack_from('<H', body, idx)[0]; idx += extra_len
    col_cnt, idx = lenenc(body, idx)
    # columns_present bitmap
    cbytes = (col_cnt+7)//8
    idx += cbytes  # skip columns_present

    while idx < len(body):
        # UPDATE: skip "before" row
        if e['type'] == 31:
            nb = (col_cnt+7)//8
            null_bm = body[idx:idx+nb]; idx += nb
            for ci in range(col_cnt):
                is_null = (null_bm[ci//8] >> (ci%8)) & 1
                if not is_null:
                    _, idx = decode_value(body, idx, col_types[ci] if ci < len(col_types) else 0)

        # null bitmap for current row
        nb = (col_cnt+7)//8
        if idx+nb > len(body): break
        null_bm = body[idx:idx+nb]; idx += nb

        row = {}
        ok = True
        for ci,(cname,_) in enumerate(COLS):
            if ci >= col_cnt: break
            is_null = (null_bm[ci//8] >> (ci%8)) & 1
            if is_null:
                row[cname] = None
            else:
                val, new_idx = decode_value(body, idx, col_types[ci] if ci < len(col_types) else 0)
                if new_idx <= idx:
                    ok = False; break
                row[cname] = val; idx = new_idx
        if not ok: break

        def fmt(v, decimals=1):
            if v is None: return 'null'
            try: return str(round(float(v), decimals))
            except: return str(v)[:8]

        submitted = 'Y' if row.get('submitted_at') else 'N'
        decoded_rows.append((ts, etype, row))
        print(f'{ts.strftime("%H:%M:%S"):8s}  {etype:6s}  '
              f'{fmt(row.get("review_task_id"),0):8s}  '
              f'{fmt(row.get("total")):6s}  '
              f'{fmt(row.get("plan")):5s}  '
              f'{fmt(row.get("problem")):7s}  '
              f'{fmt(row.get("action")):6s}  '
              f'{fmt(row.get("success")):7s}  '
              f'{fmt(row.get("review")):5s}  '
              f'{fmt(row.get("operation")):5s}  '
              f'{fmt(row.get("presentation")):5s}  '
              f'{fmt(row.get("item8")):5s}  '
              f'{str(row.get("score_form","?")):8s}  '
              f'{submitted}')
        break  # 每个事件只取一行（简化）

print(f'\n共输出 {len(decoded_rows)} 条')
print(f'total=0 的记录数: {sum(1 for _,_,r in decoded_rows if (r.get("total") or 0)==0)}')
print(f'total>0 的记录数: {sum(1 for _,_,r in decoded_rows if (r.get("total") or 0)>0)}')
