"""
正确解码生产 binlog review_scores
TABLE_MAP 中的列类型: [8,8,5,5,5,5,5,5,5,5,15,15,18,246,15]
推断生产列顺序(按类型+Spring JPA字母序): 
  id(bigint), review_task_id(bigint),
  action(double), operation(double), plan(double), presentation(double),
  problem(double), review(double), success(double), total(double),
  highlight(varchar), weakness(varchar),
  submitted_at(datetime), item8(decimal), score_form(varchar)
"""
import struct, datetime, io, sys, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'
TS_START = int(datetime.datetime(2026, 6, 2, 16, 0, 0).timestamp())
TS_END   = int(datetime.datetime(2026, 6, 3, 16, 0, 0).timestamp())

with open(BINLOG, 'rb') as f:
    raw = f.read()

# ── 解析事件 ──────────────────────────────────────────────────────────────────
pos = 4; events = []
while pos < len(raw) - 19:
    ts_raw, etype, svid, ev_len, next_pos, flags = struct.unpack_from('<IBIIIH', raw, pos)
    if ev_len < 19 or ev_len > 10_000_000: pos += 1; continue
    if pos + ev_len > len(raw): break
    events.append({'pos':pos,'ts':ts_raw,'type':etype,'len':ev_len,'body':raw[pos+19:pos+ev_len]})
    pos += ev_len

