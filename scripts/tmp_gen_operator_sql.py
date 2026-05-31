import bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 生成 opt123 的 $2a$ 哈希
raw = bcrypt.hashpw(b'opt123', bcrypt.gensalt(rounds=10)).decode()
hashed = raw.replace('$2b$', '$2a$', 1)

# 短名 -> 真实 session_code（来自排程 Excel 的 sheet 名去掉日期前缀）
SESSION_MAP = {
    '综合组问题解决型1': '综合组-问题解决型专场1（三楼开元A厅）',
    '综合组问题解决型2': '综合组-问题解决型专场2（三楼开元A厅）',
    '综合组问题解决型3': '综合组-问题解决型专场3（三楼锦兰厅）',
    '综合组问题解决型4': '综合组-问题解决型专场4(三楼开元A厅)',
    '综合组课达QFD1':   '综合组-课题达成及QFD专场2改1（三楼开元B厅）',
    '综合组课达QFD2':   '综合组-课题达成及QFD专场2（三楼开元B厅）',
    '综合组课达QFD3':   '综合组-课题达成及QFD专场3（三楼开元B厅）',
    '进阶组1':          '进阶组1组（三楼萧然厅）',
    '进阶组2':          '进阶组 2组（三楼萧然厅）',
    '进阶组3':          '进阶组3组（三楼萧然厅）',
    '基层组1':          '基层组1组（一楼活动中心）',
    '基层组2':          '基层组2组（锦绣厅）',
    '基层组3':          '基层组3组（一楼活动中心）',
    '基层组4':          '基层组4组（一楼活动中心）',
    '综合组十大安全目标1': '综合组-十大安全目标专场1（三楼锦绣厅）',
    '综合组十大安全目标2': '综合组-十大安全目标专场2（三楼锦绣厅）',
    '综合组综合工具1':  '综合组-综合工具专场1（三楼锦兰厅）',
    '综合组综合工具2':  '综合组-综合工具专场2（三楼锦兰厅）',
    '综合组PDCA1':      '综合组-PDCA专场1（二楼名仕厅）',
    '综合组PDCA2':      '综合组-PDCA专场2（二楼名仕厅）',
    '综合组PDCA3':      '综合组-PDCA专场3（二楼名仕厅）',
}

staff = [
    ('沈佩儿', '13588040680', ['综合组问题解决型1', '综合组问题解决型2', '综合组问题解决型4']),
    ('钱丽华', '15825502873', ['综合组课达QFD1',   '综合组课达QFD2',   '综合组课达QFD3']),
    ('周桉',   '18057127990', ['进阶组1',           '进阶组2',           '进阶组3']),
    ('华佳宁', '18868634981', ['基层组2',           '综合组十大安全目标1', '综合组十大安全目标2']),
    ('汪洋',   '15996257167', ['综合组综合工具1',   '综合组综合工具2',   '综合组问题解决型3']),
    ('江玲',   '18858161236', ['综合组PDCA1',       '综合组PDCA2',       '综合组PDCA3']),
    ('田阳帆', '18258881995', ['基层组1',           '基层组3',           '基层组4']),
]

now = '2026-05-30 00:00:00'
lines = []
lines.append("-- ============================================================")
lines.append("-- OPERATOR 账号创建 + 会场分配（密码 opt123）")
lines.append("-- 生成时间: 2026-05-30")
lines.append("-- ============================================================")
lines.append(f"-- 密码哈希: {hashed}")
lines.append("")
lines.append("-- 1. 创建工作人员账号（OPERATOR 角色）")
for name, phone, sessions in staff:
    sess_labels = ' / '.join(SESSION_MAP.get(s, s) for s in sessions)
    lines.append(f"-- {name} {phone} 负责: {sess_labels}")
    lines.append(f"INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)")
    lines.append(f"  VALUES ('{name}', '{phone}', '{hashed}', 'OPERATOR', 1, '{now}');")
lines.append("")
lines.append("-- 2. 分配会场（用子查询根据手机号获取 id）")
for name, phone, sessions in staff:
    for sess_short in sessions:
        sess_full = SESSION_MAP.get(sess_short, sess_short)
        safe = sess_full.replace("'", "''")
        lines.append(f"INSERT INTO staff_session_assignments (staff_id, session_code)")
        lines.append(f"  SELECT id, '{safe}' FROM user_accounts WHERE phone='{phone}' LIMIT 1;")
lines.append("")
lines.append("-- 3. 验证结果")
lines.append("SELECT ua.name, ua.phone, ssa.session_code")
lines.append("FROM staff_session_assignments ssa")
lines.append("JOIN user_accounts ua ON ua.id = ssa.staff_id")
lines.append("ORDER BY ua.name, ssa.session_code;")

sql = '\n'.join(lines)
out = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\scripts\create_operators_0530.sql'
with open(out, 'w', encoding='utf-8') as f:
    f.write(sql)
print(sql)
print(f"\n-- 已保存到: {out}")
