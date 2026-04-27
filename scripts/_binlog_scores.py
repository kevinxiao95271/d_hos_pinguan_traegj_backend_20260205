"""
从 binlog 文件精确解析 review_scores 的 INSERT/UPDATE/DELETE 记录
输出：时间 | 操作 | review_task_id | 各分项 | 总分 | highlight | weakness
"""
import struct, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── 李雅岑 reviewer_id（从 binlog 里的 review_tasks 中找）──
TARGET_REVIEWER_ID = 703

# ── MySQL binlog 事件类型 ─────────────────────────────────
TABLE_MAP_EVENT = 19
WRITE_ROWS_V1, UPDATE_ROWS_V1, DELETE_ROWS_V1 = 23, 24, 25
WRITE_ROWS_V2, UPDATE_ROWS_V2, DELETE_ROWS_V2 = 30, 31, 32
ROW_WRITE  = {WRITE_ROWS_V1, WRITE_ROWS_V2}
ROW_UPDATE = {UPDATE_ROWS_V1, UPDATE_ROWS_V2}
ROW_DELETE = {DELETE_ROWS_V1, DELETE_ROWS_V2}
ROW_EVENTS = ROW_WRITE | ROW_UPDATE | ROW_DELETE

# MySQL 列类型
TYPE_LONGLONG = 8   # BIGINT
TYPE_DOUBLE   = 5
TYPE_VARCHAR  = 15
TYPE_VAR_STR  = 253
TYPE_DATETIME2= 18
TYPE_BLOB     = 252

MAGIC = b'\xfebin'

def read_lenenc_int(data, pos):
    if pos >= len(data):
        return 0, pos
    first = data[pos]
    if first < 0xfb:
        return first, pos + 1
    elif first == 0xfc:
        return struct.unpack_from('<H', data, pos+1)[0], pos + 3
    elif first == 0xfd:
        v = struct.unpack_from('<I', data[pos+1:pos+4] + b'\x00')[0]
        return v, pos + 4
    else:
        return struct.unpack_from('<Q', data, pos+1)[0], pos + 9

def parse_row(data, pos, col_types, col_metas, null_bitmap):
    """解析一行数据，返回 (values_dict, new_pos)"""
    values = {}
    col_idx = 0
    for i, ctype in enumerate(col_types):
        # null bitmap check
        byte_idx = col_idx // 8
        bit_idx  = col_idx % 8
        is_null  = (null_bitmap[byte_idx] >> bit_idx) & 1 if byte_idx < len(null_bitmap) else 0
        col_idx += 1

        if is_null:
            values[i] = None
            continue

        if pos >= len(data):
            values[i] = None
            continue

        try:
            if ctype == TYPE_LONGLONG:
                values[i] = struct.unpack_from('<q', data, pos)[0]; pos += 8
            elif ctype == TYPE_DOUBLE:
                values[i] = struct.unpack_from('<d', data, pos)[0]; pos += 8
            elif ctype in (TYPE_VARCHAR, TYPE_VAR_STR):
                meta = col_metas.get(i, 1)
                if meta > 255:
                    slen = struct.unpack_from('<H', data, pos)[0]; pos += 2
                else:
                    slen = data[pos]; pos += 1
                values[i] = data[pos:pos+slen].decode('utf-8', errors='replace'); pos += slen
            elif ctype == TYPE_BLOB:
                meta = col_metas.get(i, 2)
                slen = int.from_bytes(data[pos:pos+meta], 'little'); pos += meta
                values[i] = data[pos:pos+slen].decode('utf-8', errors='replace'); pos += slen
            elif ctype == TYPE_DATETIME2:
                # 5 bytes big-endian
                raw = int.from_bytes(data[pos:pos+5], 'big'); pos += 5
                # frac precision stored in meta
                frac_meta = col_metas.get(i, 0)
                frac_bytes = (frac_meta + 1) // 2
                pos += frac_bytes
                # decode datetime2
                yearmonth = (raw >> 22) & 0x7FFF
                year  = yearmonth // 13
                month = yearmonth % 13
                day   = (raw >> 17) & 0x1F
                hour  = (raw >> 12) & 0x1F
                minute= (raw >> 6)  & 0x3F
                second= raw & 0x3F
                try:
                    values[i] = datetime.datetime(year, month, day, hour, minute, second)
                except:
                    values[i] = f"DT({raw})"
            else:
                # 未知类型，跳过，标记
                values[i] = f'?type{ctype}'
                break
        except Exception as e:
            values[i] = f'ERR({e})'
            break

    return values, pos


def parse_table_map(body):
    """解析 TABLE_MAP_EVENT，返回 (table_id, db, table, col_types, col_metas)"""
    pos = 0
    table_id = struct.unpack_from('<Q', body[pos:pos+8])[0] & 0xFFFFFFFFFFFF
    pos = 8
    db_len = body[pos]; pos += 1
    db = body[pos:pos+db_len].decode('utf-8', errors='replace'); pos += db_len + 1
    tbl_len = body[pos]; pos += 1
    tbl = body[pos:pos+tbl_len].decode('utf-8', errors='replace'); pos += tbl_len + 1

    col_count, pos = read_lenenc_int(body, pos)
    col_types = list(body[pos:pos+col_count]); pos += col_count

    meta_len, pos = read_lenenc_int(body, pos)
    meta_data = body[pos:pos+meta_len]; pos += meta_len

    # 解析 metadata（每种类型有不同字节数）
    col_metas = {}
    mpos = 0
    for ci, ct in enumerate(col_types):
        if ct in (TYPE_VARCHAR, TYPE_VAR_STR):
            if mpos + 2 <= len(meta_data):
                col_metas[ci] = struct.unpack_from('<H', meta_data, mpos)[0]; mpos += 2
        elif ct == TYPE_DOUBLE:
            if mpos + 1 <= len(meta_data):
                col_metas[ci] = meta_data[mpos]; mpos += 1
        elif ct == TYPE_BLOB:
            if mpos + 1 <= len(meta_data):
                col_metas[ci] = meta_data[mpos]; mpos += 1
        elif ct == TYPE_DATETIME2:
            if mpos + 1 <= len(meta_data):
                col_metas[ci] = meta_data[mpos]; mpos += 1

    return table_id, db, tbl, col_types, col_metas