# ── TABLE_MAP: 找 review_scores 的 table_id ───────────────────────────────────
table_map = {}
col_types_map = {}
col_meta_map = {}
for e in events:
    if e['type'] != 19: continue
    d = e['body']
    if len(d) < 10: continue
    tid = struct.unpack_from('<Q', d[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    idx = 8
    sl = d[idx]; idx += 1
    schema = d[idx:idx+sl].decode('utf-8','ignore'); idx += sl+1
    if idx >= len(d): continue
    tl = d[idx]; idx += 1
    table = d[idx:idx+tl].decode('utf-8','ignore'); idx += tl+1
    table_map[tid] = (schema, table)
    if 'review_score' not in table.lower(): continue
    # column_count (lenenc)
    b = d[idx]
    if b < 0xFB: col_cnt = b; idx += 1
    else: continue
    ctypes = list(d[idx:idx+col_cnt]); idx += col_cnt
    # column_meta (lenenc len + data)
    meta_len = d[idx]; idx += 1
    meta_data = d[idx:idx+meta_len]
    col_types_map[tid] = ctypes
    col_meta_map[tid] = meta_data

rs_ids = {tid for tid,(s,t) in table_map.items() if 'review_score' in t.lower()}
print(f'review_scores table_id(s): {rs_ids}')

if not rs_ids:
    print('未找到review_scores的TABLE_MAP事件')
    sys.exit()

first_tid = list(rs_ids)[0]
col_types = col_types_map.get(first_tid, [])
print(f'列类型({len(col_types)}): {col_types}')

# ── 生产列定义（基于 TABLE_MAP 类型推断）────────────────────────────────────────
# [8,8,5,5,5,5,5,5,5,5,15,15,18,246,15]
PROD_COLS = [
    ('id',             8),    # bigint
    ('review_task_id', 8),    # bigint
    ('action',         5),    # double
    ('operation',      5),    # double
    ('plan',           5),    # double
    ('presentation',   5),    # double
    ('problem',        5),    # double
    ('review',         5),    # double
    ('success',        5),    # double
    ('total',          5),    # double
    ('highlight',      15),   # varchar
    ('weakness',       15),   # varchar
    ('submitted_at',   18),   # datetime2
    ('item8',          246),  # decimal
    ('score_form',     15),   # varchar
]

# varchar 最大长度（从 meta_data 读）
# meta for varchar: 2 bytes max_length per varchar column
# meta for double: 0 bytes
# meta for bigint: 0 bytes
# meta for datetime2: 1 byte (fsp)
# meta for decimal: 2 bytes (precision, scale)
def parse_meta(col_types, meta_data):
    meta = []
    mi = 0
    for ct in col_types:
        if ct in (15, 253, 254):  # varchar/varstring/string
            if mi+2 <= len(meta_data):
                meta.append(struct.unpack_from('<H', meta_data, mi)[0]); mi += 2
            else: meta.append(255)
        elif ct in (0,1,2,3,4,5,6,7,8,9,13,14,16):  # numeric/float/double
            meta.append(0)
        elif ct == 246:  # decimal
            meta.append((meta_data[mi], meta_data[mi+1]) if mi+2<=len(meta_data) else (10,0)); mi += 2
        elif ct in (17, 18):  # timestamp2/datetime2
            meta.append(meta_data[mi] if mi<len(meta_data) else 0); mi += 1
        elif ct == 252:  # blob
            meta.append(meta_data[mi] if mi<len(meta_data) else 4); mi += 1
        else:
            meta.append(0)
    return meta

col_meta = parse_meta(col_types, col_meta_map.get(first_tid, b''))

def lenenc(buf, idx):
    if idx >= len(buf): return 0, idx
    b = buf[idx]
    if b < 0xFB: return b, idx+1
    if b == 0xFC: return struct.unpack_from('<H',buf,idx+1)[0], idx+3
    if b == 0xFD: return struct.unpack_from('<I',buf[idx+1:idx+4]+b'\x00')[0], idx+4
    return struct.unpack_from('<Q',buf,idx+1)[0], idx+9

def decode_col(buf, idx, ctype, meta):
    if ctype == 8:  # bigint
        if idx+8 > len(buf): return None, idx
        return struct.unpack_from('<q', buf, idx)[0], idx+8
    if ctype in (5,):  # double
        if idx+8 > len(buf): return None, idx
        return struct.unpack_from('<d', buf, idx)[0], idx+8
    if ctype == 4:  # float
        if idx+4 > len(buf): return None, idx
        return struct.unpack_from('<f', buf, idx)[0], idx+4
    if ctype in (15, 253):  # varchar
        max_len = meta if isinstance(meta, int) else 255
        nbytes = 2 if max_len > 255 else 1
        if idx+nbytes > len(buf): return None, idx
        slen = struct.unpack_from('<H' if nbytes==2 else 'B', buf, idx)[0]; idx += nbytes
        s = buf[idx:idx+slen].decode('utf-8','ignore')
        return s, idx+slen
    if ctype == 18:  # datetime2
        fsp = meta if isinstance(meta, int) else 0
        base = 5; extra = (fsp+1)//2
        if idx+base+extra > len(buf): return None, idx
        # 5-byte big-endian packed datetime
        v = int.from_bytes(buf[idx:idx+5], 'big')
        # sign bit at top
        sign = (v >> 39) & 1
        if not sign: return 'NULL_DT', idx+base+extra
        v &= 0x7FFFFFFFFF
        ymdhms = v
        # MySQL datetime2 encoding
        ym = (ymdhms >> 17) & 0x1FFFF
        day = (ymdhms >> 12) & 0x1F
        hm = (ymdhms >> 6) & 0x3F
        s_ = ymdhms & 0x3F
        year = ym // 13; month = ym % 13
        return f'{year:04d}-{month:02d}-{day:02d} {hm>>6:02d}:{hm&0x3F:02d}:{s_:02d}', idx+base+extra
    if ctype == 246:  # decimal/newdecimal
        prec, scale = (meta if isinstance(meta, tuple) else (10, 0))
        # rough size: ceil(prec/9)*4 - ceil(scale/9)*4 + ceil(scale/9)*4 + overflow
        # simplified: read bytes and skip
        int_part = prec - scale
        int_bytes = (int_part // 9) * 4 + [0,1,1,2,2,3,3,4,4,4][int_part % 9]
        frac_bytes = (scale // 9) * 4 + [0,1,1,2,2,3,3,4,4,4][scale % 9]
        total_b = int_bytes + frac_bytes + 1  # +1 for sign/overflow
        if idx+total_b > len(buf): return None, idx
        # just read as float approximation
        try:
            dec_bytes = buf[idx:idx+total_b]
            # high bit is sign (1=positive)
            is_neg = not (dec_bytes[0] & 0x80)
            return f'dec_{dec_bytes.hex()[:8]}', idx+total_b
        except:
            return None, idx+total_b
    if ctype in (3, 9):  # int/mediumint
        sz = 4 if ctype==3 else 3
        if idx+sz > len(buf): return None, idx
        return int.from_bytes(buf[idx:idx+sz], 'little', signed=True), idx+sz
    return f'unk{ctype}', idx+1

# ── 解码今早 review_scores WRITE 事件 ─────────────────────────────────────────
print(f'\n{"时间":8s}  {"类型":6s}  {"task_id":8s}  {"total":6s}  {"plan":5s}  {"problem":7s}  {"action":6s}  {"success":7s}  {"review":5s}  {"oper":5s}  {"pres":5s}  {"item8":5s}  {"form":8s}  sub')
print('-'*120)

decoded = []
for e in events:
    if e['ts'] < TS_START or e['ts'] > TS_END: continue
    if e['type'] not in (30, 31): continue
    body = e['body']
    if len(body) < 8: continue
    tid = struct.unpack_from('<Q', body[:6]+b'\x00\x00')[0] & 0xFFFFFFFFFF
    if tid not in rs_ids: continue

    ts = datetime.datetime.fromtimestamp(e['ts'], tz=datetime.timezone(datetime.timedelta(hours=8)))
    etype = 'WRITE' if e['type'] == 30 else 'UPDATE'
    N = len(col_types)
    nb = (N+7)//8

    idx = 6+2  # table_id + flags
    extra_len = struct.unpack_from('<H', body, idx)[0]; idx += extra_len
    col_cnt, idx = lenenc(body, idx)
    idx += nb  # columns_present

    def decode_one_row(body, idx):
        if idx+nb > len(body): return None, idx
        null_bm = body[idx:idx+nb]; idx += nb
        row = {}
        for ci,(cname,ctype_schema) in enumerate(PROD_COLS):
            if ci >= col_cnt: break
            is_null = (null_bm[ci//8] >> (ci%8)) & 1
            if is_null:
                row[cname] = None
            else:
                ct = col_types[ci] if ci < len(col_types) else 0
                m  = col_meta[ci]   if ci < len(col_meta)  else 0
                val, idx = decode_col(body, idx, ct, m)
                row[cname] = val
        return row, idx

    if etype == 'UPDATE':
        _, idx = decode_one_row(body, idx)  # skip before-image

    row, idx = decode_one_row(body, idx)
    if row is None: continue

    def f(v, d=1):
        if v is None: return '-'
        try: return str(round(float(v),d))
        except: return str(v)[:8]

    sub = 'Y' if row.get('submitted_at') not in (None,'NULL_DT') else 'N'
    decoded.append((ts, etype, row))
    print(f'{ts.strftime("%H:%M:%S"):8s}  {etype:6s}  '
          f'{f(row.get("review_task_id"),0):8s}  '
          f'{f(row.get("total")):6s}  '
          f'{f(row.get("plan")):5s}  '
          f'{f(row.get("problem")):7s}  '
          f'{f(row.get("action")):6s}  '
          f'{f(row.get("success")):7s}  '
          f'{f(row.get("review")):5s}  '
          f'{f(row.get("operation")):5s}  '
          f'{f(row.get("presentation")):5s}  '
          f'{f(row.get("item8")):5s}  '
          f'{str(row.get("score_form","?")):8s}  {sub}')

print(f'\n共 {len(decoded)} 条')
zero = [(ts,r) for ts,_,r in decoded if (r.get("total") or 0) == 0]
nonzero = [(ts,r) for ts,_,r in decoded if (r.get("total") or 0) > 0]
print(f'total=0  : {len(zero)} 条')
print(f'total>0  : {len(nonzero)} 条')
if nonzero:
    print('\ntotal>0 汇总:')
    for ts,r in sorted(nonzero, key=lambda x:x[0]):
        print(f'  {ts.strftime("%H:%M:%S")}  task={r.get("review_task_id")}  total={r.get("total")}  form={r.get("score_form")}')
