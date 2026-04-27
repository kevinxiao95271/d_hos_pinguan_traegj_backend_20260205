"""
从 binlog 找李雅岑(reviewer_id=703)的所有打分记录
步骤1: 扫 review_tasks，找 reviewer_id=703 的 task_id
步骤2: 扫 review_scores，按 task_id 过滤，取最后一次有效打分
"""
import struct, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET_REVIEWER_ID = 703
MAGIC = b'\xfebin'

TABLE_MAP_EVENT = 19
WRITE_ROWS_V1, UPDATE_ROWS_V1, DELETE_ROWS_V1 = 23, 24, 25
WRITE_ROWS_V2, UPDATE_ROWS_V2, DELETE_ROWS_V2 = 30, 31, 32
ROW_WRITE  = {WRITE_ROWS_V1, WRITE_ROWS_V2}
ROW_UPDATE = {UPDATE_ROWS_V1, UPDATE_ROWS_V2}
ROW_DELETE = {DELETE_ROWS_V1, DELETE_ROWS_V2}
ROW_EVENTS = ROW_WRITE | ROW_UPDATE | ROW_DELETE

TYPE_LONGLONG = 8
TYPE_DOUBLE   = 5
TYPE_VARCHAR  = 15
TYPE_VAR_STR  = 253
TYPE_BLOB     = 252
TYPE_DATETIME2= 18
TYPE_TINY     = 1
TYPE_SHORT    = 2
TYPE_LONG     = 3
TYPE_STRING   = 254
TYPE_ENUM     = 247
TYPE_SET      = 248

def read_lenenc(data, pos):
    if pos >= len(data): return 0, pos
    b = data[pos]
    if b < 0xfb:   return b, pos+1
    if b == 0xfc:  return struct.unpack_from('<H', data, pos+1)[0], pos+3
    if b == 0xfd:
        v = int.from_bytes(data[pos+1:pos+4], 'little')
        return v, pos+4
    return struct.unpack_from('<Q', data, pos+1)[0], pos+9

def parse_table_map(body):
    pos = 0
    tid = int.from_bytes(body[pos:pos+6], 'little'); pos = 8
    db_len = body[pos]; pos += 1
    db = body[pos:pos+db_len].decode('utf-8','replace'); pos += db_len+1
    tl = body[pos]; pos += 1
    tbl = body[pos:pos+tl].decode('utf-8','replace'); pos += tl+1
    col_count, pos = read_lenenc(body, pos)
    col_types = list(body[pos:pos+col_count]); pos += col_count
    meta_len, pos = read_lenenc(body, pos)
    meta_raw = body[pos:pos+meta_len]
    # 解析 meta
    metas = {}
    mp = 0
    for ci, ct in enumerate(col_types):
        if ct in (TYPE_VARCHAR, TYPE_VAR_STR, TYPE_STRING):
            if mp+2 <= len(meta_raw):
                metas[ci] = struct.unpack_from('<H', meta_raw, mp)[0]; mp += 2
        elif ct in (TYPE_DOUBLE, TYPE_BLOB, TYPE_DATETIME2):
            if mp < len(meta_raw):
                metas[ci] = meta_raw[mp]; mp += 1
        elif ct in (TYPE_ENUM, TYPE_SET):
            if mp < len(meta_raw):
                metas[ci] = meta_raw[mp]; mp += 1
    return tid, db, tbl, col_types, metas