def parse_binlog(filepath):
    results = []
    table_map = {}   # table_id -> (db, tbl, col_types, col_metas)

    with open(filepath, 'rb') as f:
        if f.read(4) != MAGIC:
            print(f"  ⚠️ {filepath} 非有效 binlog"); return results

        while True:
            header = f.read(19)
            if len(header) < 19: break
            ts, etype, sid, elen, lpos, flags = struct.unpack('<IBIIIH', header)
            body = f.read(elen - 19)
            if len(body) < elen - 19: break
            dt = datetime.datetime.fromtimestamp(ts) if ts else None

            if etype == TABLE_MAP_EVENT:
                try:
                    tid, db, tbl, ctypes, cmetas = parse_table_map(body)
                    table_map[tid] = (db, tbl, ctypes, cmetas)
                except: pass

            elif etype in ROW_EVENTS:
                tid = struct.unpack_from('<Q', body[0:8])[0] & 0xFFFFFFFFFFFF
                info = table_map.get(tid)
                if not info or 'review_scores' not in info[1]:
                    continue

                db, tbl, col_types, col_metas = info
                op = 'INSERT' if etype in ROW_WRITE else ('UPDATE' if etype in ROW_UPDATE else 'DELETE')

                # 跳过 table_id(6) + reserved(2) + extra(v2)
                pos = 8
                if etype in (WRITE_ROWS_V2, UPDATE_ROWS_V2, DELETE_ROWS_V2):
                    extra_len = struct.unpack_from('<H', body, pos)[0]; pos += extra_len

                col_count, pos = read_lenenc_int(body, pos)
                bitmap_len = (col_count + 7) // 8
                pos += bitmap_len  # columns_present_bitmap
                if etype in ROW_UPDATE:
                    pos += bitmap_len  # after-image bitmap

                while pos < len(body):
                    null_bitmap = body[pos:pos+bitmap_len]; pos += bitmap_len
                    vals, pos = parse_row(body, pos, col_types, col_metas, null_bitmap)

                    if etype in ROW_UPDATE:
                        # UPDATE有前后两行，跳过前像的null bitmap已处理，再读after-image
                        null_bitmap2 = body[pos:pos+bitmap_len]; pos += bitmap_len
                        vals, pos = parse_row(body, pos, col_types, col_metas, null_bitmap2)

                    # review_scores 列: 0=id, 1=review_task_id, 2=plan ... 9=total, 10=highlight, 11=weakness, 12=submitted_at
                    task_id = vals.get(1)
                    if task_id is None:
                        break

                    if FILTER_TASK_IDS and task_id not in FILTER_TASK_IDS:
                        break

                    results.append({
                        'op': op, 'ts': dt,
                        'id': vals.get(0), 'task_id': task_id,
                        'plan': vals.get(2), 'problem': vals.get(3),
                        'action': vals.get(4), 'success': vals.get(5),
                        'review': vals.get(6), 'operation': vals.get(7),
                        'presentation': vals.get(8), 'total': vals.get(9),
                        'highlight': vals.get(10), 'weakness': vals.get(11),
                        'submitted_at': vals.get(12),
                    })
                    break  # 每个 event 只取第一行（单行操作）
    return results


# ── 主流程 ────────────────────────────────────────────────
print("=== 解析 review_scores binlog 记录 ===\n")

all_rows = []
for fname in ['binlog.000003', 'binlog.000004']:
    print(f"扫描 {fname} ...")
    rows = parse_binlog(fname)
    print(f"  找到 {len(rows)} 条 review_scores 操作\n")
    all_rows.extend(rows)

# 按 task_id + 时间排序，只显示最后一次（最终状态）
from collections import defaultdict
by_task = defaultdict(list)
for r in all_rows:
    by_task[r['task_id']].append(r)

print(f"共涉及 {len(by_task)} 个 review_task_id\n")
print(f"task_id 列表: {sorted(by_task.keys())}\n")

for tid in sorted(by_task.keys()):
    rows = by_task[tid]
    last = rows[-1]  # 最后一次操作
    print(f"─── task_id={tid}  操作数={len(rows)} ───")
    print(f"  最后操作: {last['op']} @ {last['ts']}")
    for k in ['plan','problem','action','success','review','operation','presentation','total']:
        v = last.get(k)
        if v is not None:
            print(f"  {k}: {round(v,2) if isinstance(v,float) else v}")
    print(f"  highlight:  {last.get('highlight')}")
    print(f"  weakness:   {last.get('weakness')}")
    print(f"  submitted:  {last.get('submitted_at')}")
    print()
