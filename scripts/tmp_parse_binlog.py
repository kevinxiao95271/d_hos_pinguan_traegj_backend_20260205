"""
解析 binlog.000005，提取今早 review_scores 表的 INSERT/UPDATE 记录
"""
import io, sys, re, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BINLOG = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\binlog.000005'

# 用 python-mysql-replication 解析（如果有）；否则用二进制暴力扫文本特征
try:
    from mysql_replication import BinLogStreamReader
    from mysql_replication.row_event import WriteRowsEvent, UpdateRowsEvent
    HAS_LIB = True
except ImportError:
    HAS_LIB = False

if HAS_LIB:
    print('用 mysql-replication 库解析...')
    stream = BinLogStreamReader(
        connection_settings={},
        log_file=BINLOG,
        only_tables=['review_scores'],
        resume_stream=True,
        blocking=False,
    )
    for event in stream:
        if isinstance(event, (WriteRowsEvent, UpdateRowsEvent)):
            ts = datetime.datetime.fromtimestamp(event.timestamp)
            if ts.date() == datetime.date(2026, 6, 3):
                for row in event.rows:
                    vals = row.get('values') or row.get('after_values') or {}
                    total = vals.get('total')
                    task_id = vals.get('review_task_id')
                    print(f'{ts}  task_id={task_id}  total={total}  plan={vals.get("plan")}  problem={vals.get("problem")}')
    stream.close()
else:
    print('未安装 mysql-replication，改用二进制文本扫描...')
    # binlog 是二进制，但字符串字段会明文出现
    # 扫描含 review_scores 附近的可见文本
    with open(BINLOG, 'rb') as f:
        data = f.read()

    # 找所有可读ASCII片段
    text = data.decode('latin-1')  # 保留所有字节为latin-1

    # 找时间戳特征：2026-06-03 今早
    # binlog里时间戳是Unix时间戳4字节，今早范围：
    # 2026-06-03 00:00:00 UTC+8 = 2026-06-02 16:00:00 UTC = 1748872800
    # 2026-06-03 12:00:00 UTC+8 = 2026-06-03 04:00:00 UTC = 1748916000
    import struct

    results = []
    i = 0
    while i < len(data) - 4:
        # 读4字节小端时间戳
        ts_raw = struct.unpack_from('<I', data, i)[0]
        if 1748872800 <= ts_raw <= 1748916000:
            # 这个位置附近可能是binlog事件头
            # 事件头: timestamp(4) + event_type(1) + server_id(4) + event_length(4) + next_pos(4) + flags(2) = 19字节
            event_type = data[i+4] if i+4 < len(data) else 0
            # event_type 30=WRITE_ROWS_EVENTv2, 31=UPDATE_ROWS_EVENTv2, 32=DELETE_ROWS_EVENTv2
            if event_type in (30, 31):
                ev_len = struct.unpack_from('<I', data, i+9)[0]
                if 20 < ev_len < 65536:
                    chunk = data[i:i+ev_len]
                    # 在chunk里找可见字符
                    visible = re.findall(b'[\x20-\x7e]{4,}', chunk)
                    readable = [v.decode('ascii','ignore') for v in visible]
                    ts_dt = datetime.datetime.fromtimestamp(ts_raw, tz=datetime.timezone(datetime.timedelta(hours=8)))
                    results.append((ts_dt, event_type, readable))
            i += 1
        else:
            i += 1

    # 输出含 score/total/review_scores 关键字的事件
    print(f'今早(UTC+8 00:00-12:00)的 WRITE/UPDATE 事件数: {len(results)}')
    for ts_dt, etype, readable in results:
        joined = ' '.join(readable)
        # 只打含评分相关内容的
        if any(k in joined.lower() for k in ['score', 'total', 'review', 'plan', 'problem']):
            ename = 'WRITE' if etype == 30 else 'UPDATE'
            print(f'\n[{ts_dt.strftime("%H:%M:%S")}] {ename}')
            for r in readable:
                if len(r) > 3:
                    print(f'  {r}')