def read_col(data, pos, ctype, meta):
    """读一列，返回 (value, new_pos)"""
    try:
        if ctype == TYPE_LONGLONG:
            return struct.unpack_from('<q', data, pos)[0], pos+8
        if ctype in (TYPE_LONG,):
            return struct.unpack_from('<i', data, pos)[0], pos+4
        if ctype in (TYPE_SHORT,):
            return struct.unpack_from('<h', data, pos)[0], pos+2
        if ctype == TYPE_TINY:
            return data[pos], pos+1
        if ctype == TYPE_DOUBLE:
            return struct.unpack_from('<d', data, pos)[0], pos+8
        if ctype in (TYPE_VARCHAR, TYPE_VAR_STR, TYPE_STRING):
            slen_bytes = 2 if meta > 255 else 1
            slen = int.from_bytes(data[pos:pos+slen_bytes], 'little'); pos += slen_bytes
            return data[pos:pos+slen].decode('utf-8','replace'), pos+slen
        if ctype == TYPE_BLOB:
            lb = meta if meta else 2
            slen = int.from_bytes(data[pos:pos+lb], 'little'); pos += lb
            return data[pos:pos+slen].decode('utf-8','replace'), pos+slen
        if ctype == TYPE_DATETIME2:
            raw = int.from_bytes(data[pos:pos+5], 'big')
            frac_bytes = (meta+1)//2 if meta else 0
            pos2 = pos+5+frac_bytes
            ym = (raw>>22) & 0x7FFF
            yr, mo = ym//13, ym%13
            dy = (raw>>17)&0x1F
            hr = (raw>>12)&0x1F
            mn = (raw>>6)&0x3F
            sc = raw&0x3F
            try:
                return datetime.datetime(yr,mo,dy,hr,mn,sc), pos2
            except:
                return None, pos2
        if ctype in (TYPE_ENUM, TYPE_SET):
            nb = meta if meta else 1
            val = int.from_bytes(data[pos:pos+nb],'little')
            return val, pos+nb
        # 未知类型，尝试跳过0字节，返回None
        return None, pos
    except Exception as e:
        return f'ERR({e})', pos+1

def parse_rows(body, etype, col_types, metas):
    """解析事件 body，返回行列表（取 after-image）"""
    rows = []
    pos = 8  # skip table_id(6)+reserved(2)
    if etype in (WRITE_ROWS_V2, UPDATE_ROWS_V2, DELETE_ROWS_V2):
        extra = struct.unpack_from('<H', body, pos)[0]; pos += extra
    col_count, pos = read_lenenc(body, pos)
    bm_len = (col_count+7)//8
    pos += bm_len  # columns_present bitmap
    if etype in ROW_UPDATE:
        pos += bm_len  # after-image bitmap

    while pos < len(body):
        null_bm = body[pos:pos+bm_len]; pos += bm_len
        if etype in ROW_UPDATE:
            # skip before-image
            vals_before = {}
            for ci, ct in enumerate(col_types):
                nb_byte = ci//8; nb_bit = ci%8
                if nb_byte < len(null_bm) and (null_bm[nb_byte]>>nb_bit)&1:
                    vals_before[ci] = None; continue
                v, pos = read_col(body, pos, ct, metas.get(ci,0))
                vals_before[ci] = v
            null_bm2 = body[pos:pos+bm_len]; pos += bm_len
            null_bm = null_bm2

        vals = {}
        for ci, ct in enumerate(col_types):
            nb_byte = ci//8; nb_bit = ci%8
            if nb_byte < len(null_bm) and (null_bm[nb_byte]>>nb_bit)&1:
                vals[ci] = None; continue
            v, pos = read_col(body, pos, ct, metas.get(ci,0))
            if isinstance(v, str) and v.startswith('ERR'):
                break
            vals[ci] = v
        if vals:
            rows.append(vals)
        else:
            break
    return rows


