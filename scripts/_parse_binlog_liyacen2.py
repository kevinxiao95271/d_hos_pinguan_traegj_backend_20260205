"""
解析本地 binlog 文件，找 review_scores 表的所有 INSERT / UPDATE / DELETE 事件
列出其中涉及李雅岑(reviewer_id=703)任务的操作记录
"""
import struct, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── MySQL binlog 事件类型 ──────────────────────────
TABLE_MAP_EVENT     = 19
WRITE_ROWS_V1       = 23
UPDATE_ROWS_V1      = 24
DELETE_ROWS_V1      = 25
WRITE_ROWS_V2       = 30
UPDATE_ROWS_V2      = 31
DELETE_ROWS_V2      = 32
ROW_WRITE  = {WRITE_ROWS_V1, WRITE_ROWS_V2}
ROW_UPDATE = {UPDATE_ROWS_V1, UPDATE_ROWS_V2}
ROW_DELETE = {DELETE_ROWS_V1, DELETE_ROWS_V2}
ROW_EVENTS = ROW_WRITE | ROW_UPDATE | ROW_DELETE

MAGIC = b'\xfebin'

def read_lenenc_int(data, pos):
    first = data[pos]
    if first < 0xfb:
        return first, pos + 1
    elif first == 0xfc:
        return struct.unpack_from('<H', data, pos+1)[0], pos + 3
    elif first == 0xfd:
        return struct.unpack_from('<I', data[pos+1:pos+4] + b'\x00')[0], pos + 4
    else:
        return struct.unpack_from('<Q', data, pos+1)[0], pos + 9

def parse_binlog(filepath, target_table='review_scores'):
    """返回 [(op, timestamp, table_id, rows_bytes, pos)] 以及 table_map"""
    results = []
    table_map = {}  # table_id -> (db, table)

    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic != MAGIC:
            print(f"  ⚠️ {filepath} 不是有效 binlog 文件 (magic={magic.hex()})")
            return results, table_map

        while True:
            header = f.read(19)
            if len(header) < 19:
                break
            ts, etype, sid, elen, lpos, flags = struct.unpack('<IBIIIH', header)
            body_len = elen - 19
            body = f.read(body_len)
            if len(body) < body_len:
                break

            dt = datetime.datetime.fromtimestamp(ts) if ts else None

            if etype == TABLE_MAP_EVENT:
                pos = 0
                table_id = struct.unpack_from('<Q', body[pos:pos+8])[0] & 0xFFFFFFFFFFFF
                pos = 8  # 6 bytes table_id + 2 bytes reserved
                db_len = body[pos]; pos += 1
                db_name = body[pos:pos+db_len].decode('utf-8', errors='replace'); pos += db_len + 1
                tbl_len = body[pos]; pos += 1
                tbl_name = body[pos:pos+tbl_len].decode('utf-8', errors='replace'); pos += tbl_len + 1
                table_map[table_id] = (db_name, tbl_name)

            elif etype in ROW_EVENTS:
                pos = 0
                table_id = struct.unpack_from('<Q', body[pos:pos+8])[0] & 0xFFFFFFFFFFFF
                info = table_map.get(table_id, ('?', '?'))
                if target_table in info[1].lower():
                    op = 'INSERT' if etype in ROW_WRITE else ('UPDATE' if etype in ROW_UPDATE else 'DELETE')
                    results.append((op, dt, table_id, body, info))

    return results, table_map


def try_extract_strings(body, op):
    """暴力提取 body 中的可读字符串（用于找 highlight/weakness）"""
    strings = []
    i = 0
    while i < len(body):
        # 找长度前缀字符串（lenenc）
        if i + 1 < len(body):
            l = body[i]
            if 1 <= l <= 200 and i + 1 + l <= len(body):
                chunk = body[i+1:i+1+l]
                try:
                    s = chunk.decode('utf-8')
                    if all(32 <= ord(c) or c in '\n\r\t' for c in s) and len(s) > 2:
                        strings.append(s)
                        i += 1 + l
                        continue
                except:
                    pass
        i += 1
    return strings


def extract_int64(body, offset):
    try:
        return struct.unpack_from('<q', body, offset)[0]
    except:
        return None

def extract_double(body, offset):
    try:
        return struct.unpack_from('<d', body, offset)[0]
    except:
        return None


print("=" * 60)
print("解析 binlog，找 review_scores 的所有操作记录")
print("=" * 60)

all_events = []
for fname in ['binlog.000003', 'binlog.000004']:
    print(f"\n扫描 {fname} ...")
    evts, tmap = parse_binlog(fname, 'review_scores')
    print(f"  找到 review_scores 相关事件: {len(evts)} 条")
    all_events.extend(evts)

print(f"\n共 {len(all_events)} 条 review_scores 操作事件\n")

for i, (op, dt, tid, body, info) in enumerate(all_events):
    print(f"─── [{i+1}] {op} @ {dt}  table={info[1]} ───")

    # 暴力提取数字（8字节 double）和字符串
    # review_scores 列顺序: id, review_task_id, plan, problem, action, success,
    #                       review, operation, presentation, total, highlight, weakness, submitted_at

    # 跳过 TABLE_MAP 部分（6+2=8 bytes table_id + reserved + extra for v2）
    # ROW data 开始位置大约在 8~12 bytes 之后
    # 我们暴力搜索所有可读字符串

    strings = try_extract_strings(body, op)
    if strings:
        print(f"  文字内容: {strings}")

    # 尝试找 double 值（分数通常在 60-100 之间）
    scores = []
    for off in range(0, min(len(body)-8, 200), 1):
        v = extract_double(body, off)
        if v is not None and 0 < v < 200:
            scores.append(round(v, 2))
    # 去重，保留合理分数
    seen = set()
    uniq_scores = []
    for v in scores:
        if v not in seen:
            seen.add(v)
            uniq_scores.append(v)
    if uniq_scores:
        print(f"  数值(含分数候选): {uniq_scores[:20]}")

    print()
