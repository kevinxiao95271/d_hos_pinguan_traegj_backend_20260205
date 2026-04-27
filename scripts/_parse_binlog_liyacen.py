"""
解析 binlog，找李雅岑(reviewer_id=703)相关的 review_scores DELETE 记录
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pymysql

# 先从数据库拿到李雅岑的所有 review_task_id
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("""
    SELECT rt.id, rt.status, rt.updated_at, reg.project_name
    FROM review_tasks rt
    JOIN registrations reg ON reg.id = rt.registration_id
    WHERE rt.reviewer_id = 703 AND rt.stage = 'BOOK'
    ORDER BY rt.id
""")
tasks = cur.fetchall()
conn.close()

task_ids = {t[0] for t in tasks}
print(f"李雅岑书审任务共 {len(tasks)} 条，task_id 列表: {sorted(task_ids)}")
print()
for t in tasks:
    print(f"  task_id={t[0]}  status={t[1]}  updated_at={t[2]}  项目={t[3][:30]}")

print("\n\n=== 开始解析 binlog，查找被删除的 review_scores ===\n")

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent

found = []
for binlog_file in ['binlog.000003', 'binlog.000004']:
    print(f"--- 扫描 {binlog_file} ---")
    try:
        stream = BinLogStreamReader(
            connection_settings={
                'host': '127.0.0.1', 'port': 3306,
                'user': 'fake', 'passwd': 'fake'
            },
            log_file=binlog_file,
            only_events=[DeleteRowsEvent],
            resume_stream=True,
            blocking=False,
            ignored_schemas=[],
        )
        for event in stream:
            if hasattr(event, 'table') and 'review_scores' in str(event.table).lower():
                for row in event.rows:
                    vals = row.get('values', row)
                    rtid = vals.get('review_task_id') or vals.get(2)
                    if rtid in task_ids:
                        print(f"  ✅ 找到! review_task_id={rtid}")
                        print(f"     {json.dumps(vals, default=str, ensure_ascii=False)}")
                        found.append(vals)
        stream.close()
    except Exception as e:
        print(f"  ⚠️  {e}")

print(f"\n共找到 {len(found)} 条被删除记录")