def scan_binlog(files, target_tables):
    """扫描 binlog，返回 {table_name: [(op, dt, vals), ...]}"""
    table_map = {}
    result = {t: [] for t in target_tables}

    for fpath in files:
        with open(fpath, 'rb') as f:
            if f.read(4) != MAGIC:
                print(f"  ⚠️ {fpath} 非有效 binlog"); continue
            while True:
                hdr = f.read(19)
                if len(hdr) < 19: break
                ts, etype, sid, elen, lpos, flags = struct.unpack('<IBIIIH', hdr)
                body = f.read(elen-19)
                if len(body) < elen-19: break
                dt = datetime.datetime.fromtimestamp(ts) if ts else None

                if etype == TABLE_MAP_EVENT:
                    try:
                        tid, db, tbl, ctypes, cmetas = parse_table_map(body)
                        table_map[tid] = (tbl, ctypes, cmetas)
                    except: pass

                elif etype in ROW_EVENTS:
                    tid = int.from_bytes(body[0:6], 'little')
                    info = table_map.get(tid)
                    if not info: continue
                    tbl, ctypes, cmetas = info
                    if tbl not in target_tables: continue
                    op = 'INSERT' if etype in ROW_WRITE else ('UPDATE' if etype in ROW_UPDATE else 'DELETE')
                    try:
                        rows = parse_rows(body, etype, ctypes, cmetas)
                        for row in rows:
                            result[tbl].append((op, dt, row))
                    except: pass
    return result


BINLOG_FILES = ['binlog.000003', 'binlog.000004']

print("=== 步骤1：从 review_tasks 找李雅岑(703)的 task_id ===\n")
data = scan_binlog(BINLOG_FILES, {'review_tasks', 'review_scores'})

# review_tasks 列: 0=id, 1=stage(enum/str), 2=registration_id, 3=reviewer_id, 4=status, ...
task_events = data['review_tasks']
print(f"review_tasks 事件总数: {len(task_events)}")

liyacen_tasks = {}  # task_id -> {registration_id, last_op, dt}
for op, dt, vals in task_events:
    tid_val = vals.get(0)
    reviewer = vals.get(3)
    reg_id   = vals.get(2)
    if reviewer == TARGET_REVIEWER_ID and tid_val:
        liyacen_tasks[tid_val] = {'op': op, 'dt': dt, 'registration_id': reg_id, 'vals': vals}

print(f"\n李雅岑 task_id 共 {len(liyacen_tasks)} 个: {sorted(liyacen_tasks.keys())}\n")
for tid, info in sorted(liyacen_tasks.items()):
    print(f"  task_id={tid}  reg_id={info['registration_id']}  最后op={info['op']}  时间={info['dt']}")

print("\n\n=== 步骤2：从 review_scores 还原各 task 的打分 ===\n")

# review_scores 列: 0=id, 1=review_task_id, 2=plan, 3=problem, 4=action,
#                   5=success, 6=review, 7=operation, 8=presentation, 9=total,
#                   10=highlight, 11=weakness, 12=submitted_at
score_events = data['review_scores']
print(f"review_scores 事件总数: {len(score_events)}")

from collections import defaultdict
scores_by_task = defaultdict(list)
for op, dt, vals in score_events:
    task_id_val = vals.get(1)
    if task_id_val in liyacen_tasks:
        scores_by_task[task_id_val].append((op, dt, vals))

print(f"\n涉及李雅岑的 review_scores 事件: {sum(len(v) for v in scores_by_task.values())} 条\n")

for tid in sorted(scores_by_task.keys()):
    evts = scores_by_task[tid]
    # 取最后一次 INSERT 或 UPDATE（最终打分状态）
    last = evts[-1]
    op, dt, vals = last
    reg_id = liyacen_tasks[tid]['registration_id']
    print(f"─── task_id={tid}  reg_id={reg_id}  操作数={len(evts)} ───")
    print(f"  最后操作: {op} @ {dt}")
    cols = ['plan','problem','action','success','review','operation','presentation','total']
    for i, c in enumerate(cols):
        v = vals.get(i+2)
        if v is not None and not str(v).startswith('ERR'):
            print(f"  {c}: {round(v,2) if isinstance(v,float) else v}")
    hl = vals.get(10)
    wk = vals.get(11)
    sb = vals.get(12)
    print(f"  highlight:  {hl}")
    print(f"  weakness:   {wk}")
    print(f"  submitted:  {sb}")
    print()
